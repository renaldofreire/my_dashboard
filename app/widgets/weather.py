import requests
from cachetools import TTLCache, cached
from config import CACHE_TTL_MEDIUM

_cache = TTLCache(maxsize=4, ttl=CACHE_TTL_MEDIUM)

CITIES = {
    "fortaleza": {
        "name": "Fortaleza",
        "lat": -3.7172,
        "lon": -38.5433,
    },
    "maracanau": {
        "name": "Maracanaú",
        "lat": -3.8711,
        "lon": -38.6267,
    },
}

# WMO weather codes → descrição e categoria
WMO_CODES = {
    0:  ("Céu limpo",        "clear"),
    1:  ("Predomin. limpo",  "clear"),
    2:  ("Parcial. nublado", "cloudy"),
    3:  ("Nublado",          "cloudy"),
    45: ("Neblina",          "cloudy"),
    48: ("Neblina com gelo", "cloudy"),
    51: ("Garoa fraca",      "rain"),
    53: ("Garoa moderada",   "rain"),
    55: ("Garoa intensa",    "rain"),
    61: ("Chuva fraca",      "rain"),
    63: ("Chuva moderada",   "rain"),
    65: ("Chuva forte",      "rain"),
    80: ("Pancadas fracas",  "rain"),
    81: ("Pancadas moderadas","rain"),
    82: ("Pancadas fortes",  "rain"),
    95: ("Tempestade",       "storm"),
    96: ("Tempestade c/ granizo", "storm"),
    99: ("Tempestade c/ granizo", "storm"),
}


def _will_rain(code, precip_prob):
    """Retorna True se há chance real de chuva hoje."""
    _, category = WMO_CODES.get(code, ("", "clear"))
    return category in ("rain", "storm") or (precip_prob is not None and precip_prob >= 60)


@cached(_cache)
def get_weather(city_key="fortaleza"):
    city = CITIES.get(city_key, CITIES["fortaleza"])
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": city["lat"],
                "longitude": city["lon"],
                "current": "temperature_2m,weathercode,precipitation",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "timezone": "America/Fortaleza",
                "forecast_days": 1,
            },
            timeout=5
        )
        r.raise_for_status()
        data = r.json()

        current = data["current"]
        daily   = data["daily"]

        code        = current["weathercode"]
        temp        = current["temperature_2m"]
        precip      = current["precipitation"]
        temp_max    = daily["temperature_2m_max"][0]
        temp_min    = daily["temperature_2m_min"][0]
        precip_prob = daily["precipitation_probability_max"][0]

        description, category = WMO_CODES.get(code, ("Condição desconhecida", "clear"))

        return {
            "city":        city["name"],
            "temp":        temp,
            "temp_max":    temp_max,
            "temp_min":    temp_min,
            "description": description,
            "category":    category,
            "precip":      precip,
            "precip_prob": precip_prob,
            "will_rain":   _will_rain(code, precip_prob),
            "error":       None,
        }
    except Exception as e:
        return {"city": city["name"], "error": str(e)}
