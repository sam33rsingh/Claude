import json
from pathlib import Path

from halo_miner.analyze import analyze, score_posts
from halo_miner.classify import HaloClassifier
from halo_miner.cli import FIXTURE, main
from halo_miner.report import render_markdown, write_outputs
from halo_miner.score import HaloWeights
from halo_miner.sources import load_file


def test_fixture_loads_with_ratings_and_reddit():
    posts = load_file(FIXTURE)
    assert len(posts) >= 40
    assert {p.source for p in posts} >= {"google", "yelp", "reddit"}
    assert any(p.rating is None for p in posts) and any(p.rating == 3 for p in posts)


def test_analysis_structure_and_mid_star_emphasis():
    posts = load_file(FIXTURE)
    scored = score_posts(posts, HaloClassifier(), HaloWeights.default())
    a = analyze(scored, is_fixture=True)
    assert a["overview"]["posts"] == len(posts)
    assert sum(a["stars"]["distribution"].values()) == a["stars"]["rated_posts"]
    assert set(a["swipe"]) == {"pains", "fears", "hopes", "dreams", "testimonials"}
    assert all(a["swipe"][c] for c in a["swipe"])
    # 3-4 star band must carry both praise and complaint more often than 5-star.
    cp = a["complaint_vs_praise"]
    assert cp["3-4 star"]["both_present_pct"] > cp["5-star"]["both_present_pct"]
    # Mid-star reading list is really mid-star.
    assert all(r["star_band"] == "3-4 star" for r in a["top_posts"]["mid_star_3_4"])
    # Longest list is sorted by length.
    lens = [r["words"] for r in a["top_posts"]["longest"]]
    assert lens == sorted(lens, reverse=True)
    # Length correlates positively with emotional signal in this corpus.
    assert a["correlations"]["length_vs_total_signal"] > 0.3


def test_report_renders_and_writes(tmp_path: Path):
    posts = load_file(FIXTURE)
    scored = score_posts(posts, HaloClassifier(), HaloWeights.default())
    a = analyze(scored, is_fixture=True)
    md = render_markdown(a)
    assert "Swipe file" in md and "3-4★" in md and "Copy angles" in md
    paths = write_outputs(a, scored, tmp_path, "Studio Quattro Design", "interior design")
    assert all(p.exists() for p in paths.values())
    json.loads(paths["analysis_json"].read_text())


def test_cli_demo_and_import_roundtrip(tmp_path: Path):
    assert main(["demo", "--out", str(tmp_path / "demo")]) == 0
    assert (tmp_path / "demo" / "halo_report.md").exists()
    assert main(["import", str(FIXTURE), "--out", str(tmp_path / "run")]) == 0
    assert main(["analyze", "--in", str(tmp_path / "run" / "posts.jsonl"), "--out", str(tmp_path / "run" / "report")]) == 0
    assert (tmp_path / "run" / "report" / "swipe_file.csv").exists()
