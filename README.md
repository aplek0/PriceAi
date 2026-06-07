# PriceAI

**PriceAI** is a Flask-based AI shopping agent that helps users find better product prices, compare offers, track watched products, and receive price-drop alerts.

It uses **MongoDB** for memory and price history, **Gemini** for deal recommendations, and **SerpApi Google Shopping** for real product search results.

---

## Features

* Search real product prices from Google Shopping
* Rank offers by relevance, price, seller quality, rating, and reviews
* Generate AI buying advice using Gemini
* Save watched products
* Track price history over time
* Detect price drops
* Store search history, alerts, and product data in MongoDB
* Web interface built with Flask and plain HTML/CSS
* CLI mode for terminal usage
* Setup validation page when required services are missing

---

## Tech Stack

* **Python 3.10+**
* **Flask**
* **MongoDB / MongoDB Atlas**
* **Gemini API** via `google-genai`
* **SerpApi Google Shopping API**
* **HTML/CSS**
* No React
* No frontend build step

---

## Required Services

PriceAI requires these services:

| Service | Purpose                                               |
| ------- | ----------------------------------------------------- |
| MongoDB | Stores searches, watchlist, price history, and alerts |
| Gemini  | Generates deal recommendations and buy/wait advice    |
| SerpApi | Fetches live Google Shopping product data             |

If any of these variables are missing, the app will show a setup error page and block normal usage:

```env
MONGODB_URI=
GEMINI_API_KEY=
SERPAPI_KEY=
```

---

## Project Structure

```text
PriceAI/
├── app.py
├── requirements.txt
├── .env.example
├── price_ai/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── db.py
│   ├── gemini.py
│   ├── serpapi_client.py
│   ├── ranking.py
│   └── watchlist.py
├── templates/
│   ├── index.html
│   ├── watch.html
│   ├── alerts.html
│   ├── dashboard.html
│   └── setup_error.html
└── static/
    └── style.css
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/aplek0/PriceAi.git
cd PriceAi
```

---

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Create your environment file

```bash
copy .env.example .env
```

On macOS/Linux:

```bash
cp .env.example .env
```

Edit `.env` and add your real API keys.

```env
MONGODB_URI=
MONGODB_DB=price_ai

GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

SERPAPI_KEY=
```

Do **not** commit `.env` to GitHub.

---

## Environment Variables

| Variable         | Required | Description                                    |
| ---------------- | -------: | ---------------------------------------------- |
| `MONGODB_URI`    |      Yes | MongoDB Atlas connection string                |
| `MONGODB_DB`     |       No | Database name. Defaults to `price_ai`          |
| `GEMINI_API_KEY` |      Yes | API key from Google AI Studio                  |
| `GEMINI_MODEL`   |       No | Gemini model name. Default: `gemini-2.5-flash` |
| `SERPAPI_KEY`    |      Yes | API key from SerpApi                           |

Example:

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB=price_ai
GEMINI_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-2.5-flash
SERPAPI_KEY=your_serpapi_key_here
```

---

## MongoDB Atlas Setup

1. Create a MongoDB Atlas account.
2. Create a free cluster.
3. Create a database user with read/write permissions.
4. Add the required network access rule.
5. Copy your MongoDB connection string.
6. Paste it into `.env` as `MONGODB_URI`.
7. Keep `MONGODB_DB=price_ai`, unless you want another database name.

PriceAI uses these collections:

```text
search_history
watchlist
alerts
price_history
```

---

## Gemini Setup

1. Go to Google AI Studio.
2. Create a Gemini API key.
3. Add it to `.env`:

```env
GEMINI_API_KEY=your_key_here
```

The default model is:

```env
GEMINI_MODEL=gemini-2.5-flash
```

Gemini is used to explain the best offer and generate buy/wait recommendations.

---

## SerpApi Setup

1. Create a SerpApi account.
2. Copy your API key.
3. Add it to `.env`:

```env

```

PriceAI uses SerpApi Google Shopping to extract:

* product title
* price
* seller
* rating
* number of reviews
* thumbnail
* product link

The app then ranks offers so that cheap accessories, unrelated products, and poor matches are less likely to appear first.

---

## Run the Web App

Start the Flask app:

```bash
python app.py
```

Open the app in your browser:

```text
http://127.0.0.1:5000
```

Main pages:

| Page           | Purpose                                         |
| -------------- | ----------------------------------------------- |
| `/`            | Search products and get AI deal recommendations |
| `/watch`       | View and manage watched products                |
| `/check-watch` | Check all watched products for price drops      |
| `/alerts`      | View price-drop alerts                          |
| `/dashboard`   | View MongoDB stats and app data                 |

---

## Run the CLI

You can also use PriceAI from the terminal:

```bash
python -m price_ai.cli
```

The CLI asks for:

* product name
* country code, for example `ro`, `us`, `uk`, `de`

It then prints:

* top 10 ranked offers
* cheapest relevant offers
* Gemini recommendation
* buy/wait advice

---

## Demo Flow

For a hackathon demo, use this flow:

1. Show the required environment variables are configured.
2. Start the app:

```bash
python app.py
```

3. Open:

```text
http://127.0.0.1:5000
```

4. Search:

```text
iphone 15
```

Country:

```text
ro
```

5. Show the ranked shopping results.
6. Show the Gemini recommendation.
7. Open `/watch`.
8. Add `iphone 15` to the watchlist with an optional target price.
9. Click **Check All Watched Products**.
10. Open `/alerts` to show generated price-drop alerts.
11. Open `/dashboard` to show stored MongoDB data.

---

## How PriceAI Works

PriceAI follows this agent workflow:

```text
User searches product
        ↓
SerpApi fetches live Google Shopping results
        ↓
PriceAI cleans and ranks offers
        ↓
MongoDB stores search history and price data
        ↓
Gemini analyzes the best options
        ↓
User gets a recommendation
        ↓
User can watch the product
        ↓
PriceAI checks later for price drops
        ↓
Alerts are saved when a better price appears
```

---

## Offer Ranking

PriceAI does not simply sort by the lowest price.

It ranks offers using:

* product title match
* price
* seller information
* rating
* review count
* product relevance
* deal quality

This helps avoid bad results such as:

* phone cases when searching for phones
* accessories instead of the real product
* unrelated products
* fake-looking low prices
* low-quality sellers

---

Built by [@aplek0](https://github.com/aplek0) for a hackathon MVP.
