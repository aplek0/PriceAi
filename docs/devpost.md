# PriceAI Devpost Draft

## Inspiration

Online prices change constantly, and shoppers waste time checking the same product across sellers. We wanted a lightweight AI agent that searches real offers, remembers what users care about, and tells them when a deal improves.

## What It Does

PriceAI lets users search real product prices with SerpApi Google Shopping, receive Gemini recommendations, save products to a MongoDB watchlist, track price history, and create alerts when prices drop.

## How We Built It

- Flask powers the web app.
- SerpApi retrieves real Google Shopping offers.
- Gemini generates concise deal recommendations.
- MongoDB stores search history, watchlist items, alerts, and price history.

## MongoDB Usage

MongoDB is the memory layer for the agent. It stores:

- `search_history`
- `watchlist`
- `alerts`
- `price_history`

The dashboard reads directly from MongoDB to show searches, watched products, alert counts, most searched products, and biggest price drop.

## AI Usage

Gemini receives the product, country, budget, top offers, cheapest offer, and best value offer. It returns a short recommendation, explains why the deal is strong, warns about weak seller/rating signals, and says whether to buy now or wait.

## Challenges

The main challenge is normalizing messy shopping prices from multiple countries and sellers. PriceAI parses formatted prices into numeric values so offers can be sorted and compared reliably.

## Accomplishments

We built a clean MVP with required service validation, real shopping data, AI recommendations, persistent memory, price alerts, dashboard stats, and CLI support.

## What's Next

- Scheduled background watch checks
- Better seller trust scoring
- Email notifications
- Multi-currency normalization
- User accounts after the hackathon MVP

## Pitch

PriceAI is a MongoDB-powered Gemini shopping agent that uses SerpApi to search real product prices, remembers watched products, tracks price history, and alerts users when prices drop.
