# Halo Miner - voice-of-customer research for Studio Quattro Design

A scraper + analyser that applies the **Halo Strategy** from Sabri Suby's *Sell Like Crazy*
to Reddit threads, Yelp reviews and Google reviews about kitchens, cabinetry, closets and
hiring a designer - the market [Studio Quattro Design](https://studioquattrodesign.com)
serves from its Solana Beach showroom (San Diego & Orange County, Veneta Cucine, Sangiacomo, Kico).

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

### Reddit (free, but OAuth is now required)
Reddit began returning **403 to unauthenticated `.json` requests in late May 2026**, so the
miner uses the official Data API with OAuth. Create a free *script* app at
https://www.reddit.com/prefs/apps and export `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`.
Without them `mine` stops with a clear error instead of silently collecting 403s
(`allow_unauthenticated: true` tries the legacy endpoints anyway; it only works from some
residential IPs). Subreddit search per query plus comment threads for the most-discussed
posts, ~100 requests/minute.

### Yelp
* **Fusion API** (`YELP_API_KEY`, free): finds businesses by term + location, but returns only
  3 short excerpts per business. Good for discovery, thin for depth.
* **Business page JSON-LD** (`html: true`): reads the schema.org reviews embedded in public
  business pages. Yelp fronts its site with DataDome bot protection and its Terms of Service
  restrict automated access, so this is off by default and will often be blocked.
* Studio Quattro's own listing has a handful of reviews: copy them into a CSV and
  `halo-miner import` - faster than any scraper.

### Google reviews
* **Google Business Profile API** - the free, official route to *all* reviews of your **own**
  listing (`accounts.locations.reviews.list`). Save the JSON and `halo-miner import` it; the
  `starRating` enum format is auto-detected.
* **Places API (New)** (`GOOGLE_PLACES_API_KEY`): official, cheap, max 5 reviews per place.
  Fine for finding competitors.
* **SerpApi** (`SERPAPI_KEY`, `engine=google_maps_reviews`): paginates all reviews for a place.
  Paid, reliable.
* **Open-source scrapers** (free, need a desktop with Chrome or Docker):
  [gosom/google-maps-scraper](https://github.com/gosom/google-maps-scraper) (Go, MIT, ~6k stars,
  `-json -extra-reviews` collects up to ~300 reviews per place) and
  [georgekhananaev/google-reviews-scraper-pro](https://github.com/georgekhananaev/google-reviews-scraper-pro)
  (Python, MIT, undetected Chrome, full review text with dates and owner replies). Both output
  JSON that `halo-miner import` recognises automatically.

### Import anything
`halo-miner import file.csv|json|jsonl` first checks for the JSON shapes of known tools
(gosom, google-reviews-scraper-pro, Google Business Profile API, Places API, SerpApi, Yelp
Fusion), then falls back to loose column matching (`review`, `Review Text`, `reviewBody`,
`stars`, `rating`, `date`, `author`, `url`, `business`...). Exports from most review tools
work without editing.

## Which scrapers actually work (checked October 2026)

| Platform | Works | Avoid |
|---|---|---|
| Reddit | Official Data API via OAuth (built in; PRAW-equivalent). Free script app, ~100 req/min. | Any "no API key" scraper built on `.json` endpoints (yars, ScrapiReddit and similar) - they get 403 from servers since May 2026. |
| Google reviews | Business Profile API for your own listing; gosom/google-maps-scraper or google-reviews-scraper-pro for competitors; SerpApi if you want to pay for reliability. | Places API alone for depth (5 reviews max). Tiny repos that funnel you to a paid proxy. |
| Yelp | Fusion API for discovery; manual copy of the few reviews that matter; licensed exports (Outscraper, Apify). | Hobby Selenium scrapers - DataDome blocks them within minutes, and most are unmaintained since 2019-2021. |

Run the browser-based tools from a laptop on a residential connection, keep concurrency at 1,
and respect each site's terms.

## How the analysis works

1. **Classify** - each post is split into sentences; each sentence is scored against a weighted
   phrase lexicon per bucket (`halo_miner/lexicon.py`, extendable in `config.yaml`). The best
   sentence per bucket becomes the swipe-file quote. Topics (budget, communication, timeline,
   trust, style, process stress, contractors, function, designer value), objections / things
   already tried (DIY, Pinterest, e-design, hourly vs flat fee) and buying triggers (new house,
   baby, empty nest, inheritance, WFH) are tagged alongside. A cabinetry layer (particle board,
   lead times, damaged deliveries, showroom selection, handle-less European look) is built in.
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
