from __future__ import annotations

import os
import re
from math import log10
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
SERPAPI_URL = "https://serpapi.com/search.json"
STOP_WORDS = {
    "a",
    "an",
    "and",
    "for",
    "in",
    "of",
    "on",
    "the",
    "to",
    "with",
}
ACCESSORY_TERMS = {
    "adapter",
    "band",
    "cable",
    "case",
    "charger",
    "cover",
    "holder",
    "lens",
    "mount",
    "parts",
    "protector",
    "replacement",
    "sleeve",
    "stand",
    "strap",
    "sticker",
}
CONDITION_TERMS = {"open", "box", "preowned", "refurbished", "renewed", "used"}


@dataclass
class Settings:
    mongodb_uri: str
    mongodb_db: str
    gemini_api_key: str
    gemini_model: str
    serpapi_key: str

    @property
    def missing_required(self) -> list[str]:
        missing = []
        if not self.mongodb_uri:
            missing.append("MONGODB_URI")
        if not self.gemini_api_key:
            missing.append("GEMINI_API_KEY")
        if not self.serpapi_key:
            missing.append("SERPAPI_KEY")
        return missing


def load_settings() -> Settings:
    load_dotenv(ENV_PATH, override=True)
    return Settings(
        mongodb_uri=os.getenv("MONGODB_URI", "").strip(),
        mongodb_db=os.getenv("MONGODB_DB", "price_ai").strip() or "price_ai",
        gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        or "gemini-2.5-flash",
        serpapi_key=os.getenv("SERPAPI_KEY", "").strip(),
    )


def parse_price(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value)
    text = text.replace("\xa0", " ")
    match = re.search(r"(\d[\d\s.,]*)", text)
    if not match:
        return None
    number = match.group(1).strip().replace(" ", "")
    if "," in number and "." in number:
        if number.rfind(",") > number.rfind("."):
            number = number.replace(".", "").replace(",", ".")
        else:
            number = number.replace(",", "")
    elif "," in number:
        parts = number.split(",")
        if len(parts[-1]) == 2:
            number = number.replace(",", ".")
        else:
            number = number.replace(",", "")
    else:
        parts = number.split(".")
        if len(parts) > 2 or (len(parts) == 2 and len(parts[-1]) == 3):
            number = number.replace(".", "")
    try:
        return float(number)
    except ValueError:
        return None


def parse_count(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value).lower().replace(",", "").replace("+", "")
    match = re.search(r"(\d+(?:\.\d+)?)\s*([km])?", text)
    if not match:
        return None
    number = float(match.group(1))
    suffix = match.group(2)
    if suffix == "k":
        number *= 1_000
    elif suffix == "m":
        number *= 1_000_000
    return int(number)


def tokenize(value: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", value.lower())
    return [token for token in tokens if token not in STOP_WORDS]


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_offer(item: dict[str, Any]) -> dict[str, Any] | None:
    price = item.get("price") or item.get("extracted_price")
    price_value = item.get("extracted_price")
    if price_value is None:
        price_value = parse_price(price)
    try:
        price_value = float(price_value)
    except (TypeError, ValueError):
        return None

    title = item.get("title") or item.get("name") or "Unknown product"
    seller = item.get("source") or item.get("seller") or item.get("merchant") or "Unknown seller"
    rating = item.get("rating")
    reviews = item.get("reviews") or item.get("reviews_count") or item.get("extracted_reviews")
    link = item.get("link") or item.get("product_link") or item.get("serpapi_product_api") or ""
    thumbnail = item.get("thumbnail") or item.get("image") or ""

    return {
        "title": str(title),
        "price": str(price or price_value),
        "price_value": price_value,
        "seller": str(seller),
        "rating": rating,
        "reviews": parse_count(reviews),
        "link": str(link),
        "thumbnail": str(thumbnail),
    }


def offer_score(product: str, offer: dict[str, Any], median_price: float | None = None) -> float:
    query_tokens = set(tokenize(product))
    title = str(offer.get("title") or "")
    title_tokens = set(tokenize(title))
    title_text = " ".join(tokenize(title))
    query_text = " ".join(tokenize(product))

    if query_tokens:
        coverage = len(query_tokens & title_tokens) / len(query_tokens)
    else:
        coverage = 0.0
    phrase_bonus = 1.0 if query_text and query_text in title_text else 0.0

    accessory_penalty = 0.0
    if ACCESSORY_TERMS & title_tokens and not (ACCESSORY_TERMS & query_tokens):
        accessory_penalty = 1.0

    condition_penalty = 0.0
    if CONDITION_TERMS & title_tokens and not (CONDITION_TERMS & query_tokens):
        condition_penalty = 0.2

    rating_value = safe_float(offer.get("rating"), 3.5)
    rating_score = max(0.0, min(rating_value, 5.0)) / 5.0

    reviews = offer.get("reviews")
    review_score = min(log10(float(reviews) + 1) / 4, 1.0) if reviews else 0.0

    price = float(offer.get("price_value") or 0)
    if median_price and price > 0:
        price_score = max(0.0, min(median_price / price, 1.6)) / 1.6
    else:
        price_score = 0.5

    return (
        coverage * 70
        + phrase_bonus * 15
        + rating_score * 8
        + review_score * 5
        + price_score * 12
        - accessory_penalty * 85
        - condition_penalty * 15
    )


def rank_offers(product: str, offers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not offers:
        return []

    prices = sorted(float(offer["price_value"]) for offer in offers if offer.get("price_value"))
    median_price = prices[len(prices) // 2] if prices else None
    ranked = []
    for offer in offers:
        scored = dict(offer)
        scored["score"] = round(offer_score(product, scored, median_price), 2)
        ranked.append(scored)

    ranked.sort(
        key=lambda offer: (
            safe_float(offer.get("score")),
            safe_float(offer.get("rating")),
            -safe_float(offer.get("price_value")),
        ),
        reverse=True,
    )

    relevant = [offer for offer in ranked if safe_float(offer.get("score")) >= 45]
    return relevant or ranked


def search_products(
    product: str,
    country: str,
    serpapi_key: str,
    limit: int = 10,
) -> tuple[list[dict[str, Any]], str | None]:
    product = product.strip()
    country = country.strip().lower()
    if not product:
        return [], "Product is required."
    if not serpapi_key:
        return [], "SERPAPI_KEY is missing."

    params = {
        "engine": "google_shopping",
        "q": product,
        "api_key": serpapi_key,
        "gl": country or "us",
        "hl": "en",
    }
    try:
        response = requests.get(SERPAPI_URL, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        return [], f"SerpApi request failed: {exc}"

    raw_results = data.get("shopping_results") or []
    offers = []
    for item in raw_results:
        if not isinstance(item, dict):
            continue
        offer = normalize_offer(item)
        if offer:
            offers.append(offer)
    return rank_offers(product, offers)[:limit], None


def cheapest_offer(offers: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not offers:
        return None
    return min(offers, key=lambda offer: offer["price_value"])


def best_value_offer(offers: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not offers:
        return None

    def score(offer: dict[str, Any]) -> float:
        ranked_score = offer.get("score")
        if ranked_score is not None:
            try:
                return float(ranked_score)
            except (TypeError, ValueError):
                pass
        price = float(offer.get("price_value") or 0)
        rating = offer.get("rating")
        try:
            rating_value = float(rating)
        except (TypeError, ValueError):
            rating_value = 3.0
        return rating_value / max(price, 1)

    return max(offers, key=score)


def format_offer(offer: dict[str, Any], index: int | None = None) -> str:
    prefix = f"{index}. " if index is not None else ""
    rating = offer.get("rating")
    rating_text = f", rating {rating}" if rating else ""
    return (
        f"{prefix}{offer.get('title')} - {offer.get('price')} "
        f"({offer.get('price_value')}) from {offer.get('seller')}{rating_text}"
    )
