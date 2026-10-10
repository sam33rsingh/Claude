"""Reddit via the official Data API with OAuth (free "script" app).

Since late May 2026 Reddit returns 403 to unauthenticated ``.json`` requests
from servers, so credentials are required by default: create an app at
https://www.reddit.com/prefs/apps (type *script*), then set
``REDDIT_CLIENT_ID`` and ``REDDIT_CLIENT_SECRET``.  The miner uses the
client-credentials grant against ``oauth.reddit.com`` (~100 requests/min).

Set ``allow_unauthenticated: true`` in the reddit config to try the legacy
public endpoints anyway (works from some residential IPs, never from cloud).
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from ..models import Post
from .base import BaseSource, HttpClient, SourceError, dedupe

log = logging.getLogger("halo_miner.reddit")

PUBLIC = "https://www.reddit.com"
OAUTH = "https://oauth.reddit.com"

DEFAULT_SUBREDDITS = ["kitchenremodel", "InteriorDesign", "HomeImprovement", "Renovations", "homeowners", "Remodel", "DesignMyRoom", "HomeDecorating", "Cabinetry", "sandiego", "orangecounty"]
DEFAULT_QUERIES = [
    "kitchen designer worth it", "hired a kitchen designer", "kitchen showroom experience",
    "Italian kitchen cabinets", "European cabinets vs American", "custom cabinets vs IKEA",
    "cabinet quality particle board", "cabinet lead time delay", "cabinets arrived damaged",
    "kitchen remodel regret", "kitchen remodel over budget", "contractor nightmare kitchen",
    "custom closet worth it", "walk-in closet design", "bathroom vanity quality",
    "dream kitchen finally", "forever home kitchen", "overwhelmed kitchen decisions",
]


def _iso(ts: Optional[float]) -> str:
    if not ts:
        return ""
    return datetime.fromtimestamp(float(ts), tz=timezone.utc).date().isoformat()


class RedditSource(BaseSource):
    name = "reddit"

    def __init__(self, http: Optional[HttpClient] = None, client_id: Optional[str] = None, client_secret: Optional[str] = None, allow_unauthenticated: bool = False):
        super().__init__(http or HttpClient(delay=6.0))
        self.client_id = client_id or os.environ.get("REDDIT_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("REDDIT_CLIENT_SECRET")
        self.base = PUBLIC
        self.authenticated = False
        self.allow_unauthenticated = allow_unauthenticated
        self._auth()

    def _auth(self) -> None:
        if not (self.client_id and self.client_secret):
            if not self.allow_unauthenticated:
                raise SourceError(
                    "Reddit now requires OAuth (unauthenticated .json requests return 403 since May 2026). "
                    "Create a free 'script' app at https://www.reddit.com/prefs/apps and set "
                    "REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET, or set reddit.allow_unauthenticated: true to try anyway."
                )
            log.warning("reddit: no credentials - trying legacy public endpoints (expect 403 from cloud IPs)")
            return
        try:
            resp = self.http.request(
                "POST", f"{PUBLIC}/api/v1/access_token",
                data={"grant_type": "client_credentials"},
                auth=(self.client_id, self.client_secret),
            )
            token = resp.json().get("access_token")
            if not token:
                raise SourceError(f"reddit: token response had no access_token: {resp.text[:200]}")
            self.http.session.headers["Authorization"] = f"bearer {token}"
            self.base = OAUTH
            self.authenticated = True
            self.http.delay = min(self.http.delay, 1.0)
            log.info("reddit: OAuth enabled")
        except (SourceError, ValueError) as e:
            if not self.allow_unauthenticated:
                raise SourceError(f"reddit: OAuth failed ({e}); check REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET") from e
            log.warning("reddit: OAuth failed (%s); continuing unauthenticated", e)

    # --- parsing (pure, unit-tested) ------------------------------------
    @staticmethod
    def parse_listing(data: Dict[str, Any], query: str = "") -> List[Post]:
        posts: List[Post] = []
        for child in data.get("data", {}).get("children", []):
            d = child.get("data", {})
            if child.get("kind") != "t3" or d.get("stickied"):
                continue
            text = d.get("selftext") or ""
            if text in ("[removed]", "[deleted]"):
                text = ""
            if not text and not d.get("title"):
                continue
            posts.append(Post(
                source="reddit", kind="post", title=d.get("title", ""), text=text,
                author=d.get("author", ""), url="https://www.reddit.com" + d.get("permalink", ""),
                created=_iso(d.get("created_utc")), upvotes=int(d.get("score", 0) or 0),
                comments=int(d.get("num_comments", 0) or 0), venue=d.get("subreddit", ""), query=query,
                id=d.get("id", ""), meta={"flair": d.get("link_flair_text")},
            ))
        return posts

    @staticmethod
    def parse_comments(thread: List[Any], permalink: str, subreddit: str, min_words: int = 25) -> List[Post]:
        out: List[Post] = []

        def walk(children: Iterable[Dict[str, Any]], depth: int) -> None:
            for ch in children:
                if ch.get("kind") != "t1":
                    continue
                d = ch.get("data", {})
                body = d.get("body") or ""
                if body not in ("[removed]", "[deleted]") and len(body.split()) >= min_words:
                    out.append(Post(
                        source="reddit", kind="comment", text=body, author=d.get("author", ""),
                        url="https://www.reddit.com" + d.get("permalink", permalink), created=_iso(d.get("created_utc")),
                        upvotes=int(d.get("score", 0) or 0), venue=subreddit, id=d.get("id", ""), meta={"depth": depth},
                    ))
                replies = d.get("replies")
                if isinstance(replies, dict):
                    walk(replies.get("data", {}).get("children", []), depth + 1)

        if len(thread) > 1 and isinstance(thread[1], dict):
            walk(thread[1].get("data", {}).get("children", []), 0)
        return out

    # --- fetching ---------------------------------------------------------
    def search(self, subreddit: str, query: str, limit: int = 100, time_filter: str = "all", pages: int = 1) -> List[Post]:
        posts: List[Post] = []
        after = None
        for _ in range(pages):
            params = {"q": query, "restrict_sr": 1, "sort": "relevance", "t": time_filter, "limit": min(limit, 100), "raw_json": 1}
            if after:
                params["after"] = after
            try:
                data = self.http.get_json(f"{self.base}/r/{subreddit}/search.json", params=params)
            except SourceError as e:
                if "403" in str(e) and not self.authenticated:
                    raise SourceError("403 from Reddit: unauthenticated access is blocked; set REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET") from e
                raise
            posts.extend(self.parse_listing(data, query))
            after = data.get("data", {}).get("after")
            if not after:
                break
        return posts

    def comments_for(self, post: Post, limit: int = 200) -> List[Post]:
        path = post.url.replace("https://www.reddit.com", "")
        data = self.http.get_json(f"{self.base}{path}.json", params={"limit": limit, "depth": 4, "sort": "top", "raw_json": 1})
        return self.parse_comments(data, path, post.venue)

    def fetch(self, config: Dict[str, Any]) -> List[Post]:
        subs = config.get("subreddits") or DEFAULT_SUBREDDITS
        queries = config.get("queries") or DEFAULT_QUERIES
        limit = int(config.get("limit_per_query", 50))
        pages = int(config.get("pages", 1))
        time_filter = config.get("time_filter", "all")
        comment_top_n = int(config.get("comments_for_top_posts", 0))
        posts: List[Post] = []
        for sub in subs:
            for q in queries:
                try:
                    found = self.search(sub, q, limit=limit, time_filter=time_filter, pages=pages)
                    log.info("reddit r/%s %r -> %d posts", sub, q, len(found))
                    posts.extend(found)
                except SourceError as e:
                    log.warning("reddit r/%s %r failed: %s", sub, q, e)
        posts = dedupe(posts)
        if comment_top_n:
            ranked = sorted(posts, key=lambda p: p.comments, reverse=True)[:comment_top_n]
            for p in ranked:
                try:
                    posts.extend(self.comments_for(p))
                except SourceError as e:
                    log.warning("reddit comments %s failed: %s", p.url, e)
        return dedupe(posts)
