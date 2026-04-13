from flask import Blueprint, render_template, jsonify
from .widgets.crypto import get_bitcoin_price, get_exchange_rates
from .widgets.hackernews import get_top_stories

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


# --- Crypto & Câmbio ---
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
