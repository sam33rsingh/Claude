"""Optional Claude pass for nuance the lexicon misses (sarcasm, implied fears,
the dream behind a complaint).  Enabled with ``--llm``.  Needs the ``anthropic``
package and credentials (``ANTHROPIC_API_KEY`` or an ``ant auth login`` profile).

Each post is classified into the five Halo buckets with 0-10 intensity scores
and one verbatim quote per bucket; results are merged into the lexicon
classification (max of the two) so the deterministic baseline is never lost.
"""
from __future__ import annotations

import json
import logging
from typing import Dict, List, Optional, Sequence

from .analyze import ScoredPost
from .classify import Quote
from .lexicon import HALO_CATEGORIES

log = logging.getLogger("halo_miner.llm")

MODEL = "claude-opus-5-5"

SCHEMA = {
    "type": "object",
    "properties": {
        "posts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "scores": {
                        "type": "object",
                        "properties": {c: {"type": "integer", "minimum": 0, "maximum": 10} for c in HALO_CATEGORIES},
                        "required": HALO_CATEGORIES,
                        "additionalProperties": False,
                    },
                    "quotes": {
                        "type": "object",
                        "properties": {c: {"type": "string"} for c in HALO_CATEGORIES},
                        "required": HALO_CATEGORIES,
                        "additionalProperties": False,
                    },
                    "dream_buyer_note": {"type": "string"},
                },
                "required": ["id", "scores", "quotes", "dream_buyer_note"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["posts"],
    "additionalProperties": False,
}

SYSTEM = """You are a direct-response copywriter doing Halo Strategy research (Sabri Suby, Sell Like Crazy)
for a residential interior design studio. For each customer post, rate 0-10 how strongly it expresses each bucket:
pains (present frustrations), fears (anticipated bad outcomes), hopes (what they are seeking), dreams (the vivid
after-picture they long for), testimonials (proof language of delight). Then copy ONE verbatim sentence from the
post that best voices each bucket (empty string if none). Add a one-line dream_buyer_note: who this person is and
what they are really buying. Never paraphrase quotes - copy exact words."""


def _client():
    try:
        import anthropic  # noqa: WPS433 - optional dependency
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("pip install anthropic to use --llm") from e
    return anthropic, anthropic.Anthropic()


def classify_batch(scored: Sequence[ScoredPost], model: str = MODEL, batch_size: int = 12) -> Dict[str, Dict]:
    anthropic, client = _client()
    results: Dict[str, Dict] = {}
    for i in range(0, len(scored), batch_size):
        batch = scored[i : i + batch_size]
        payload = [{"id": s.post.id, "rating": s.post.rating, "source": s.post.source, "text": s.post.full_text[:6000]} for s in batch]
        try:
            resp = client.beta.messages.create(
                model=model,
                max_tokens=16000,
                system=SYSTEM,
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}},
                messages=[{"role": "user", "content": "Classify these posts:\n" + json.dumps(payload, ensure_ascii=False)}],
            )
        except anthropic.RateLimitError as e:
            log.warning("rate limited (%s); skipping batch %d", e, i // batch_size)
            continue
        except anthropic.APIStatusError as e:
            log.warning("API error %s on batch %d: %s", e.status_code, i // batch_size, e.message)
            continue
        except anthropic.APIConnectionError as e:
            log.warning("network error on batch %d: %s", i // batch_size, e)
            continue
        if resp.stop_reason == "refusal":
            log.warning("batch %d refused; keeping lexicon result", i // batch_size)
            continue
        text = next((b.text for b in resp.content if b.type == "text"), "")
        try:
            data = json.loads(text)
        except ValueError:
            log.warning("batch %d returned non-JSON; skipping", i // batch_size)
            continue
        for item in data.get("posts", []):
            results[item["id"]] = item
    return results


def merge(scored: Sequence[ScoredPost], llm: Dict[str, Dict]) -> int:
    """Blend LLM scores into the lexicon classification in place. Returns posts touched."""
    touched = 0
    for s in scored:
        item = llm.get(s.post.id)
        if not item:
            continue
        touched += 1
        words = max(s.post.word_count, 1)
        for c in HALO_CATEGORIES:
            llm_score = float(item["scores"].get(c, 0)) * 0.6   # 10/10 ≈ 6 weighted lexicon hits
            s.cls.scores[c] = round(max(s.cls.scores[c], llm_score), 2)
            s.cls.density[c] = round(100.0 * s.cls.scores[c] / words, 2)
            q = (item["quotes"].get(c) or "").strip()
            if q and (c not in s.cls.quotes or len(q.split()) >= 6):
                s.cls.quotes[c] = Quote(text=q, category=c, score=round(max(llm_score, s.cls.quotes[c].score if c in s.cls.quotes else 0), 2), matched=["llm"])
        best = max(s.cls.scores, key=s.cls.scores.get)  # type: ignore[arg-type]
        s.cls.primary = best if s.cls.scores[best] > 0 else "neutral"
        s.post.meta["dream_buyer_note"] = item.get("dream_buyer_note", "")
    return touched
