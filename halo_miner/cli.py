"""Command line interface.

    halo-miner mine    --config config.yaml --out runs/today        # scrape sources -> posts.jsonl
    halo-miner import  export.csv --source google --out runs/today  # add an exported review file
    halo-miner analyze --in runs/today/posts.jsonl --out runs/today/report [--llm]
    halo-miner demo    --out runs/demo                              # fixture end-to-end
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import List

from .analyze import analyze, score_posts
from .classify import HaloClassifier
from .config import load_config
from .models import Post
from .report import write_outputs
from .score import HaloWeights
from .sources import GoogleReviewsSource, RedditSource, YelpSource, load_file
from .sources.base import dedupe
from .sources.csv_import import save_jsonl

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "sample_reviews.csv"


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO, format="%(levelname)s %(name)s: %(message)s", stream=sys.stderr)


def cmd_mine(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    out = Path(args.out)
    posts: List[Post] = []
    srcs = cfg["sources"]
    if srcs.get("reddit", {}).get("enabled", True):
        posts.extend(RedditSource().fetch(srcs.get("reddit", {})))
    if srcs.get("yelp", {}).get("enabled"):
        posts.extend(YelpSource().fetch(srcs.get("yelp", {})))
    if srcs.get("google", {}).get("enabled"):
        posts.extend(GoogleReviewsSource().fetch(srcs.get("google", {})))
    existing = out / "posts.jsonl"
    if existing.exists() and not args.fresh:
        posts.extend(load_file(existing))
    posts = dedupe(posts)
    n = save_jsonl(posts, existing)
    print(f"saved {n} posts -> {existing}")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    out = Path(args.out)
    posts = load_file(args.file, default_source=args.source)
    target = out / "posts.jsonl"
    if target.exists():
        posts = dedupe(load_file(target) + posts)
    n = save_jsonl(posts, target)
    print(f"imported {len(posts)} posts ({n} total) -> {target}")
    return 0


def _run_analysis(posts: List[Post], cfg: dict, out: Path, use_llm: bool, is_fixture: bool) -> int:
    if not posts:
        print("no posts to analyse", file=sys.stderr)
        return 1
    classifier = HaloClassifier(cfg.get("lexicon_extra") or None, cfg.get("topics_extra") or None)
    weights = HaloWeights.default(cfg.get("weights"))
    scored = score_posts(posts, classifier, weights)
    if use_llm:
        from . import llm
        touched = llm.merge(scored, llm.classify_batch(scored))
        # Re-weight: emotional signal feeds the halo score.
        from .score import halo_score
        for s in scored:
            s.weights = halo_score(s.post, s.cls, weights)
        print(f"llm: refined {touched}/{len(scored)} posts", file=sys.stderr)
    rep = cfg.get("report", {})
    a = analyze(scored, top_n=int(rep.get("top_n", 15)), swipe_n=int(rep.get("swipe_n", 12)), is_fixture=is_fixture)
    paths = write_outputs(a, scored, out, cfg.get("brand", "Studio Quattro Design"), cfg.get("service", "interior design"))
    for k, p in paths.items():
        print(f"{k:14s} {p}")
    s = a["stars"]
    c = a["categories"]
    print(f"\n{a['overview']['posts']} posts · avg {a['overview']['avg_words']} words · 3-4★ share {s['share_3_4_of_rated']}% · "
          + " · ".join(f"{k} {v}%" for k, v in c["halo_weighted_share_pct"].items()))
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    posts: List[Post] = []
    for f in args.inputs:
        posts.extend(load_file(f))
    return _run_analysis(dedupe(posts), cfg, Path(args.out), args.llm, is_fixture=False)


def cmd_demo(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    posts = load_file(FIXTURE)
    return _run_analysis(posts, cfg, Path(args.out), args.llm, is_fixture=True)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="halo-miner", description="Halo Strategy voice-of-customer miner for Studio Quattro Design")
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("mine", help="scrape configured sources into posts.jsonl")
    m.add_argument("--config", default=None)
    m.add_argument("--out", required=True)
    m.add_argument("--fresh", action="store_true", help="ignore an existing posts.jsonl in --out")
    m.set_defaults(func=cmd_mine)

    i = sub.add_parser("import", help="import a CSV/JSON/JSONL review export")
    i.add_argument("file")
    i.add_argument("--source", default="csv", help="label when the file has no source column (yelp, google, reddit...)")
    i.add_argument("--out", required=True)
    i.set_defaults(func=cmd_import)

    a = sub.add_parser("analyze", help="classify, weight and report")
    a.add_argument("--in", dest="inputs", nargs="+", required=True)
    a.add_argument("--out", required=True)
    a.add_argument("--config", default=None)
    a.add_argument("--llm", action="store_true", help="refine with Claude (needs anthropic + credentials)")
    a.set_defaults(func=cmd_analyze)

    d = sub.add_parser("demo", help="run the whole pipeline on the bundled synthetic fixture")
    d.add_argument("--out", default="runs/demo")
    d.add_argument("--config", default=None)
    d.add_argument("--llm", action="store_true")
    d.set_defaults(func=cmd_demo)
    return p


def main(argv: List[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    _setup_logging(args.verbose)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
