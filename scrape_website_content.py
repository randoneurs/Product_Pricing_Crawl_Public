"""
Crawl a telco's official website with JS rendering (Apify's website-content-crawler)
and dump the rendered page text/markdown for later manual parsing of product
name / price / quota / validity details.

Usage:
    export APIFY_API_TOKEN=...
    python scrape_website_content.py <label> <start_url> <include_glob> [max_pages]
"""

import json
import os
import sys

from apify_client import ApifyClient

ACTOR_ID = "apify/website-content-crawler"
OUTPUT_DIR = "output"


def main() -> None:
    if len(sys.argv) not in (4, 5):
        sys.exit("Usage: python scrape_website_content.py <label> <start_url> <include_glob> [max_pages]")
    label = sys.argv[1]
    start_url = sys.argv[2]
    include_glob = sys.argv[3]
    max_pages = int(sys.argv[4]) if len(sys.argv) == 5 else 20

    token = os.environ.get("APIFY_API_TOKEN")
    if not token:
        sys.exit("APIFY_API_TOKEN environment variable is not set.")

    client = ApifyClient(token)

    print(f"[{label}] Crawling {start_url} (include: {include_glob}, max {max_pages} pages)...")
    run = client.actor(ACTOR_ID).call(
        run_input={
            "startUrls": [{"url": start_url}],
            "includeUrlGlobs": [include_glob],
            "crawlerType": "playwright:adaptive",
            "maxCrawlDepth": 5,
            "maxCrawlPages": max_pages,
            "maxResults": max_pages,
            "dynamicContentWaitSecs": 15,
        }
    )
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    print(f"[{label}] Got {len(items)} page(s).")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, f"{label}_website_content.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    print(f"[{label}] Wrote {len(items)} page(s) to {output_path}")


if __name__ == "__main__":
    main()
