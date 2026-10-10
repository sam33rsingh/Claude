"""Yelp reviews.

Two routes, both optional:

1. **Yelp Fusion API** (free key, `YELP_API_KEY`): business search plus the
   `/reviews` endpoint.  Honest limitation: Fusion returns only **3 review
   excerpts** (about 160 characters each) per business, so it is good for
   discovering businesses and thin on voice-of-customer depth.
2. **Business page JSON-LD** (`html: true` in config): Yelp business pages
   embed up to 10 full reviews per page as schema.org JSON-LD.  This reads
   public pages politely (one request every few seconds) but Yelp's Terms of
   Service restrict automated access - enable it only for your own
   listing/competitive research where you've accepted that risk, or use a
   licensed export (Outscraper, Apify, etc.) and `halo-miner import` instead.
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

from ..models import Post
from .base import BaseSource, HttpClient, SourceError, dedupe

log = logging.getLogger("halo_miner.yelp")
FUSION = "https://api.yelp.com/v3"
_LD_RE = re.compile(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', re.S | re.I)


class YelpSource(BaseSource):
    name = "yelp"

    def __init__(self, http: Optional[HttpClient] = None, api_key: Optional[str] = None):
        super().__init__(http or HttpClient(delay=3.0))
        self.api_key = api_key or os.environ.get("YELP_API_KEY")

    # --- Fusion -------------------------------------------------------------
    def _headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise SourceError("YELP_API_KEY not set")
        return {"Authorization": f"Bearer {self.api_key}"}

    def search_businesses(self, term: str, location: str, limit: int = 20) -> List[Dict[str, Any]]:
        data = self.http.get_json(f"{FUSION}/businesses/search", headers=self._headers(),
                                  params={"term": term, "location": location, "limit": min(limit, 50), "sort_by": "review_count"})
        return data.get("businesses", [])

    def fusion_reviews(self, business: Dict[str, Any]) -> List[Post]:
        data = self.http.get_json(f"{FUSION}/businesses/{business['id']}/reviews", headers=self._headers(), params={"limit": 20, "sort_by": "yelp_sort"})
        return self.parse_fusion_reviews(data, business.get("name", ""), business.get("url", ""))

    @staticmethod
    def parse_fusion_reviews(data: Dict[str, Any], business_name: str, business_url: str = "") -> List[Post]:
        posts = []
        for r in data.get("reviews", []):
            posts.append(Post(source="yelp", kind="review", text=r.get("text", ""), rating=r.get("rating"),
                              author=(r.get("user") or {}).get("name", ""), url=r.get("url") or business_url,
                              created=(r.get("time_created") or "")[:10], venue=business_name, id=r.get("id", ""),
                              meta={"excerpt": True}))
        return posts

    # --- JSON-LD from business pages ------------------------------------------
    @staticmethod
    def parse_jsonld(html: str, business_name: str = "", url: str = "") -> List[Post]:
        posts: List[Post] = []
        for raw in _LD_RE.findall(html):
            try:
                data = json.loads(raw.strip())
            except ValueError:
                continue
            items = data if isinstance(data, list) else [data]
            for item in items:
                if not isinstance(item, dict):
                    continue
                name = item.get("name") or business_name
                for r in item.get("review", []) or []:
                    rating = (r.get("reviewRating") or {}).get("ratingValue")
                    author = r.get("author")
                    author = author.get("name", "") if isinstance(author, dict) else (author or "")
                    body = r.get("reviewBody") or r.get("description") or ""
                    if not body:
                        continue
                    posts.append(Post(source="yelp", kind="review", text=body, rating=rating, author=author,
                                      url=url, created=(r.get("datePublished") or "")[:10], venue=name))
        return posts

    def page_reviews(self, business_url: str, pages: int = 3, business_name: str = "") -> List[Post]:
        posts: List[Post] = []
        for i in range(pages):
            url = f"{business_url}{'&' if '?' in business_url else '?'}start={i * 10}"
            try:
                html = self.http.get_text(url)
            except SourceError as e:
                log.warning("yelp page %s failed: %s", url, e)
                break
            batch = self.parse_jsonld(html, business_name, business_url)
            if not batch:
                break
            posts.extend(batch)
        return posts

    # --- orchestrate ---------------------------------------------------------
    def fetch(self, config: Dict[str, Any]) -> List[Post]:
        posts: List[Post] = []
        term = config.get("term", "interior designer")
        locations = config.get("locations") or []
        use_html = bool(config.get("html", False))
        pages = int(config.get("pages", 3))
        businesses: List[Dict[str, Any]] = [{"name": b.get("name", ""), "url": b["url"], "id": b.get("id")} for b in config.get("businesses", [])]
        if self.api_key and locations:
            for loc in locations:
                try:
                    businesses.extend(self.search_businesses(term, loc, int(config.get("businesses_per_location", 10))))
                except SourceError as e:
                    log.warning("yelp search %s failed: %s", loc, e)
        if not businesses:
            log.warning("yelp: no businesses configured and no YELP_API_KEY/locations - skipping")
            return []
        for b in businesses:
            if self.api_key and b.get("id"):
                try:
                    posts.extend(self.fusion_reviews(b))
                except SourceError as e:
                    log.warning("yelp fusion reviews %s failed: %s", b.get("name"), e)
            if use_html and b.get("url"):
                posts.extend(self.page_reviews(b["url"].split("?")[0], pages=pages, business_name=b.get("name", "")))
        return dedupe(posts)
