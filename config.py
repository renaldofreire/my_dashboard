import os

# Football API (Free API Live Football Data - Smart API via RapidAPI)
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY", "")
FOOTBALL_API_HOST = "free-api-live-football-data.p.rapidapi.com"

# GitHub
GITHUB_USERNAME = "renaldofreire"

# Cache TTL in seconds
CACHE_TTL_SHORT = 300    # 5 min  — crypto, câmbio
CACHE_TTL_MEDIUM = 600   # 10 min — HN, clima
CACHE_TTL_LONG = 1800    # 30 min — futebol (pouca variação)
