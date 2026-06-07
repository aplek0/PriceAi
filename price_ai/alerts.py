from __future__ import annotations

from typing import Any

from .core import Settings, cheapest_offer, search_products
from .memory import MongoMemory


def check_watchlist(settings: Settings, memory: MongoMemory) -> dict[str, Any]:
    watched = memory.get_watchlist()
    checked = 0
    alerts_created = 0
    errors: list[str] = []

    for item in watched:
        product = item.get("product", "")
        country = item.get("country", "")
        offers, error = search_products(product, country, settings.serpapi_key, limit=10)
        if error:
            errors.append(f"{product}: {error}")
            continue
        current = cheapest_offer(offers)
        if not current:
            errors.append(f"{product}: no current offers found")
            continue

        checked += 1
        memory.save_price_history(item["_id"], product, country, current)

        baseline_price = float(item.get("baseline_price") or current["price_value"])
        target_price = item.get("target_price")
        current_price = float(current["price_value"])

        if current_price < baseline_price:
            memory.create_alert(
                item["_id"],
                product,
                baseline_price,
                current_price,
                current,
                "Current cheapest price is below the baseline price.",
            )
            alerts_created += 1

        if target_price is not None and current_price <= float(target_price):
            memory.create_alert(
                item["_id"],
                product,
                baseline_price,
                current_price,
                current,
                "Current cheapest price reached the target price.",
            )
            alerts_created += 1

    return {
        "watched": len(watched),
        "checked": checked,
        "alerts_created": alerts_created,
        "errors": errors,
    }
