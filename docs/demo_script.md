# Demo Script

## 1. Environment Setup

Open `.env`.

Show:

- MONGODB_URI
- GEMINI_API_KEY
- SERPAPI_KEY
Explain that MongoDB, Gemini, and SerpApi are required.

## 2. Search

Open `/`.

Search:

```text
product: iphone 15
country: ro
budget: 3000
```

Show:

- Top 10 cheapest Google Shopping offers
- Parsed numeric prices
- Seller and rating where available
- Gemini recommendation

## 3. Watch

Open `/watch`.

Enter:

```text
product: iphone 15
country: ro
target price: 3000
```

Explain that PriceAI saves the current cheapest offer as `baseline_price` and stores `baseline_offer` in MongoDB.

## 4. Check Watchlist

Click Check All Watched Products or open `/check-watch`.

Explain:

- Every check searches current prices again with SerpApi.
- Every check saves to `price_history`.
- A price drop creates an alert in MongoDB.
- Target price hits also create alerts.

## 5. Alerts

Open `/alerts`.

Show:

- Product
- Old price
- New price
- Drop amount
- Seller
- Date
- Reason

## 6. Dashboard

Open `/dashboard`.

Show:

- Total searches
- Watched products
- Alerts count
- Most searched products
- Biggest price drop

## 7. Pitch Close

PriceAI is a MongoDB-powered Gemini shopping agent that uses SerpApi to search real product prices, remembers watched products, tracks price history, and alerts users when prices drop.
