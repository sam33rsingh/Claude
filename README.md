# Halo Miner - voice-of-customer research for Studio Quattro Design

A scraper + analyser that applies the **Halo Strategy** from Sabri Suby's *Sell Like Crazy*
to Reddit threads, Yelp reviews and Google reviews about hiring an interior designer.

It collects what prospects and clients say in their own words, sorts every sentence into the
five buckets a copywriter needs - **Pains, Fears, Hopes, Dreams, Testimonials** - and weights
the evidence toward the two most honest sources Suby points at:

* **3- and 4-star reviews** (balanced: "what I wanted vs what I got"), weighted 1.5x
* **The longest posts** (the most emotionally invested writers), weighted on a log curve

The output is a research brief with numerical analysis, a verbatim swipe file, priority
reading lists and first-draft copy angles.

## Quick start

```bash
pip install -e .[yaml,dev]           # requests + pyyaml + pytest
python -m halo_miner demo --out runs/demo        # end-to-end on the bundled synthetic fixture
open runs/demo/halo_report.md
```

Outputs per run:

| File | What it is |
|---|---|
| `halo_report.md` | The research brief (numbers, buckets, topics, correlations, swipe file, reading lists, copy angles) |
| `analysis.json` | Every number in the report, machine-readable |
| `scored_posts.csv` | One row per post with Halo score, star/length weights, bucket scores, topics, objections, triggers |
| `swipe_file.csv` | Verbatim quotes per bucket, ranked, with source, stars, length and URL |

## Mining live sources

```bash
cp config.example.yaml config.yaml    # edit subreddits, queries, businesses
halo-miner mine --config config.yaml --out runs/$(date +%F)
halo-miner import google_reviews_export.csv --source google --out runs/$(date +%F)
halo-miner analyze --in runs/$(date +%F)/posts.jsonl --out runs/$(date +%F)/report --config config.yaml
```

### Reddit (free, no key)
Uses Reddit's public JSON endpoints: subreddit search per query, plus comment threads for the
most-discussed posts (long comments are often the best material). Unauthenticated access is
throttled to ~10 requests/minute, so the default delay is 6 s. Create a free "script" app and
set `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` for OAuth and ~10x throughput.

### Yelp
* **Fusion API** (`YELP_API_KEY`, free): finds businesses by term + location, but returns only
  3 short excerpts per business. Good for discovery, thin for depth.
* **Business page JSON-LD** (`html: true`): reads the schema.org reviews embedded in public
  business pages, 10 per page. Yelp's Terms of Service restrict automated access, so this is
  off by default. Prefer a licensed export (Outscraper, Apify, etc.) and `halo-miner import`.

### Google reviews
* **Places API (New)** (`GOOGLE_PLACES_API_KEY`): official, cheap, max 5 reviews per place.
* **SerpApi** (`SERPAPI_KEY`, `engine=google_maps_reviews`): paginates through all reviews for a
  place by `place_id`/`data_id`. Paid, but the sanctioned route to depth.
* Or export from Google Business Profile / a review tool and `halo-miner import`.

### Import anything
`halo-miner import file.csv|json|jsonl` maps columns loosely (`review`, `Review Text`,
`reviewBody`, `stars`, `rating`, `date`, `author`, `url`, `business`...). Exports from most
review tools work without editing.

## How the analysis works

1. **Classify** - each post is split into sentences; each sentence is scored against a weighted
   phrase lexicon per bucket (`halo_miner/lexicon.py`, extendable in `config.yaml`). The best
   sentence per bucket becomes the swipe-file quote. Topics (budget, communication, timeline,
   trust, style, process stress, contractors, function, designer value), objections / things
   already tried (DIY, Pinterest, e-design, hourly vs flat fee) and buying triggers (new house,
   baby, empty nest, inheritance, WFH) are tagged alongside.
2. **Weight** - `halo_score = star_weight x length_weight x engagement x intensity x signal`
   with 3★/4★ = 1.5, 2★ = 1.1, 1★ = 0.9, 5★ = 0.8, Reddit = 1.0, and
   `length_weight = 1 + ln(1 + words/120)` capped at 3.
3. **Analyse** - star distribution and average length per star, complaint-vs-praise ratio per
   band (3-4★ posts contain *both* far more often), bucket counts / hits per 1,000 words /
   Halo-weighted share, bucket density by star band, topic x bucket matrix, n-gram frequency,
   Pearson correlations (length ↔ emotional signal, rating ↔ pain, rating ↔ praise), and three
   priority reading lists: top 3-4★ by Halo score, longest posts, highest Halo score overall.
4. **Report** - Markdown brief with the swipe file and copy angles (pain hook, risk reversal,
   after-picture, proof phrases to echo, objections to pre-empt, Godfather offer / HVCO prompts).

### Optional Claude refinement (`--llm`)
`pip install anthropic`, set `ANTHROPIC_API_KEY` (or `ant auth login`), then add `--llm` to
`analyze`/`demo`. Posts are sent in batches to `claude-opus-5-5` with a structured-output
schema; it scores each bucket 0-10, pulls one verbatim quote per bucket and writes a one-line
dream-buyer note per post. Scores merge with the lexicon result (max of the two), so the
deterministic baseline is never lost. Server-side refusal fallback is enabled by default.

## Development

```bash
pytest -q
```

Tests cover the classifier, the 3-4★ and length weighting rules, every source parser
(Reddit listing/comments, Yelp Fusion + JSON-LD, Google Places + SerpApi, CSV aliases),
and the CLI end to end. `fixtures/sample_reviews.csv` is synthetic.

## Notes and caveats

* Live scraping of Reddit, Yelp and Google was **not** run in the environment that built this
  (outbound access to those hosts is blocked there). The source code paths are unit-tested on
  captured response shapes; run `mine` locally for real data.
* Lexicon matching is a first pass; read the priority lists yourself. The Halo Strategy is about
  absorbing the market's voice, not just counting it.
* Respect each platform's terms. Keep delays polite, prefer official APIs and licensed exports.
