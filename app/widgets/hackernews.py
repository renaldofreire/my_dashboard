import requests
import time
from cachetools import TTLCache, cached
from config import CACHE_TTL_MEDIUM

_cache = TTLCache(maxsize=10, ttl=CACHE_TTL_MEDIUM)

# API Algolia para busca avançada no Hacker News
SEARCH_URL = "https://hn.algolia.com/api/v1/search"


@cached(_cache)
def get_top_stories(limit=5):
    try:
        # Timestamp de exatas 24 horas atrás
        now = int(time.time())
        yesterday_ts = now - (24 * 60 * 60)

        params = {
            "tags": "story",
            "numericFilters": f"created_at_i>{yesterday_ts}",
            "hitsPerPage": 100,  # Pegamos o top 100 do dia para garantir que os 5 melhores estejam aqui
        }

        r = requests.get(SEARCH_URL, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()

        hits = data.get("hits", [])
        
        # Filtragem e ordenação manual rigorosa por pontos (upvotes)
        # Garantimos que o item é de fato das últimas 24h e é uma história com pontos
        valid_stories = [
            h for h in hits 
            if h.get("created_at_i", 0) > yesterday_ts 
            and h.get("points") is not None
        ]
        
        # Ordena de forma decrescente pelos pontos
        valid_stories.sort(key=lambda x: x.get("points", 0), reverse=True)

        stories = []
        for hit in valid_stories[:limit]:
            stories.append(
                {
                    "id": hit.get("objectID"),
                    "title": hit.get("title"),
                    "url": hit.get("url")
                    or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                    "score": hit.get("points"),
                    "by": hit.get("author"),
                    "time": hit.get("created_at_i"),
                }
            )

        return {"stories": stories, "error": None}
    except Exception as e:
        return {"stories": [], "error": str(e)}
