from halo_miner.classify import HaloClassifier, split_sentences
from halo_miner.models import Post


def test_split_sentences_keeps_real_sentences():
    s = split_sentences("I was scared. Honestly the designer listened to us! Now our home feels like us.")
    assert len(s) == 3


def test_buckets_detected_per_sentence():
    p = Post(source="google", rating=4, text=(
        "I was terrified they would impose their taste on us. "
        "We hoped for a calm, light-filled living room. "
        "It is the dream kitchen I have pictured since childhood. "
        "The invoice was frustrating and went over budget. "
        "Highly recommend, worth every penny."
    ))
    c = HaloClassifier().classify(p)
    for cat in ("fears", "hopes", "dreams", "pains", "testimonials"):
        assert c.scores[cat] > 0, cat
        assert cat in c.quotes
    assert "terrified" in c.quotes["fears"].text.lower()
    assert "worth every penny" in c.quotes["testimonials"].text.lower()
    assert c.primary in c.scores


def test_topics_objections_triggers():
    p = Post(source="reddit", text="We just closed on a new house. Got quoted $150/hr and I think DIY with Pinterest might be cheaper. Afraid of surprise invoices.")
    c = HaloClassifier().classify(p)
    assert "budget & pricing" in c.topics
    assert any("diy" in o for o in c.objections)
    assert any("closed" in t or "new house" in t for t in c.triggers)


def test_neutral_when_no_signal():
    c = HaloClassifier().classify(Post(source="csv", text="The table is brown and measures two metres."))
    assert c.primary == "neutral"
