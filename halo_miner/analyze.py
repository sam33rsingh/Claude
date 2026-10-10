"""Numerical analysis over classified, weighted posts."""
from __future__ import annotations

import math
import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Sequence, Tuple

from .classify import Classification, HaloClassifier
from .lexicon import HALO_CATEGORIES, STOPWORDS
from .models import Post
from .score import HaloWeights, halo_score

_WORD_RE = re.compile(r"[a-z0-9'’]+")


def _pct(n: int, d: int) -> float:
    return round(100.0 * n / d, 1) if d else 0.0


def _mean(xs: Sequence[float]) -> float:
    return round(statistics.fmean(xs), 2) if xs else 0.0


def _median(xs: Sequence[float]) -> float:
    return round(statistics.median(xs), 1) if xs else 0.0


def _percentile(xs: Sequence[float], p: float) -> float:
    if not xs:
        return 0.0
    s = sorted(xs)
    k = (len(s) - 1) * p
    f, c = math.floor(k), math.ceil(k)
    if f == c:
        return round(s[int(k)], 1)
    return round(s[f] + (s[c] - s[f]) * (k - f), 1)


def pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    if len(xs) < 3 or len(xs) != len(ys):
        return 0.0
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return round(num / den, 3) if den else 0.0


def ngrams(text: str, n: int) -> Iterable[str]:
    toks = [t for t in _WORD_RE.findall(text.lower()) if t not in STOPWORDS and len(t) > 2]
    for i in range(len(toks) - n + 1):
        yield " ".join(toks[i : i + n])


def top_phrases(texts: Iterable[str], n_values=(1, 2, 3), k: int = 12) -> Dict[str, List[Tuple[str, int]]]:
    out: Dict[str, List[Tuple[str, int]]] = {}
    texts = list(texts)
    for n in n_values:
        c: Counter = Counter()
        for t in texts:
            c.update(set(ngrams(t, n)))      # count documents, not repeats
        min_docs = 2 if len(texts) >= 6 else 1
        out[f"{n}-gram"] = [(g, cnt) for g, cnt in c.most_common(k * 3) if cnt >= min_docs][:k]
    return out


class ScoredPost:
    __slots__ = ("post", "cls", "weights")

    def __init__(self, post: Post, cls: Classification, weights: Dict[str, float]):
        self.post, self.cls, self.weights = post, cls, weights

    @property
    def halo(self) -> float:
        return self.weights["halo_score"]

    def summary(self, quote_cat: str | None = None) -> Dict:
        p = self.post
        d = {
            "id": p.id, "source": p.source, "kind": p.kind, "venue": p.venue, "rating": p.rating,
            "star_band": p.star_band, "words": p.word_count, "upvotes": p.upvotes, "comments": p.comments,
            "url": p.url, "title": p.title[:120], "primary": self.cls.primary,
            "halo_score": self.halo, "scores": self.cls.scores,
        }
        cat = quote_cat or (self.cls.primary if self.cls.primary != "neutral" else None)
        if cat and cat in self.cls.quotes:
            d["quote"] = self.cls.quotes[cat].text
        else:
            d["quote"] = p.text[:280]
        return d


def score_posts(posts: Sequence[Post], classifier: HaloClassifier, weights: HaloWeights) -> List[ScoredPost]:
    out = []
    for p in posts:
        cls = classifier.classify(p)
        out.append(ScoredPost(p, cls, halo_score(p, cls, weights)))
    return out


def analyze(scored: Sequence[ScoredPost], top_n: int = 15, swipe_n: int = 12, is_fixture: bool = False) -> Dict:
    posts = [s.post for s in scored]
    n = len(posts)
    words = [p.word_count for p in posts]

    # --- Overview -----------------------------------------------------------
    by_source = Counter(p.source for p in posts)
    by_kind = Counter(p.kind for p in posts)
    overview = {
        "posts": n,
        "by_source": dict(by_source),
        "by_kind": dict(by_kind),
        "total_words": sum(words),
        "avg_words": _mean(words),
        "median_words": _median(words),
        "length_percentiles": {"p25": _percentile(words, 0.25), "p50": _percentile(words, 0.5),
                               "p75": _percentile(words, 0.75), "p90": _percentile(words, 0.9)},
    }

    # --- Stars --------------------------------------------------------------
    rated = [p for p in posts if p.rating is not None]
    star_counts = Counter(str(int(round(p.rating))) for p in rated)  # type: ignore[arg-type]
    band_counts = Counter(p.star_band for p in posts)
    words_by_band: Dict[str, List[int]] = defaultdict(list)
    words_by_star: Dict[str, List[int]] = defaultdict(list)
    for p in posts:
        words_by_band[p.star_band].append(p.word_count)
        if p.rating is not None:
            words_by_star[str(int(round(p.rating)))].append(p.word_count)
    mid = band_counts.get("3-4 star", 0)
    stars = {
        "rated_posts": len(rated),
        "distribution": {k: star_counts.get(k, 0) for k in "12345"},
        "distribution_pct": {k: _pct(star_counts.get(k, 0), len(rated)) for k in "12345"},
        "avg_rating": _mean([p.rating for p in rated]),  # type: ignore[misc]
        "band_counts": dict(band_counts),
        "band_pct": {b: _pct(c, n) for b, c in band_counts.items()},
        "share_3_4_of_rated": _pct(mid, len(rated)),
        "avg_words_by_band": {b: _mean(v) for b, v in words_by_band.items()},
        "avg_words_by_star": {k: _mean(words_by_star[k]) for k in "12345" if words_by_star.get(k)},
    }

    # --- Categories ---------------------------------------------------------
    any_counts = {c: sum(1 for s in scored if s.cls.scores[c] > 0) for c in HALO_CATEGORIES}
    primary_counts = Counter(s.cls.primary for s in scored)
    total_words = max(sum(words), 1)
    per_1000 = {c: round(1000.0 * sum(s.cls.scores[c] for s in scored) / total_words, 2) for c in HALO_CATEGORIES}
    by_band: Dict[str, Dict[str, float]] = {}
    for band in ("1-2 star", "3-4 star", "5-star", "unrated"):
        grp = [s for s in scored if s.post.star_band == band]
        if grp:
            by_band[band] = {c: _mean([s.cls.density[c] for s in grp]) for c in HALO_CATEGORIES}
            by_band[band]["n"] = len(grp)
    # Halo-weighted share: what the *weighted* evidence says matters most.
    weighted = {c: sum(s.cls.scores[c] * s.halo for s in scored) for c in HALO_CATEGORIES}
    wsum = sum(weighted.values()) or 1.0
    categories = {
        "posts_with_signal": any_counts,
        "posts_with_signal_pct": {c: _pct(v, n) for c, v in any_counts.items()},
        "primary_counts": dict(primary_counts),
        "primary_pct": {c: _pct(v, n) for c, v in primary_counts.items()},
        "hits_per_1000_words": per_1000,
        "mean_density_by_band": by_band,
        "halo_weighted_share_pct": {c: round(100.0 * v / wsum, 1) for c, v in weighted.items()},
    }

    # --- Complaint vs praise by band ---------------------------------------
    cp: Dict[str, Dict[str, float]] = {}
    for band in by_band:
        grp = [s for s in scored if s.post.star_band == band]
        neg = sum(s.cls.scores["pains"] + s.cls.scores["fears"] for s in grp)
        pos = sum(s.cls.scores["testimonials"] for s in grp)
        cp[band] = {"complaint_signal": round(neg, 1), "praise_signal": round(pos, 1),
                    "complaint_to_praise": round(neg / pos, 2) if pos else float("inf") if neg else 0.0,
                    "both_present_pct": _pct(sum(1 for s in grp if (s.cls.scores["pains"] + s.cls.scores["fears"]) > 0 and s.cls.scores["testimonials"] > 0), len(grp))}

    # --- Topics -------------------------------------------------------------
    topic_counts: Counter = Counter()
    topic_by_cat: Dict[str, Counter] = defaultdict(Counter)
    for s in scored:
        for t, hits in s.cls.topics.items():
            topic_counts[t] += hits
            if s.cls.primary != "neutral":
                topic_by_cat[t][s.cls.primary] += hits
    topics = {
        "sentence_hits": dict(topic_counts.most_common()),
        "posts_mentioning_pct": {t: _pct(sum(1 for s in scored if t in s.cls.topics), n) for t in topic_counts},
        "by_primary_category": {t: dict(c) for t, c in topic_by_cat.items()},
    }

    # --- Keywords per category (from quotable sentences) --------------------
    keywords = {}
    for c in HALO_CATEGORIES:
        texts = [s.cls.quotes[c].text for s in scored if c in s.cls.quotes]
        keywords[c] = top_phrases(texts)
    matched_terms = {c: Counter(t for s in scored for t in s.cls.matched_terms.get(c, [])).most_common(15) for c in HALO_CATEGORIES}

    # --- Objections & triggers ---------------------------------------------
    objections = Counter(o for s in scored for o in s.cls.objections).most_common(15)
    triggers = Counter(t for s in scored for t in s.cls.triggers).most_common(15)

    # --- Correlations -------------------------------------------------------
    sig = [sum(s.cls.scores.values()) for s in scored]
    correlations = {
        "length_vs_total_signal": pearson(words, sig),
        "length_vs_pain_density": pearson(words, [s.cls.density["pains"] for s in scored]),
        "length_vs_dream_density": pearson(words, [s.cls.density["dreams"] for s in scored]),
        "rating_vs_pain_score": pearson([s.post.rating for s in scored if s.post.rating is not None],  # type: ignore[misc]
                                        [s.cls.scores["pains"] for s in scored if s.post.rating is not None]),
        "rating_vs_testimonial_score": pearson([s.post.rating for s in scored if s.post.rating is not None],  # type: ignore[misc]
                                               [s.cls.scores["testimonials"] for s in scored if s.post.rating is not None]),
        "intensity_mean": _mean([s.cls.intensity for s in scored]),
        "first_person_mean": _mean([s.cls.first_person for s in scored]),
    }

    # --- Priority reading lists ---------------------------------------------
    by_halo = sorted(scored, key=lambda s: s.halo, reverse=True)
    longest = sorted(scored, key=lambda s: s.post.word_count, reverse=True)
    mid_star = sorted([s for s in scored if s.post.star_band == "3-4 star"], key=lambda s: s.halo, reverse=True)
    long_threshold = _percentile(words, 0.75)
    top_posts = {
        "by_halo_score": [s.summary() for s in by_halo[:top_n]],
        "longest": [s.summary() for s in longest[:top_n]],
        "mid_star_3_4": [s.summary() for s in mid_star[:top_n]],
        "long_post_threshold_words": long_threshold,
        "long_posts_count": sum(1 for w in words if w >= long_threshold),
    }

    # --- Swipe file ---------------------------------------------------------
    swipe: Dict[str, List[Dict]] = {}
    for c in HALO_CATEGORIES:
        cands = [s for s in scored if c in s.cls.quotes and s.cls.scores[c] > 0]
        cands.sort(key=lambda s: s.cls.quotes[c].score * s.halo, reverse=True)
        seen = set()
        rows = []
        for s in cands:
            q = s.cls.quotes[c].text
            key = q.lower()[:80]
            if key in seen:
                continue
            seen.add(key)
            rows.append({"quote": q, "post_id": s.post.id, "source": s.post.source, "rating": s.post.rating,
                         "star_band": s.post.star_band, "words": s.post.word_count, "halo_score": s.halo,
                         "url": s.post.url, "matched": s.cls.quotes[c].matched})
            if len(rows) >= swipe_n:
                break
        swipe[c] = rows

    return {
        "meta": {
            "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "posts": n,
            "is_fixture": is_fixture,
            "framework": "Halo Strategy (Sabri Suby, Sell Like Crazy) - pains / fears / hopes / dreams / testimonials",
        },
        "overview": overview,
        "stars": stars,
        "categories": categories,
        "complaint_vs_praise": cp,
        "topics": topics,
        "keywords": keywords,
        "matched_terms": matched_terms,
        "objections": objections,
        "triggers": triggers,
        "correlations": correlations,
        "top_posts": top_posts,
        "swipe": swipe,
    }
