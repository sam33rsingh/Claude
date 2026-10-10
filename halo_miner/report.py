"""Render the analysis as a copywriter's research brief (Markdown + JSON + CSV)."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Sequence

from .analyze import ScoredPost
from .lexicon import CATEGORY_LABELS, HALO_CATEGORIES

INF = float("inf")


def _fmt(v) -> str:
    if v == INF:
        return "∞"
    if isinstance(v, float):
        return f"{v:.1f}" if abs(v) >= 10 else f"{v:.2f}"
    return str(v)


def _table(headers: Sequence[str], rows: Sequence[Sequence]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(_fmt(c) for c in r) + " |")
    return "\n".join(out)


def _bar(pct: float, width: int = 20) -> str:
    filled = int(round(width * min(max(pct, 0), 100) / 100))
    return "█" * filled + "░" * (width - filled)


def _clean(q: str, limit: int = 320) -> str:
    q = re.sub(r"\s+", " ", q).strip()
    return q if len(q) <= limit else q[: limit - 1].rsplit(" ", 1)[0] + "…"


def _cite(row: Dict) -> str:
    bits = [row["source"]]
    if row.get("rating") is not None:
        bits.append(f"{int(round(row['rating']))}★")
    bits.append(f"{row['words']} words")
    bits.append(f"halo {row['halo_score']:.2f}")
    return ", ".join(bits)


# --- Copy angles -------------------------------------------------------------
# Deterministic templates: the data chooses the words, the templates give the
# copywriter a first draft of hooks in each Halo direction.

TOPIC_PHRASES = {
    "budget & pricing": ("budget surprises", "knowing the number before you start"),
    "communication & responsiveness": ("weeks of radio silence", "a weekly update you never have to chase"),
    "timeline & delays": ("the timeline that quietly doubles", "a schedule you can plan your life around"),
    "quality & craftsmanship": ("sloppy finishes you have to redo", "work you never have to look twice at"),
    "trust & honesty": ("markups you find out about later", "every dollar accounted for"),
    "style, taste & cohesion": ("a house that looks like a showroom", "a home that looks like you"),
    "process & decision stress": ("decision paralysis", "one decision at a time, made with you"),
    "contractors & trades": ("chasing contractors yourself", "one person in charge of every trade"),
    "function & livability": ("rooms that photograph well but don't work", "a home that works for how you actually live"),
    "designer value & fit": ("wondering if a designer is worth it", "knowing exactly what you are paying for"),
}


def _short(q: str, limit: int = 140) -> str:
    return _clean(q, limit).rstrip(".…") + ("…" if len(q) > limit else "")


def copy_angles(a: Dict, brand: str, service: str) -> List[str]:
    """First-draft hooks in each Halo direction, built from topics and verbatim quotes."""
    lines: List[str] = []
    bycat = a["topics"]["by_primary_category"]
    ranked = list(a["topics"]["sentence_hits"].keys())
    pain_topics = [t for t in ranked if bycat.get(t, {}).get("pains", 0) >= max(bycat.get(t, {}).values(), default=0)][:3] or ranked[:3]
    swipe = a["swipe"]
    proof = [t for t, _ in a["matched_terms"].get("testimonials", [])][:5]
    objections = [o for o, _ in a["objections"]][:4]

    if ranked:
        lines.append(f"**Lead with the #1 topic ({ranked[0]}).** Open the page on what they talk about most ({a['topics']['posts_mentioning_pct'][ranked[0]]}% of posts), not on the portfolio.")
    if pain_topics:
        pains = [TOPIC_PHRASES.get(t, (t, t))[0] for t in pain_topics]
        promises = [TOPIC_PHRASES.get(t, (t, t))[1] for t in pain_topics]
        lines.append(f"**Pain hook:** \"{service.capitalize()} without {', '.join(pains[:-1])}{' or ' if len(pains) > 1 else ''}{pains[-1]}.\"")
        lines.append(f"**Promise stack:** {'; '.join(promises)}.")
    fear_q = swipe["fears"][0]["quote"] if swipe.get("fears") else ""
    pain_rows = [r for r in swipe.get("pains", []) if r["quote"] != fear_q] or swipe.get("pains", [])
    if pain_rows:
        lines.append(f"**Agitate in their words:** open with the top pain line verbatim - “{_short(pain_rows[0]['quote'])}” - then name the gap it describes.")
    if swipe.get("fears"):
        lines.append(f"**Risk reversal:** the fear to answer head-on is “{_short(swipe['fears'][0]['quote'])}”. Counter it with a fixed-fee scope, a written schedule with milestone payments, or a guarantee.")
    if swipe.get("hopes"):
        lines.append(f"**Core promise:** what they are actually seeking - “{_short(swipe['hopes'][0]['quote'])}”. Make this the sub-headline.")
    if swipe.get("dreams"):
        lines.append(f"**After-picture:** paint this in the first 10 seconds of any video or landing page - “{_short(swipe['dreams'][0]['quote'])}”.")
    if proof:
        lines.append(f"**Proof language to echo:** {', '.join(f'“{p}”' for p in proof)} - the exact words delighted clients reach for; use them as testimonial headlines and in the guarantee.")
    if objections:
        lines.append(f"**Pre-empt objections / alternatives tried:** {', '.join(objections)} - address each in an FAQ before the call-to-action.")
    n_mid = len(a["top_posts"]["mid_star_3_4"])
    lines.append("**Godfather offer test:** build an offer that removes the top fear and guarantees the top hope; price it against the cost of the top pain.")
    lines.append(f"**High-value content offer (HVCO) idea for {brand}:** \"The renovation mistakes {n_mid} homeowners wish they'd avoided\" - sourced from the 3-4★ reading list below.")
    return lines


# --- Markdown ----------------------------------------------------------------

def render_markdown(a: Dict, brand: str = "Studio Quattro Design", service: str = "interior design") -> str:
    o, s, c, cp, t = a["overview"], a["stars"], a["categories"], a["complaint_vs_praise"], a["topics"]
    md: List[str] = []
    md.append(f"# {brand} - Halo Strategy Research Brief\n")
    md.append(f"_Generated {a['meta']['generated']} - {o['posts']} posts across {', '.join(f'{k} ({v})' for k, v in o['by_source'].items())}._\n")
    if a["meta"].get("is_fixture"):
        md.append("> **Note:** this run used the bundled **synthetic fixture dataset** (illustrative, not real customers). Run `mine` or `import` against live sources for production numbers.\n")
    md.append("Framework: Sabri Suby's Halo Strategy - mine where the dream buyer already talks, capture their exact words, sort into **Pains, Fears, Hopes, Dreams, Testimonials**, and weight toward **3-4★ reviews** and the **longest posts**.\n")

    # Executive numbers
    md.append("## 1. Numbers at a glance\n")
    rows = [
        ["Posts analysed", o["posts"]],
        ["Total words", o["total_words"]],
        ["Avg / median words per post", f"{o['avg_words']} / {o['median_words']}"],
        ["Long-post threshold (p75)", f"{a['top_posts']['long_post_threshold_words']} words ({a['top_posts']['long_posts_count']} posts)"],
        ["Rated reviews", s["rated_posts"]],
        ["Average rating", s["avg_rating"]],
        ["3-4★ share of rated reviews", f"{s['share_3_4_of_rated']}%"],
        ["Emotional intensity (intensifiers / 100 words)", a["correlations"]["intensity_mean"]],
        ["First-person density (/100 words)", a["correlations"]["first_person_mean"]],
    ]
    md.append(_table(["Metric", "Value"], rows) + "\n")

    md.append("### Star distribution\n")
    rows = [[f"{k}★", s["distribution"][k], f"{s['distribution_pct'][k]}%", _bar(s["distribution_pct"][k]), s["avg_words_by_star"].get(k, "-")] for k in "54321"]
    md.append(_table(["Stars", "Reviews", "Share", "", "Avg words"], rows) + "\n")
    md.append("### Why the middle matters\n")
    rows = []
    for band in ("5-star", "3-4 star", "1-2 star", "unrated"):
        if band in cp:
            rows.append([band, cp[band]["complaint_signal"], cp[band]["praise_signal"], cp[band]["complaint_to_praise"], f"{cp[band]['both_present_pct']}%", s["avg_words_by_band"].get(band, "-")])
    md.append(_table(["Band", "Complaint signal", "Praise signal", "Complaint:praise", "Both present", "Avg words"], rows))
    md.append("\n_3-4★ reviews carry both praise and complaint in the same post far more often - that is the \"what I wanted vs what I got\" gap the Halo Strategy mines for._\n")

    # Halo buckets
    md.append("## 2. The five Halo buckets\n")
    rows = []
    for cat in HALO_CATEGORIES:
        rows.append([CATEGORY_LABELS[cat].split(" (")[0], c["posts_with_signal"][cat], f"{c['posts_with_signal_pct'][cat]}%", c["primary_counts"].get(cat, 0), c["hits_per_1000_words"][cat], f"{c['halo_weighted_share_pct'][cat]}%", _bar(c["halo_weighted_share_pct"][cat])])
    md.append(_table(["Bucket", "Posts w/ signal", "%", "Primary", "Hits/1k words", "Halo-weighted share", ""], rows) + "\n")
    md.append("### Density by star band (mean hits per 100 words)\n")
    bands = list(c["mean_density_by_band"].keys())
    rows = [[CATEGORY_LABELS[cat].split(" (")[0]] + [c["mean_density_by_band"][b][cat] for b in bands] for cat in HALO_CATEGORIES]
    md.append(_table(["Bucket"] + [f"{b} (n={c['mean_density_by_band'][b]['n']})" for b in bands], rows) + "\n")

    # Topics
    md.append("## 3. What they talk about (topics)\n")
    rows = []
    for topic, hits in t["sentence_hits"].items():
        bycat = t["by_primary_category"].get(topic, {})
        lead = max(bycat, key=bycat.get) if bycat else "-"
        rows.append([topic, hits, f"{t['posts_mentioning_pct'][topic]}%", lead])
    md.append(_table(["Topic", "Sentence hits", "Posts mentioning", "Dominant bucket"], rows) + "\n")

    # Correlations
    cr = a["correlations"]
    md.append("## 4. Correlations (Pearson r)\n")
    rows = [
        ["Post length ↔ total emotional signal", cr["length_vs_total_signal"]],
        ["Post length ↔ pain density", cr["length_vs_pain_density"]],
        ["Post length ↔ dream density", cr["length_vs_dream_density"]],
        ["Star rating ↔ pain score", cr["rating_vs_pain_score"]],
        ["Star rating ↔ testimonial score", cr["rating_vs_testimonial_score"]],
    ]
    md.append(_table(["Pair", "r"], rows))
    md.append("\n_Positive length↔signal confirms the Halo rule: longer posts are richer. Strongly negative rating↔pain means low stars are mostly venting; look to 3-4★ for balanced detail._\n")

    # Swipe file
    md.append("## 5. Swipe file - their exact words\n")
    md.append("Ranked by quote strength x Halo weight (3-4★ and long posts float up). Use verbatim where possible; the market's language beats the copywriter's.\n")
    for cat in HALO_CATEGORIES:
        md.append(f"### {CATEGORY_LABELS[cat]}\n")
        kw = a["matched_terms"].get(cat, [])
        if kw:
            md.append("Most-used phrases: " + ", ".join(f"**{k}** ({n})" for k, n in kw[:10]) + "\n")
        for row in a["swipe"].get(cat, []):
            md.append(f"- “{_clean(row['quote'])}”  \n  <sub>{_cite(row)}{' - ' + row['url'] if row.get('url') else ''}</sub>")
        md.append("")

    # Objections & triggers
    md.append("## 6. What they've tried & what triggers the search\n")
    md.append("**Objections / alternatives already considered:** " + (", ".join(f"{o} ({n})" for o, n in a["objections"]) or "none detected") + "\n")
    md.append("**Buying triggers (life events):** " + (", ".join(f"{o} ({n})" for o, n in a["triggers"]) or "none detected") + "\n")

    # Reading lists
    md.append("## 7. Priority reading lists\n")
    md.append("### 3-4★ reviews (balanced, most honest) - top by Halo score\n")
    for r in a["top_posts"]["mid_star_3_4"][:10]:
        md.append(f"- **{int(round(r['rating']))}★ · {r['words']} words · halo {r['halo_score']:.2f} · {r['primary']}** - “{_clean(r['quote'], 220)}”{' - ' + r['url'] if r.get('url') else ''}")
    md.append("\n### Longest posts (most invested voices)\n")
    for r in a["top_posts"]["longest"][:10]:
        stars_txt = f"{int(round(r['rating']))}★ · " if r.get("rating") is not None else ""
        md.append(f"- **{stars_txt}{r['words']} words · {r['source']} · {r['primary']}** - “{_clean(r['quote'], 220)}”{' - ' + r['url'] if r.get('url') else ''}")
    md.append("\n### Highest Halo score overall\n")
    for r in a["top_posts"]["by_halo_score"][:10]:
        stars_txt = f"{int(round(r['rating']))}★ · " if r.get("rating") is not None else ""
        md.append(f"- **halo {r['halo_score']:.2f} · {stars_txt}{r['words']} words · {r['source']}** - “{_clean(r['quote'], 220)}”")

    # Keywords
    md.append("\n## 8. Keyword & phrase frequency (from quotable sentences)\n")
    for cat in HALO_CATEGORIES:
        kws = a["keywords"][cat]
        parts = []
        for gram in ("2-gram", "3-gram", "1-gram"):
            if kws.get(gram):
                parts.append(", ".join(f"{g} ({n})" for g, n in kws[gram][:8]))
        if parts:
            md.append(f"- **{cat}:** " + " · ".join(parts))

    # Copy angles
    md.append("\n## 9. Copy angles for the copywriter\n")
    for line in copy_angles(a, brand, service):
        md.append(f"- {line}")
    md.append("\n## 10. Method notes\n")
    md.append("- **Weights:** 3★/4★ x1.5, 2★ x1.1, 1★ x0.9, 5★ x0.8, Reddit x1.0; length on a log curve (capped x3); small boosts for upvotes/comments and emotional intensity.")
    md.append("- **Classification:** sentence-level weighted phrase lexicon (editable in config). Add `--llm` to re-classify with Claude for nuance.")
    md.append("- **Caveats:** lexicon matching is a first pass; read the priority lists yourself - the Halo Strategy is about absorbing the voice, not just counting it.")
    return "\n".join(md) + "\n"


# --- Writers -----------------------------------------------------------------

def write_outputs(a: Dict, scored: Sequence[ScoredPost], out_dir: Path, brand: str, service: str) -> Dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    paths["report_md"] = out_dir / "halo_report.md"
    paths["report_md"].write_text(render_markdown(a, brand, service), encoding="utf-8")
    paths["analysis_json"] = out_dir / "analysis.json"
    paths["analysis_json"].write_text(json.dumps(a, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    paths["scored_csv"] = out_dir / "scored_posts.csv"
    with paths["scored_csv"].open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "source", "kind", "venue", "rating", "star_band", "words", "upvotes", "comments", "halo_score",
                    "star_weight", "length_weight", "primary", *HALO_CATEGORIES, "intensity", "topics", "objections", "triggers", "url", "title", "text"])
        for s in sorted(scored, key=lambda x: x.halo, reverse=True):
            p, cl, wts = s.post, s.cls, s.weights
            w.writerow([p.id, p.source, p.kind, p.venue, p.rating, p.star_band, p.word_count, p.upvotes, p.comments, wts["halo_score"],
                        wts["star_weight"], wts["length_weight"], cl.primary, *[cl.scores[c] for c in HALO_CATEGORIES], cl.intensity,
                        "; ".join(f"{k}:{v}" for k, v in cl.topics.items()), "; ".join(cl.objections), "; ".join(cl.triggers), p.url, p.title, p.text])

    paths["swipe_csv"] = out_dir / "swipe_file.csv"
    with paths["swipe_csv"].open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["category", "rank", "quote", "source", "rating", "star_band", "words", "halo_score", "matched", "url", "post_id"])
        for cat in HALO_CATEGORIES:
            for i, r in enumerate(a["swipe"].get(cat, []), 1):
                w.writerow([cat, i, r["quote"], r["source"], r["rating"], r["star_band"], r["words"], r["halo_score"], "; ".join(r["matched"]), r["url"], r["post_id"]])
    return paths
