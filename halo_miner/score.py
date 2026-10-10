"""Halo weighting - which voices deserve the copywriter's attention first.

Two rules from the Halo Strategy drive the weights:

* **3- and 4-star reviews are gold.**  Five-star reviews gush, one-star
  reviews rage; the middle band explains *what they wanted, what they got,
  and the gap*.  They get a 1.5x multiplier by default.
* **The longest posts are the most invested.**  Someone who writes 400
  words about their renovation is handing you their inner monologue.
  Length is rewarded on a log curve so a 600-word post outranks a 60-word
  one without a 6000-word rant swamping everything.

Reddit engagement (upvotes, comments) and emotional intensity add smaller
boosts.  All multipliers are configurable.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Optional

from .classify import Classification
from .models import Post

DEFAULT_STAR_WEIGHTS: Dict[str, float] = {
    "3": 1.5, "4": 1.5,     # balanced, most honest
    "2": 1.1, "1": 0.9,     # useful for pains/fears, but often one-note
    "5": 0.8,               # proof language, but little nuance
    "unrated": 1.0,         # Reddit / forums
}


@dataclass
class HaloWeights:
    star_weights: Dict[str, float]
    length_reference_words: int = 120      # a post this long gets ~1.7x
    length_cap: float = 3.0
    engagement_scale: float = 0.12
    intensity_scale: float = 0.02
    emotional_signal_scale: float = 0.05

    @classmethod
    def default(cls, overrides: Optional[Dict] = None) -> "HaloWeights":
        w = cls(star_weights=dict(DEFAULT_STAR_WEIGHTS))
        for k, v in (overrides or {}).items():
            if k == "star_weights":
                w.star_weights.update({str(kk): float(vv) for kk, vv in v.items()})
            elif hasattr(w, k):
                setattr(w, k, v)
        return w


def star_weight(post: Post, weights: HaloWeights) -> float:
    if post.rating is None:
        return weights.star_weights.get("unrated", 1.0)
    key = str(int(round(post.rating)))
    return weights.star_weights.get(key, 1.0)


def length_weight(post: Post, weights: HaloWeights) -> float:
    ref = max(weights.length_reference_words, 1)
    return min(1.0 + math.log1p(post.word_count / ref), weights.length_cap)


def engagement_weight(post: Post, weights: HaloWeights) -> float:
    return 1.0 + weights.engagement_scale * math.log1p(max(post.upvotes, 0) + max(post.comments, 0))


def halo_score(post: Post, cls: Classification, weights: HaloWeights) -> Dict[str, float]:
    sw = star_weight(post, weights)
    lw = length_weight(post, weights)
    ew = engagement_weight(post, weights)
    iw = 1.0 + weights.intensity_scale * min(cls.intensity, 15.0)
    signal = sum(cls.scores.values())
    sig_w = 1.0 + weights.emotional_signal_scale * math.log1p(signal)
    total = sw * lw * ew * iw * sig_w
    return {
        "halo_score": round(total, 3),
        "star_weight": round(sw, 3),
        "length_weight": round(lw, 3),
        "engagement_weight": round(ew, 3),
        "intensity_weight": round(iw, 3),
        "signal_weight": round(sig_w, 3),
    }
