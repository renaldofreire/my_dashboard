import requests
from cachetools import TTLCache, cached
from config import CACHE_TTL_MEDIUM, GITHUB_USERNAME

_cache = TTLCache(maxsize=2, ttl=CACHE_TTL_MEDIUM)

EVENT_LABELS = {
    "PushEvent": "push",
    "PullRequestEvent": "pull request",
    "IssuesEvent": "issue",
    "CreateEvent": "criou branch/tag",
    "WatchEvent": "starred",
    "ForkEvent": "fork",
    "IssueCommentEvent": "comentário",
    "PullRequestReviewEvent": "review",
    "DeleteEvent": "deletou branch/tag",
    "ReleaseEvent": "release",
}


def _summarize(event):
    etype = event.get("type", "")
    repo = event.get("repo", {}).get("name", "")
    label = EVENT_LABELS.get(etype, etype.replace("Event", ""))
    payload = event.get("payload", {})

    detail = ""
    if etype == "PushEvent":
        commits = payload.get("commits", [])
        count = payload.get("size") or len(commits)
        msg = commits[0]["message"].split("\n")[0] if commits else ""
        detail = f"{count} commit(s) — {msg}" if msg else f"{count} commit(s)"
    elif etype == "PullRequestEvent":
        action = payload.get("action", "")
        title = payload.get("pull_request", {}).get("title", "")
        detail = f"{action} — {title}"
    elif etype == "IssuesEvent":
        action = payload.get("action", "")
        title = payload.get("issue", {}).get("title", "")
        detail = f"{action} — {title}"
    elif etype == "CreateEvent":
        ref_type = payload.get("ref_type", "")
        ref = payload.get("ref", "")
        detail = f"{ref_type} {ref}".strip()

    return {
        "type": label,
        "repo": repo,
        "detail": detail,
        "url": f"https://github.com/{repo}",
    }


@cached(_cache)
def get_recent_activity(limit=6):
    try:
        r = requests.get(
            f"https://api.github.com/users/{GITHUB_USERNAME}/events/public",
            headers={"Accept": "application/vnd.github+json"},
            timeout=5,
        )
        r.raise_for_status()
        events = r.json()[:limit]
        return {
            "username": GITHUB_USERNAME,
            "events": [_summarize(e) for e in events],
            "error": None,
        }
    except Exception as e:
        return {"username": GITHUB_USERNAME, "events": [], "error": str(e)}
