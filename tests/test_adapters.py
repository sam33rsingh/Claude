import json
from pathlib import Path

import pytest

from halo_miner.sources import load_file
from halo_miner.sources.adapters import detect_and_convert
from halo_miner.sources.base import SourceError
from halo_miner.sources.reddit import RedditSource


def test_gosom_extended_reviews(tmp_path: Path):
    data = [{"title": "Studio Quattro Design", "link": "https://maps.google.com/?cid=1",
             "user_reviews": [{"Name": "A", "Rating": 5, "Description": "Short.", "When": "a month ago"}],
             "user_reviews_extended": [
                 {"review_id": "r1", "Name": "Melissa", "rating_float": 4.0, "text_original": "Installation was on schedule, communication was clear, a small gap by the fridge.",
                  "posted_at_unix_micros": 1757000000000000, "author_url": "https://maps.google.com/u/1", "reply_text": "Thanks!"},
                 {"review_id": "r2", "Name": "B", "rating_float": 5.0, "text_original": "", "published_at": "2026-09-01T00:00:00Z"},
             ]}]
    name, posts = detect_and_convert(data)
    assert name == "gosom/google-maps-scraper"
    assert len(posts) == 1 and posts[0].rating == 4.0 and posts[0].created == "2025-09-04" and posts[0].venue == "Studio Quattro Design"
    f = tmp_path / "gmaps.json"
    f.write_text(json.dumps(data))
    assert len(load_file(f)) == 1


def test_gosom_basic_reviews_only():
    data = [{"title": "Biz", "user_reviews": [{"Name": "A", "Rating": 3, "Description": "Fine but slow.", "When": "2 weeks ago"}]}]
    name, posts = detect_and_convert(data)
    assert posts[0].rating == 3.0 and posts[0].meta["when"] == "2 weeks ago"


def test_reviews_scraper_pro_multilanguage():
    data = [{"review_id": "x", "author": "Karla", "rating": 5, "description": {"en": "Beautiful showroom, friendly team.", "es": "Hermoso."},
             "review_date": "2026-03-04T10:00:00", "likes": 2, "company": "Studio Quattro Design", "owner_responses": []}]
    name, posts = detect_and_convert(data)
    assert name == "google-reviews-scraper-pro" and posts[0].text.startswith("Beautiful") and posts[0].upvotes == 2 and posts[0].created == "2026-03-04"


def test_business_profile_api_enum_rating():
    data = {"reviews": [{"reviewId": "abc", "reviewer": {"displayName": "Denedra"}, "starRating": "FOUR", "comment": "Knowledgeable about cabinet options.", "createTime": "2026-05-06T00:00:00Z", "reviewReply": {"comment": "Thank you"}}]}
    name, posts = detect_and_convert(data)
    assert name == "google-business-profile-api" and posts[0].rating == 4.0 and posts[0].meta["reply"] == "Thank you"


def test_places_serpapi_fusion_detected():
    places = {"displayName": {"text": "Biz"}, "reviews": [{"rating": 3, "text": {"text": "ok"}, "authorAttribution": {"displayName": "C"}, "publishTime": "2026-03-04T00:00:00Z"}]}
    serp = {"place_info": {"title": "Biz"}, "reviews": [{"review_id": "z", "rating": 4, "snippet": "Good."}]}
    fusion = {"business_name": "Biz", "reviews": [{"id": "r", "text": "Great.", "rating": 5, "user": {"name": "B"}, "time_created": "2026-02-03 10:00:00"}]}
    assert detect_and_convert(places)[0] == "google-places-api"
    assert detect_and_convert(serp)[0] == "serpapi-google-maps-reviews"
    assert detect_and_convert(fusion)[0] == "yelp-fusion"


def test_unknown_json_falls_back_to_rows(tmp_path: Path):
    f = tmp_path / "x.json"
    f.write_text(json.dumps([{"Review Text": "Lovely.", "Stars": 5}]))
    posts = load_file(f, default_source="google")
    assert len(posts) == 1 and posts[0].source == "google"


def test_reddit_requires_oauth(monkeypatch):
    monkeypatch.delenv("REDDIT_CLIENT_ID", raising=False)
    monkeypatch.delenv("REDDIT_CLIENT_SECRET", raising=False)
    with pytest.raises(SourceError, match="OAuth"):
        RedditSource()
    assert RedditSource(allow_unauthenticated=True).authenticated is False
