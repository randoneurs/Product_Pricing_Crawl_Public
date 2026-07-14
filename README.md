# Telco Competitive Intelligence Dashboards

Two self-contained HTML dashboards comparing Telkomsel, Indosat (IOH), and
XLSMART, refreshed daily by a scheduled Claude Code cloud routine.

- `telco_dashboard.html` — Instagram comment sentiment & topic breakdown
- `telco_product_dashboard.html` — product movement, line-up, pricing, and
  product-specific sentiment tracker

## Data sources
- Official Instagram accounts (@telkomsel, @indosat, @xlsmart) — Apify
  `instagram-scraper`, posts + comments
- Official websites, canonical source list (as of 14 Jul 2026):
  - Telkomsel: https://www.telkomsel.com/
  - Indosat (IOH): https://ioh.co.id/ID/home
  - XLSMART: https://www.xlsmart.co.id/id
  Crawled with Apify `website-content-crawler` (JS-rendering; the sites are
  client-rendered SPAs). Prior snapshots (through 14 Jul 2026) were crawled
  from im3.id and xl.co.id instead — the consumer-brand sites linked from
  ioh.co.id/xlsmart.co.id — see dashboard methodology footer for why, and for
  when each source last changed.
- TikTok and X/Twitter were evaluated but are not part of the regular
  pipeline — see `output/` notes and dashboard methodology sections for why.

## Pipeline (run daily)
1. `scrape_ig_comments.py <handle>` — refresh last-30-day IG comments per operator
2. `scrape_website_content.py <label> <start_url> <include_glob>` — refresh
   website product/pricing content. Current canonical invocations:
   - `scrape_website_content.py telkomsel "https://www.telkomsel.com/" "https://www.telkomsel.com/**"`
   - `scrape_website_content.py indosat "https://ioh.co.id/ID/home" "https://ioh.co.id/**"`
   - `scrape_website_content.py xlsmart "https://www.xlsmart.co.id/id" "https://www.xlsmart.co.id/**"`
3. Classify new comments using `CLASSIFICATION_RUBRIC.md`, checking
   `classification_cache.json` first to avoid re-classifying repeats
4. Update the aggregate numbers embedded in both dashboard HTML files
5. Validate JS syntax/runtime before publishing (see below)
6. Commit everything, then publish both HTML files as Artifacts using their
   **existing** URLs (pass `url` explicitly) so links don't change day to day

## Validation before publishing
Since there's no way to visually preview an artifact from here, always run:
```
python3 -c "import json; ..."   # extract <script> body
osascript -l JavaScript -e '...' # new Function() syntax check
```
and a runtime check against a stubbed `document` object (see prior commits
for the stub pattern) before every publish.

## Secrets
`APIFY_API_TOKEN` is required for steps 1–2. It is intentionally not stored in
this repo — it's supplied to the scheduled routine at run time.
