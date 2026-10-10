import json

from halo_miner.sources.csv_import import rows_to_posts
from halo_miner.sources.google import GoogleReviewsSource
from halo_miner.sources.reddit import RedditSource
from halo_miner.sources.yelp import YelpSource


def test_reddit_listing_and_comments_parse():
    listing = {"data": {"after": None, "children": [
        {"kind": "t3", "data": {"id": "abc", "title": "Worth it?", "selftext": "Scared of fees.", "author": "u1", "permalink": "/r/x/comments/abc/", "created_utc": 1700000000, "score": 12, "num_comments": 3, "subreddit": "x"}},
        {"kind": "t3", "data": {"id": "sticky", "title": "Rules", "selftext": "", "stickied": True, "permalink": "/r/x/comments/s/", "subreddit": "x"}},
    ]}}
    posts = RedditSource.parse_listing(listing, "worth it")
    assert len(posts) == 1 and posts[0].kind == "post" and posts[0].upvotes == 12 and posts[0].created == "2023-11-14"
    thread = [{}, {"data": {"children": [
        {"kind": "t1", "data": {"id": "c1", "body": " ".join(["long"] * 30), "author": "u2", "permalink": "/r/x/comments/abc/c1/", "score": 5,
                                "replies": {"data": {"children": [{"kind": "t1", "data": {"id": "c2", "body": "short", "replies": ""}}]}}}},
    ]}}]
    comments = RedditSource.parse_comments(thread, "/r/x/comments/abc/", "x")
    assert len(comments) == 1 and comments[0].kind == "comment"


def test_yelp_jsonld_parse():
    html = '<html><script type="application/ld+json">' + json.dumps({
        "@type": "LocalBusiness", "name": "Studio X",
        "review": [{"author": {"name": "A"}, "datePublished": "2026-01-02", "reviewRating": {"ratingValue": 4}, "reviewBody": "Loved it but pricey."}],
    }) + "</script></html>"
    posts = YelpSource.parse_jsonld(html, url="https://yelp.com/biz/x")
    assert len(posts) == 1 and posts[0].rating == 4.0 and posts[0].venue == "Studio X"


def test_yelp_fusion_parse():
    posts = YelpSource.parse_fusion_reviews({"reviews": [{"id": "r1", "text": "Great.", "rating": 5, "user": {"name": "B"}, "time_created": "2026-02-03 10:00:00"}]}, "Biz")
    assert posts[0].created == "2026-02-03" and posts[0].meta["excerpt"]


def test_google_parsers():
    places = {"displayName": {"text": "Biz"}, "googleMapsUri": "https://maps.google.com/?cid=1",
              "reviews": [{"name": "places/1/reviews/abc", "rating": 3, "text": {"text": "Fine, slow."}, "authorAttribution": {"displayName": "C"}, "publishTime": "2026-03-04T00:00:00Z"}]}
    p = GoogleReviewsSource.parse_places_reviews(places)
    assert p[0].rating == 3.0 and p[0].id == "abc"
    serp = {"place_info": {"title": "Biz"}, "reviews": [{"review_id": "z", "rating": 4, "snippet": "Good but late.", "user": {"name": "D"}, "iso_date": "2026-04-05T00:00:00Z", "likes": 2}]}
    q = GoogleReviewsSource.parse_serpapi_reviews(serp)
    assert q[0].upvotes == 2 and q[0].venue == "Biz"


def test_csv_alias_mapping_and_dedupe():
    rows = [
        {"Review Text": "Loved the designer.", "Stars": "5 out of 5", "Reviewer": "E", "Published": "2026-05-06T10:00:00"},
        {"Review Text": "Loved the designer.", "Stars": "5", "Reviewer": "E"},
        {"body": "", "title": ""},
    ]
    posts = rows_to_posts(rows, default_source="google")
    assert len(posts) == 1 and posts[0].rating == 5.0 and posts[0].created == "2026-05-06" and posts[0].source == "google"
