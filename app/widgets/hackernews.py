import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from cachetools import TTLCache, cached
from config import CACHE_TTL_MEDIUM

_cache = TTLCache(maxsize=10, ttl=CACHE_TTL_MEDIUM)

BASE_URL = "https://hacker-news.firebaseio.com/v0"


def _fetch_item(item_id):
    r = requests.get(f"{BASE_URL}/item/{item_id}.json", timeout=5)
    r.raise_for_status()
    return r.json()


@cached(_cache)
def get_top_stories(limit=5):
    try:
        # Busca uma lista maior de IDs para podermos filtrar por upvotes
        r = requests.get(f"{BASE_URL}/topstories.json", timeout=5)
        r.raise_for_status()
        ids = r.json()[:30]

        stories = []
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = {executor.submit(_fetch_item, i): i for i in ids}
            for future in as_completed(futures):
                try:
                    stories.append(future.result())
                except Exception:
                    pass

        # Filtra apenas itens válidos (não None e que tenham score) e ordena por upvotes (score)
        stories = [s for s in stories if s and "score" in s]
        stories.sort(key=lambda s: s.get("score", 0), reverse=True)

        return {"stories": stories[:limit], "error": None}
    except Exception as e:
        return {"stories": [], "error": str(e)}
