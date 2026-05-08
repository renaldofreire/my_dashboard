from flask import Blueprint, render_template, jsonify, request
from .widgets.crypto import get_bitcoin_price, get_exchange_rates
from .widgets.hackernews import get_top_stories
from .widgets.weather import get_weather
from .widgets.github_activity import get_recent_activity

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


# --- Crypto & Câmbio ---
@bp.route("/api/finances")
def finances():
    return jsonify({
        "bitcoin": get_bitcoin_price(),
        "exchange": get_exchange_rates()
    })


@bp.route("/api/bitcoin")
def bitcoin():
    return jsonify(get_bitcoin_price())


@bp.route("/api/exchange")
def exchange():
    return jsonify(get_exchange_rates())


# --- Hacker News ---
@bp.route("/api/hackernews")
def hackernews():
    return jsonify(get_top_stories())


# --- Clima ---
@bp.route("/api/weather")
def weather():
    city = request.args.get("city", "fortaleza")
    return jsonify(get_weather(city))


# --- GitHub ---
@bp.route("/api/github")
def github():
    return jsonify(get_recent_activity())
