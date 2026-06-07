# PriceAI

PriceAI is a MongoDB-powered Gemini shopping agent that uses SerpApi to search real product prices, remembers watched products, tracks price history, and alerts users when prices drop.

## Stack

- Python 3.10+
- Flask
- MongoDB
- Gemini via `google-genai`
- SerpApi Google Shopping
- HTML/CSS, no React

## Required Services

MongoDB, Gemini, and SerpApi are required.

If `MONGODB_URI`, `GEMINI_API_KEY`, or `SERPAPI_KEY` is missing, the web app shows a setup error page and blocks normal app flow until configured.

## Setup

```powershell
cd D:\Cyber\Proiecte\Hackthaloton\Price
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` before starting the app.

```env
MONGODB_URI=
MONGODB_DB=price_ai
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
SERPAPI_KEY=
```

## MongoDB Atlas Setup

1. Create a MongoDB Atlas account.
2. Create a free cluster.
3. Create a database user with read/write permissions.
4. Add your IP address to Network Access.
5. Copy the connection string.
6. Put it in `.env` as `MONGODB_URI`.
7. Keep `MONGODB_DB=price_ai` unless you want a different database name.

Collections used:

```text
search_history
watchlist
alerts
price_history
```

## Gemini Setup

1. Create a Gemini API key in Google AI Studio.
2. Put it in `.env` as `GEMINI_API_KEY`.
3. The default model is:

```env
GEMINI_MODEL=gemini-2.5-flash
```

Gemini is required for deal recommendations.

## SerpApi Setup

1. Create a SerpApi account.
2. Copy your API key.
3. Put it in `.env` as `SERPAPI_KEY`.

PriceAI uses SerpApi Google Shopping and extracts title, price, seller, rating, reviews, thumbnail, and link from shopping results. Offers are ranked by product match, seller/rating quality, reviews, and price so cheap accessories or wrong products are less likely to appear first.

## Run Web App

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

Core pages:

```text
/
/watch
/check-watch
/alerts
/dashboard
```

## Run CLI

```powershell
python -m price_ai.cli
```

The CLI asks for product and country, prints the top 10 cheapest offers, then prints the Gemini recommendation.

## Demo Flow

1. Show `.env` with MongoDB, Gemini, and SerpApi configured.
2. Search `iphone 15` in country `ro`.
3. Show top 10 best matching offers ranked by relevance and deal quality.
4. Show the Gemini recommendation and buy/wait advice.
5. Open `/watch` and watch `iphone 15` with an optional target price.
6. Click Check All Watched Products.
7. Open `/alerts` to show price-drop history if an alert was created.
8. Open `/dashboard` to show MongoDB stats.

## Hackathon Pitch

PriceAI is a MongoDB-powered Gemini shopping agent that uses SerpApi to search real product prices, remembers watched products, tracks price history, and alerts users when prices drop.

The product solves a common buyer problem: prices move constantly across sellers, and people do not want to manually check every product. PriceAI turns shopping into an agent workflow: search, recommend, remember, track, and alert.

MongoDB stores search memory, watched products, price history, and alert history. Gemini explains which deal is best and whether the buyer should purchase now or wait. SerpApi provides live Google Shopping data.

## Notes

- No auth is included for the MVP.
- No React or frontend build step is required.
- Startup validation blocks normal pages until required services are configured.
