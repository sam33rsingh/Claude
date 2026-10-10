"""Google reviews.

Routes:

1. **Google Places API (New)** - `GOOGLE_PLACES_API_KEY`.  Text search finds
   businesses; Place Details returns at most **5 reviews** per place.  Cheap
   and official, shallow.
2. **SerpApi Google Maps Reviews** - `SERPAPI_KEY`.  Paginates through *all*
   reviews of a place (by `data_id` or `place_id`), with full text and star
   rating.  Paid, but the only sanctioned way to get depth.
3. Otherwise, export reviews (Google Business Profile export, Outscraper,
   Apify) and use `halo-miner import`.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from ..models import Post
from .base import BaseSource, HttpClient, SourceError, dedupe

log = logging.getLogger("halo_miner.google")
PLACES = "https://places.googleapis.com/v1"
SERPAPI = "https://serpapi.com/search.json"


class GoogleReviewsSource(BaseSource):
    name = "google"

    def __init__(self, http: Optional[HttpClient] = None, places_key: Optional[str] = None, serpapi_key: Optional[str] = None):
        super().__init__(http or HttpClient(delay=1.0))
        self.places_key = places_key or os.environ.get("GOOGLE_PLACES_API_KEY")
        self.serpapi_key = serpapi_key or os.environ.get("SERPAPI_KEY")

    # --- Places API (New) --------------------------------------------------
    def text_search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        if not self.places_key:
            raise SourceError("GOOGLE_PLACES_API_KEY not set")
        resp = self.http.request("POST", f"{PLACES}/places:searchText",
                                 headers={"X-Goog-Api-Key": self.places_key, "X-Goog-FieldMask": "places.id,places.displayName,places.googleMapsUri,places.rating,places.userRatingCount"},
                                 json={"textQuery": query, "pageSize": min(max_results, 20)})
        if resp.status_code >= 400:
            raise SourceError(f"places search {resp.status_code}: {resp.text[:200]}")
        return resp.json().get("places", [])

    def place_reviews(self, place: Dict[str, Any]) -> List[Post]:
        data = self.http.get_json(f"{PLACES}/places/{place['id']}", headers={"X-Goog-Api-Key": self.places_key, "X-Goog-FieldMask": "reviews,displayName,googleMapsUri"})
        return self.parse_places_reviews(data)

    @staticmethod
    def parse_places_reviews(data: Dict[str, Any]) -> List[Post]:
        name = (data.get("displayName") or {}).get("text", "")
        url = data.get("googleMapsUri", "")
        posts = []
        for r in data.get("reviews", []):
            text = (r.get("text") or r.get("originalText") or {}).get("text", "")
            if not text:
                continue
            posts.append(Post(source="google", kind="review", text=text, rating=r.get("rating"),
                              author=(r.get("authorAttribution") or {}).get("displayName", ""), url=url,
                              created=(r.get("publishTime") or "")[:10], venue=name, id=(r.get("name") or "").rsplit("/", 1)[-1]))
        return posts

    # --- SerpApi -----------------------------------------------------------
    def serpapi_reviews(self, data_id: Optional[str] = None, place_id: Optional[str] = None, max_pages: int = 10, venue: str = "") -> List[Post]:
        if not self.serpapi_key:
            raise SourceError("SERPAPI_KEY not set")
        params: Dict[str, Any] = {"engine": "google_maps_reviews", "api_key": self.serpapi_key, "hl": "en", "sort_by": "newestFirst"}
        if data_id:
            params["data_id"] = data_id
        elif place_id:
            params["place_id"] = place_id
        else:
            raise SourceError("serpapi needs data_id or place_id")
        posts: List[Post] = []
        for _ in range(max_pages):
            data = self.http.get_json(SERPAPI, params=params)
            posts.extend(self.parse_serpapi_reviews(data, venue))
            token = (data.get("serpapi_pagination") or {}).get("next_page_token")
            if not token:
                break
            params["next_page_token"] = token
        return posts

    @staticmethod
    def parse_serpapi_reviews(data: Dict[str, Any], venue: str = "") -> List[Post]:
        venue = venue or (data.get("place_info") or {}).get("title", "")
        posts = []
        for r in data.get("reviews", []):
            text = r.get("snippet") or (r.get("extracted_snippet") or {}).get("original") or ""
            if not text:
                continue
            posts.append(Post(source="google", kind="review", text=text, rating=r.get("rating"),
                              author=(r.get("user") or {}).get("name", ""), url=r.get("link", ""),
                              created=(r.get("iso_date") or "")[:10], venue=venue, upvotes=int(r.get("likes", 0) or 0),
                              id=r.get("review_id", "")))
        return posts

    # --- orchestrate ---------------------------------------------------------
    def fetch(self, config: Dict[str, Any]) -> List[Post]:
        posts: List[Post] = []
        for place in config.get("places", []):
            try:
                if place.get("data_id") or place.get("place_id"):
                    if self.serpapi_key:
                        posts.extend(self.serpapi_reviews(place.get("data_id"), place.get("place_id"), int(config.get("serpapi_pages", 10)), place.get("name", "")))
                    elif self.places_key and place.get("place_id"):
                        posts.extend(self.place_reviews({"id": place["place_id"]}))
            except SourceError as e:
                log.warning("google place %s failed: %s", place, e)
        if self.places_key:
            for q in config.get("queries", []):
                try:
                    for place in self.text_search(q, int(config.get("places_per_query", 10))):
                        posts.extend(self.place_reviews(place))
                except SourceError as e:
                    log.warning("google query %r failed: %s", q, e)
        if not posts:
            log.warning("google: nothing fetched (set GOOGLE_PLACES_API_KEY or SERPAPI_KEY, or import an export)")
        return dedupe(posts)
