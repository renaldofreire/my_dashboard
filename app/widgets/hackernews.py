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
        # Timestamp de 24 horas atrás
        yesterday_ts = int(time.time()) - (24 * 60 * 60)

        params = {
            "tags": "story",
            "numericFilters": f"created_at_i>{yesterday_ts}",
            "hitsPerPage": 20,  # Pegamos uma amostra razoável para garantir qualidade
        }

        r = requests.get(SEARCH_URL, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()

        # A API Algolia já retorna os hits. Vamos garantir a ordenação por score (upvotes)
        hits = data.get("hits", [])
        hits.sort(key=lambda x: x.get("points", 0), reverse=True)

        stories = []
        for hit in hits[:limit]:
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
