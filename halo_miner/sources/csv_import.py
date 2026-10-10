"""Import reviews/posts from CSV, JSON or JSONL exports (any vendor).

Column names are matched loosely so exports from Google Business Profile,
Outscraper, Apify, Yelp data exports or a hand-made spreadsheet all work.
"""
from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from ..models import Post
from .base import dedupe

log = logging.getLogger("halo_miner.import")

ALIASES: Dict[str, List[str]] = {
    "text": ["text", "review", "review_text", "reviewbody", "body", "content", "comment", "snippet", "selftext", "description", "review text"],
    "title": ["title", "headline", "subject", "summary"],
    "rating": ["rating", "stars", "star", "score_rating", "review_rating", "ratingvalue", "star_rating", "review stars"],
    "author": ["author", "author_name", "user", "username", "name", "reviewer", "author_title"],
    "url": ["url", "link", "review_url", "permalink", "reviews_link"],
    "created": ["created", "date", "published", "publishedatdate", "review_datetime_utc", "time_created", "created_utc", "datepublished", "published_at"],
    "upvotes": ["upvotes", "score", "likes", "review_likes", "useful", "ups", "helpful"],
    "comments": ["comments", "num_comments", "replies", "comment_count"],
    "venue": ["venue", "business", "business_name", "place", "subreddit", "name_of_business", "company", "location_name"],
    "source": ["source", "platform", "site"],
    "kind": ["kind", "type"],
}


def _norm(k: str) -> str:
    return k.strip().lower().replace(" ", "_")


def _pick(row: Dict[str, Any], field: str) -> Optional[Any]:
    keys = {_norm(k): k for k in row.keys()}
    for alias in ALIASES[field]:
        a = _norm(alias)
        if a in keys and row[keys[a]] not in (None, ""):
            return row[keys[a]]
    return None


def _int(v: Any) -> int:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def row_to_post(row: Dict[str, Any], default_source: str = "csv") -> Optional[Post]:
    text = _pick(row, "text")
    title = _pick(row, "title") or ""
    if not text and not title:
        return None
    rating = _pick(row, "rating")
    if isinstance(rating, str):
        rating = rating.strip().split()[0].replace("/5", "") if rating.strip() else None
    kind = str(_pick(row, "kind") or ("review" if rating not in (None, "") else "post"))
    return Post(
        source=str(_pick(row, "source") or default_source).lower(), text=str(text or ""), title=str(title),
        rating=rating if rating not in (None, "") else None, author=str(_pick(row, "author") or ""),
        url=str(_pick(row, "url") or ""), created=str(_pick(row, "created") or "")[:10],
        upvotes=_int(_pick(row, "upvotes")), comments=_int(_pick(row, "comments")),
        venue=str(_pick(row, "venue") or ""), kind=kind,
    )


def rows_to_posts(rows: Iterable[Dict[str, Any]], default_source: str = "csv") -> List[Post]:
    posts = [p for p in (row_to_post(r, default_source) for r in rows) if p]
    return dedupe(posts)


def load_file(path: str | Path, default_source: str = "csv") -> List[Post]:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    elif suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = data if isinstance(data, list) else data.get("reviews") or data.get("posts") or data.get("data") or []
    else:
        with path.open(newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))
    # Already-serialised Post dicts round-trip exactly.
    if rows and isinstance(rows[0], dict) and {"source", "text", "kind"} <= set(rows[0].keys()) and suffix in (".json", ".jsonl"):
        return dedupe([Post.from_dict(r) for r in rows])
    if suffix == ".json":
        from .adapters import detect_and_convert
        hit = detect_and_convert(data)
        if hit:
            log.info("import: recognised %s output (%d reviews)", hit[0], len(hit[1]))
            return dedupe(hit[1])
    return rows_to_posts(rows, default_source)


def save_jsonl(posts: Iterable[Post], path: str | Path) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8") as fh:
        for p in posts:
            fh.write(json.dumps(p.to_dict(), ensure_ascii=False) + "\n")
            n += 1
    return n
