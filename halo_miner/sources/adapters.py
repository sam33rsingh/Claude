"""Importers for the output formats of the open-source scrapers and official
APIs that actually work in 2026.  ``load_file`` tries these before falling
back to loose CSV/JSON column mapping.

Recognised shapes:

* **gosom/google-maps-scraper** (`-json`): list of place entries with
  ``user_reviews`` / ``user_reviews_extended`` (Go struct ``Review``).
* **georgekhananaev/google-reviews-scraper-pro** (`google_reviews.json`):
  list of reviews with ``description`` keyed by language.
* **Google Business Profile API** (`accounts.locations.reviews.list`):
  ``{"reviews": [{"reviewId", "reviewer", "starRating": "FIVE", "comment", ...}]}``
  - the free, official route to *all* of your own reviews.
* **Google Places API (New)** place details, **SerpApi** google_maps_reviews,
  **Yelp Fusion** `/reviews` - re-using the live-source parsers.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..models import Post
from .google import GoogleReviewsSource
from .yelp import YelpSource

STAR_ENUM = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5}


def _micros_to_date(us: Any) -> str:
    try:
        us = int(us)
    except (TypeError, ValueError):
        return ""
    if us <= 0:
        return ""
    return datetime.fromtimestamp(us / 1_000_000, tz=timezone.utc).date().isoformat()


# --- gosom/google-maps-scraper ----------------------------------------------

def is_gosom(data: Any) -> bool:
    if isinstance(data, dict):
        data = [data]
    return isinstance(data, list) and bool(data) and isinstance(data[0], dict) and (
        "user_reviews" in data[0] or "user_reviews_extended" in data[0]
    )


def parse_gosom(data: Any) -> List[Post]:
    entries = data if isinstance(data, list) else [data]
    posts: List[Post] = []
    for entry in entries:
        venue = entry.get("title") or entry.get("name") or ""
        link = entry.get("link") or entry.get("url") or ""
        reviews = entry.get("user_reviews_extended") or entry.get("user_reviews") or []
        for r in reviews:
            text = r.get("text_original") or r.get("text_translated") or r.get("Description") or r.get("description") or ""
            if not text:
                continue
            rating = r.get("rating_float") or r.get("Rating") or r.get("rating")
            created = ""
            if r.get("published_at"):
                created = str(r["published_at"])[:10]
            elif r.get("posted_at_unix_micros"):
                created = _micros_to_date(r["posted_at_unix_micros"])
            posts.append(Post(
                source="google", kind="review", text=text, rating=rating,
                author=r.get("Name") or r.get("name") or "", url=r.get("author_url") or link,
                created=created, venue=venue, id=r.get("review_id") or "",
                meta={"tool": "gosom/google-maps-scraper", "when": r.get("When") or r.get("when") or "",
                      "reply": r.get("reply_text") or ""},
            ))
    return posts


# --- georgekhananaev/google-reviews-scraper-pro ------------------------------

def is_reviews_scraper_pro(data: Any) -> bool:
    rows = data.get("reviews") if isinstance(data, dict) else data
    return isinstance(rows, list) and bool(rows) and isinstance(rows[0], dict) and "description" in rows[0] and (
        isinstance(rows[0]["description"], dict) or "review_date" in rows[0]
    )


def parse_reviews_scraper_pro(data: Any) -> List[Post]:
    rows = data.get("reviews") if isinstance(data, dict) else data
    posts: List[Post] = []
    for r in rows:
        desc = r.get("description")
        if isinstance(desc, dict):
            text = desc.get("en") or next((v for v in desc.values() if v), "")
        else:
            text = desc or ""
        if not text:
            continue
        posts.append(Post(
            source="google", kind="review", text=text, rating=r.get("rating"),
            author=r.get("author", ""), url=r.get("author_profile_url", ""),
            created=str(r.get("review_date") or "")[:10], venue=r.get("company", ""),
            upvotes=int(r.get("likes", 0) or 0), id=r.get("review_id", ""),
            meta={"tool": "google-reviews-scraper-pro", "owner_responses": r.get("owner_responses")},
        ))
    return posts


# --- Google Business Profile API --------------------------------------------

def is_business_profile(data: Any) -> bool:
    rows = data.get("reviews") if isinstance(data, dict) else None
    return isinstance(rows, list) and bool(rows) and isinstance(rows[0], dict) and "starRating" in rows[0]


def parse_business_profile(data: Dict[str, Any], venue: str = "") -> List[Post]:
    posts: List[Post] = []
    for r in data.get("reviews", []):
        text = r.get("comment") or ""
        if not text:
            continue
        rating = STAR_ENUM.get(str(r.get("starRating", "")).upper())
        posts.append(Post(
            source="google", kind="review", text=text, rating=rating,
            author=(r.get("reviewer") or {}).get("displayName", ""), created=str(r.get("createTime") or "")[:10],
            venue=venue, id=r.get("reviewId", ""),
            meta={"tool": "google-business-profile-api", "reply": (r.get("reviewReply") or {}).get("comment", "")},
        ))
    return posts


# --- Registry ------------------------------------------------------------------

def _is_places(data: Any) -> bool:
    return isinstance(data, dict) and isinstance(data.get("reviews"), list) and bool(data["reviews"]) and "authorAttribution" in data["reviews"][0]


def _is_serpapi(data: Any) -> bool:
    return isinstance(data, dict) and isinstance(data.get("reviews"), list) and bool(data["reviews"]) and ("snippet" in data["reviews"][0] or "review_id" in data["reviews"][0]) and "place_info" in data


def _is_fusion(data: Any) -> bool:
    return isinstance(data, dict) and isinstance(data.get("reviews"), list) and bool(data["reviews"]) and "time_created" in data["reviews"][0]


ADAPTERS: List[Tuple[str, Callable[[Any], bool], Callable[[Any], List[Post]]]] = [
    ("gosom/google-maps-scraper", is_gosom, parse_gosom),
    ("google-reviews-scraper-pro", is_reviews_scraper_pro, parse_reviews_scraper_pro),
    ("google-business-profile-api", is_business_profile, parse_business_profile),
    ("google-places-api", _is_places, GoogleReviewsSource.parse_places_reviews),
    ("serpapi-google-maps-reviews", _is_serpapi, GoogleReviewsSource.parse_serpapi_reviews),
    ("yelp-fusion", _is_fusion, lambda d: YelpSource.parse_fusion_reviews(d, d.get("business_name", ""))),
]


def detect_and_convert(data: Any) -> Optional[Tuple[str, List[Post]]]:
    """Return (format_name, posts) when the JSON matches a known tool, else None."""
    for name, detect, parse in ADAPTERS:
        try:
            if detect(data):
                return name, parse(data)
        except (KeyError, TypeError, AttributeError):
            continue
    return None
