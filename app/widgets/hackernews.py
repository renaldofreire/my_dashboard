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
        r = requests.get(f"{BASE_URL}/topstories.json", timeout=5)
        r.raise_for_status()
        ids = r.json()[:limit]

        stories = []
        with ThreadPoolExecutor(max_workers=limit) as executor:
            futures = {executor.submit(_fetch_item, i): i for i in ids}
            for future in as_completed(futures):
                try:
                    stories.append(future.result())
                except Exception:
                    pass

        # Mantém a ordem original (as_completed não garante ordem)
        id_order = {item_id: idx for idx, item_id in enumerate(ids)}
        stories.sort(key=lambda s: id_order.get(s.get("id"), 999))

        return {"stories": stories, "error": None}
    except Exception as e:
        return {"stories": [], "error": str(e)}
