from halo_miner.classify import HaloClassifier
from halo_miner.models import Post
from halo_miner.score import HaloWeights, halo_score, length_weight, star_weight

W = HaloWeights.default()
C = HaloClassifier()


def _score(rating, text):
    p = Post(source="google", rating=rating, text=text)
    return halo_score(p, C.classify(p), W)["halo_score"]


def test_three_and_four_star_outrank_five_star_for_same_text():
    text = "The design was lovely but the timeline slipped and the invoice was confusing. Still recommend."
    assert _score(3, text) > _score(5, text)
    assert _score(4, text) > _score(5, text)
    assert _score(3, text) > _score(1, text)


def test_longer_post_outranks_shorter_post():
    short = "Frustrating process, loved the result."
    long = " ".join(["Frustrating process, loved the result, and here is the long story of why."] * 12)
    assert _score(4, long) > _score(4, short)


def test_length_weight_is_capped():
    p = Post(source="reddit", text="word " * 100000)
    assert length_weight(p, W) == W.length_cap


def test_star_weight_overrides():
    w = HaloWeights.default({"star_weights": {"5": 2.0}})
    assert star_weight(Post(source="yelp", rating=5, text="x"), w) == 2.0
    assert star_weight(Post(source="reddit", text="x"), w) == 1.0
