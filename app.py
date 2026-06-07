from __future__ import annotations

from flask import Flask, redirect, render_template, request, url_for

from price_ai.agent import GeminiAgent
from price_ai.alerts import check_watchlist
from price_ai.core import (
    best_value_offer,
    cheapest_offer,
    load_settings,
    parse_price,
    search_products,
)
from price_ai.memory import MongoMemory


app = Flask(__name__)
app.config["SECRET_KEY"] = "price-ai-hackathon-dev"


def setup_status() -> dict[str, object]:
    settings = load_settings()
    mongo_connected = False
    mongo_error = ""
    if settings.mongodb_uri:
        try:
            mongo_connected = MongoMemory(settings).ping()
        except Exception as exc:
            mongo_error = str(exc)
    return {
        "settings": settings,
        "mongo_connected": mongo_connected,
        "mongo_error": mongo_error,
        "gemini_connected": bool(settings.gemini_api_key),
        "serpapi_connected": bool(settings.serpapi_key),
        "missing_required": settings.missing_required,
        "ready": (
            mongo_connected
            and bool(settings.gemini_api_key)
            and bool(settings.serpapi_key)
        ),
    }


def require_ready():
    status = setup_status()
    if not status["ready"]:
        return render_template("setup_error.html", status=status), 503
    return None


@app.before_request
def block_until_configured():
    allowed = {"static"}
    if request.endpoint in allowed:
        return None
    return require_ready()


@app.context_processor
def inject_status():
    return {"setup_status": setup_status()}


def runtime():
    settings = load_settings()
    memory = MongoMemory(settings)
    agent = GeminiAgent(settings)
    return settings, memory, agent


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        settings, memory, agent = runtime()
        product = request.form.get("product", "").strip()
        country = request.form.get("country", "").strip() or "us"
        budget = request.form.get("budget", "").strip() or None

        offers, error = search_products(product, country, settings.serpapi_key, limit=10)
        recommendation = ""
        if not error:
            recommendation = agent.recommend(product, country, budget, offers)
            memory.save_search(product, country, budget, offers, recommendation)

        result = {
            "product": product,
            "country": country,
            "budget": budget,
            "offers": offers,
            "error": error,
            "recommendation": recommendation,
            "cheapest_offer": cheapest_offer(offers),
            "best_value_offer": best_value_offer(offers),
        }
    return render_template("index.html", result=result)


@app.route("/watch", methods=["GET", "POST"])
def watch():
    result = None
    if request.method == "POST":
        settings, memory, _agent = runtime()
        product = request.form.get("product", "").strip()
        country = request.form.get("country", "").strip() or "us"
        target_raw = request.form.get("target_price", "").strip()
        target_price = parse_price(target_raw) if target_raw else None

        offers, error = search_products(product, country, settings.serpapi_key, limit=10)
        baseline_offer = cheapest_offer(offers)
        watch_id = None
        if not error and baseline_offer:
            watch_id = memory.save_watch(product, country, target_price, baseline_offer)
        result = {
            "product": product,
            "country": country,
            "target_price": target_price,
            "offer": baseline_offer,
            "watch_id": watch_id,
            "error": error if error else None,
        }
    return render_template("watch.html", result=result, check_result=None)


@app.route("/check-watch", methods=["GET", "POST"])
def check_watch():
    settings, memory, _agent = runtime()
    result = check_watchlist(settings, memory)
    return render_template("watch.html", result=None, check_result=result)


@app.route("/alerts")
def alerts():
    _settings, memory, _agent = runtime()
    return render_template("alerts.html", alerts=memory.alerts())


@app.route("/dashboard")
def dashboard():
    _settings, memory, _agent = runtime()
    return render_template("dashboard.html", stats=memory.stats())


@app.errorhandler(404)
def not_found(_error):
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
