import requests
from cachetools import TTLCache, cached
from config import CACHE_TTL_SHORT

_btc_cache = TTLCache(maxsize=1, ttl=CACHE_TTL_SHORT)
_fx_cache = TTLCache(maxsize=1, ttl=CACHE_TTL_SHORT)


@cached(_btc_cache)
def get_bitcoin_price():
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "usd"},
            timeout=5,
        )
        r.raise_for_status()
        usd = r.json()["bitcoin"]["usd"]
        return {"usd": usd, "error": None}
    except Exception as e:
        return {"usd": None, "error": str(e)}


@cached(_fx_cache)
def get_exchange_rates():
    try:
        r_usd = requests.get(
            "https://api.frankfurter.app/latest?from=USD&to=BRL", timeout=5
        )
        r_gbp = requests.get(
            "https://api.frankfurter.app/latest?from=GBP&to=BRL", timeout=5
        )
        r_usd.raise_for_status()
        r_gbp.raise_for_status()
        return {
            "usd_brl": r_usd.json()["rates"]["BRL"],
            "gbp_brl": r_gbp.json()["rates"]["BRL"],
            "error": None,
        }
    except Exception as e:
        return {"usd_brl": None, "gbp_brl": None, "error": str(e)}
