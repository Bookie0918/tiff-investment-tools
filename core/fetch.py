import feedparser
from datetime import datetime, timezone
from core.config import SOURCES, MAX_ITEMS_PER_SOURCE


def _parse_time(entry) -> datetime:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def _get_content(entry) -> str:
    if hasattr(entry, "content") and entry.content:
        return entry.content[0].value[:1500]
    if hasattr(entry, "summary"):
        return entry.summary[:1500]
    return ""


def fetch_all(max_age_hours: int = 24) -> list[dict]:
    articles = []
    cutoff = datetime.now(timezone.utc).timestamp() - max_age_hours * 3600

    for source in SOURCES:
        try:
            feed = feedparser.parse(
                source["url"],
                request_headers={"User-Agent": "Mozilla/5.0"}
            )
            count = 0
            for entry in feed.entries:
                if count >= MAX_ITEMS_PER_SOURCE:
                    break
                pub_time = _parse_time(entry)
                if pub_time.timestamp() < cutoff:
                    continue
                articles.append({
                    "source_name": source["name"],
                    "category": source["category"],
                    "title": entry.get("title", "").strip(),
                    "link": entry.get("link", ""),
                    "content": _get_content(entry),
                    "published": pub_time.strftime("%Y-%m-%d %H:%M UTC"),
                    "summary": None,
                })
                count += 1
        except Exception:
            pass

    articles.sort(key=lambda x: x["published"], reverse=True)
    return articles
