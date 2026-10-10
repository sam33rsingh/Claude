"""Sentence-level Halo classification.

Every post is split into sentences; every sentence is scored against each
Halo bucket.  A post therefore carries *several* buckets at once (a 3-star
review usually praises and complains in the same breath), plus the single
best quotable sentence for each bucket - the raw material for the swipe file.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Pattern, Tuple

from .lexicon import (
    FIRST_PERSON,
    HALO_CATEGORIES,
    INTENSIFIERS,
    OBJECTIONS,
    TRIGGERS,
    compile_lexicon,
    compile_simple,
    compile_topics,
)
from .models import Post

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])|\n{2,}|(?<=[.!?])\s*\n")
_WORD_RE = re.compile(r"[A-Za-z0-9'’]+")

MIN_QUOTE_WORDS = 6
MAX_QUOTE_WORDS = 70


def split_sentences(text: str) -> List[str]:
    parts = [p.strip() for p in _SENT_SPLIT.split(text or "") if p and p.strip()]
    return [p for p in parts if len(_WORD_RE.findall(p)) >= 3]


@dataclass
class Quote:
    text: str
    category: str
    score: float
    matched: List[str] = field(default_factory=list)


@dataclass
class Classification:
    post_id: str
    scores: Dict[str, float]                 # raw weighted hits per bucket
    density: Dict[str, float]                # hits per 100 words
    primary: str                             # strongest bucket (or "neutral")
    quotes: Dict[str, Quote]                 # best sentence per bucket
    topics: Dict[str, int]                   # topic -> sentence hits
    objections: List[str]                    # matched objection phrases
    triggers: List[str]                      # matched life-event phrases
    intensity: float                         # intensifiers per 100 words
    first_person: float                      # first-person pronouns per 100 words
    matched_terms: Dict[str, List[str]]      # category -> distinct matched substrings

    def to_dict(self) -> Dict:
        return {
            "post_id": self.post_id,
            "scores": self.scores,
            "density": self.density,
            "primary": self.primary,
            "quotes": {k: {"text": q.text, "score": q.score, "matched": q.matched} for k, q in self.quotes.items()},
            "topics": self.topics,
            "objections": self.objections,
            "triggers": self.triggers,
            "intensity": self.intensity,
            "first_person": self.first_person,
            "matched_terms": self.matched_terms,
        }


class HaloClassifier:
    def __init__(
        self,
        extra_lexicon: Dict[str, List[Tuple[str, float]]] | None = None,
        extra_topics: Dict[str, str] | None = None,
    ) -> None:
        self.lexicon = compile_lexicon(extra_lexicon)
        self.topics = compile_topics(extra_topics)
        self.objections = compile_simple(OBJECTIONS)
        self.triggers = compile_simple(TRIGGERS)

    @staticmethod
    def _hits(patterns: List[Tuple[Pattern[str], float]], text: str) -> Tuple[float, List[str]]:
        total = 0.0
        matched: List[str] = []
        for pat, weight in patterns:
            found = pat.findall(text)
            if found:
                total += weight * len(found)
                m = pat.search(text)
                if m:
                    matched.append(m.group(0).lower())
        return total, matched

    def classify(self, post: Post) -> Classification:
        sentences = split_sentences(post.full_text) or [post.full_text]
        words = max(post.word_count, 1)

        scores = {c: 0.0 for c in HALO_CATEGORIES}
        quotes: Dict[str, Quote] = {}
        matched_terms: Dict[str, List[str]] = {c: [] for c in HALO_CATEGORIES}
        topic_hits = {t: 0 for t in self.topics}

        for sent in sentences:
            n_words = len(_WORD_RE.findall(sent))
            for cat, patterns in self.lexicon.items():
                s, matched = self._hits(patterns, sent)
                if s <= 0:
                    continue
                scores[cat] += s
                for m in matched:
                    if m not in matched_terms[cat]:
                        matched_terms[cat].append(m)
                # Quotable: emotionally dense, first person, right length.
                quotable = s * (1.0 + 0.15 * len(FIRST_PERSON.findall(sent)))
                if n_words < MIN_QUOTE_WORDS:
                    quotable *= 0.3
                elif n_words > MAX_QUOTE_WORDS:
                    quotable *= 0.6
                if cat not in quotes or quotable > quotes[cat].score:
                    quotes[cat] = Quote(text=sent.strip(), category=cat, score=round(quotable, 2), matched=matched)
            for topic, pat in self.topics.items():
                if pat.search(sent):
                    topic_hits[topic] += 1

        full = post.full_text
        _, objections = self._hits(self.objections, full)
        _, triggers = self._hits(self.triggers, full)
        intensity = 100.0 * len(INTENSIFIERS.findall(full)) / words
        first_person = 100.0 * len(FIRST_PERSON.findall(full)) / words
        density = {c: round(100.0 * v / words, 2) for c, v in scores.items()}

        best = max(scores, key=scores.get)  # type: ignore[arg-type]
        primary = best if scores[best] > 0 else "neutral"

        return Classification(
            post_id=post.id,
            scores={c: round(v, 2) for c, v in scores.items()},
            density=density,
            primary=primary,
            quotes=quotes,
            topics={t: n for t, n in topic_hits.items() if n},
            objections=objections,
            triggers=triggers,
            intensity=round(intensity, 2),
            first_person=round(first_person, 2),
            matched_terms=matched_terms,
        )
