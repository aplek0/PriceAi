from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo import MongoClient, DESCENDING
from pymongo.database import Database

from .core import Settings


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MongoMemory:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client: MongoClient | None = None
        self.db: Database | None = None
        if settings.mongodb_uri:
            self.client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[settings.mongodb_db]

    def ping(self) -> bool:
        if self.client is None:
            return False
        self.client.admin.command("ping")
        return True

    def is_ready(self) -> bool:
        try:
            return self.ping()
        except Exception:
            return False

    def save_search(
        self,
        product: str,
        country: str,
        budget: str | None,
        offers: list[dict[str, Any]],
        recommendation: str,
    ) -> None:
        self._collection("search_history").insert_one(
            {
                "product": product,
                "country": country,
                "budget": budget,
                "offers": offers,
                "recommendation": recommendation,
                "created_at": utc_now(),
            }
        )

    def save_watch(
        self,
        product: str,
        country: str,
        target_price: float | None,
        baseline_offer: dict[str, Any],
    ) -> str:
        result = self._collection("watchlist").insert_one(
            {
                "product": product,
                "country": country,
                "target_price": target_price,
                "baseline_price": baseline_offer["price_value"],
                "baseline_offer": baseline_offer,
                "active": True,
                "created_at": utc_now(),
                "last_checked_at": None,
            }
        )
        return str(result.inserted_id)

    def get_watchlist(self) -> list[dict[str, Any]]:
        return list(self._collection("watchlist").find({"active": True}).sort("created_at", DESCENDING))

    def save_price_history(
        self,
        watch_id: Any,
        product: str,
        country: str,
        offer: dict[str, Any],
    ) -> None:
        self._collection("price_history").insert_one(
            {
                "watch_id": watch_id,
                "product": product,
                "country": country,
                "offer": offer,
                "price": offer["price_value"],
                "seller": offer.get("seller"),
                "checked_at": utc_now(),
            }
        )
        self._collection("watchlist").update_one(
            {"_id": watch_id},
            {"$set": {"last_checked_at": utc_now(), "last_offer": offer}},
        )

    def create_alert(
        self,
        watch_id: Any,
        product: str,
        old_price: float,
        new_price: float,
        offer: dict[str, Any],
        reason: str,
    ) -> None:
        self._collection("alerts").insert_one(
            {
                "watch_id": watch_id,
                "product": product,
                "old_price": old_price,
                "new_price": new_price,
                "drop_amount": round(old_price - new_price, 2),
                "seller": offer.get("seller"),
                "offer": offer,
                "reason": reason,
                "created_at": utc_now(),
            }
        )

    def alerts(self, limit: int = 100) -> list[dict[str, Any]]:
        return list(
            self._collection("alerts")
            .find()
            .sort("created_at", DESCENDING)
            .limit(limit)
        )

    def stats(self) -> dict[str, Any]:
        search_history = self._collection("search_history")
        watchlist = self._collection("watchlist")
        alerts = self._collection("alerts")

        most_searched = list(
            search_history.aggregate(
                [
                    {"$group": {"_id": "$product", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 5},
                ]
            )
        )
        biggest_drop = alerts.find_one(sort=[("drop_amount", DESCENDING)])

        return {
            "total_searches": search_history.count_documents({}),
            "watched_products": watchlist.count_documents({"active": True}),
            "alerts_count": alerts.count_documents({}),
            "most_searched": most_searched,
            "biggest_drop": biggest_drop,
        }

    def _collection(self, name: str):
        if self.db is None:
            raise RuntimeError("MongoDB is not configured.")
        return self.db[name]
