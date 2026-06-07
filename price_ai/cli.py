from __future__ import annotations

from .agent import GeminiAgent
from .core import format_offer, load_settings, search_products
from .memory import MongoMemory


def main() -> None:
    settings = load_settings()
    missing = settings.missing_required
    if missing:
        print("Missing required environment variables: " + ", ".join(missing))
        print("Create or update the project .env file.")
        return

    memory = MongoMemory(settings)
    try:
        memory.ping()
    except Exception as exc:
        print(f"MongoDB is not connected: {exc}")
        return

    product = input("Product: ").strip()
    country = input("Country: ").strip() or "us"
    offers, error = search_products(product, country, settings.serpapi_key, limit=10)
    if error:
        print(error)
        return

    print("\nTop 10 best matching offers:")
    for index, offer in enumerate(offers, start=1):
        print(format_offer(offer, index))

    recommendation = GeminiAgent(settings).recommend(product, country, None, offers)
    memory.save_search(product, country, None, offers, recommendation)
    print("\nGemini recommendation:")
    print(recommendation)


if __name__ == "__main__":
    main()
