from __future__ import annotations

import json
from typing import Any

from google import genai

from .core import Settings, best_value_offer, cheapest_offer


class GeminiAgent:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = genai.Client(api_key=settings.gemini_api_key)

    def recommend(
        self,
        product: str,
        country: str,
        budget: str | None,
        offers: list[dict[str, Any]],
    ) -> str:
        if not offers:
            return "No offers found, so I cannot recommend a deal yet."

        cheapest = cheapest_offer(offers)
        best_value = best_value_offer(offers)
        prompt = {
            "role": "You are PriceAI, a concise shopping deal analyst.",
            "task": "Return a short recommendation for the user.",
            "requirements": [
                "Prefer the offer that best matches the requested product, not just the cheapest listing.",
                "Say which offer is the best deal.",
                "Explain why this is the best deal.",
                "Warn if seller or rating looks weak.",
                "Warn if the cheapest result looks like an accessory, refurbished item, or wrong product.",
                "Say whether to buy now or wait.",
                "Keep it under 160 words.",
            ],
            "product": product,
            "country": country,
            "budget": budget,
            "top_offers": offers[:10],
            "cheapest_offer": cheapest,
            "best_value_offer": best_value,
        }
        try:
            response = self.client.models.generate_content(
                model=self.settings.gemini_model,
                contents=json.dumps(prompt, ensure_ascii=False),
            )
            text = getattr(response, "text", "") or ""
            return text.strip() or "Gemini returned an empty recommendation."
        except Exception as exc:
            return f"Gemini recommendation failed: {exc}"
