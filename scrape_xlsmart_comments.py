"""
Scrape comments from @xlsmart's Instagram posts published in the last 30 days,
using the apify/instagram-scraper actor, and write them to a CSV file.

Usage:
    export APIFY_API_TOKEN=...
    python scrape_xlsmart_comments.py
"""

import csv
import os
import sys
from datetime import date, timedelta

from apify_client import ApifyClient

ACTOR_ID = "apify/instagram-scraper"
PROFILE_URL = "https://www.instagram.com/xlsmart/"
COMMENTS_PER_POST_LIMIT = 100
DAYS_BACK = 30
OUTPUT_DIR = "output"


def fetch_posts(client: ApifyClient, since_date: date) -> list[dict]:
    run = client.actor(ACTOR_ID).call(
        run_input={
            "directUrls": [PROFILE_URL],
            "resultsType": "posts",
            "onlyPostsNewerThan": since_date.isoformat(),
            "resultsLimit": 200,
        }
    )
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    posts = []
    for item in items:
        url = item.get("url")
        if not url:
            continue
        posts.append(
            {
                "post_url": url,
                "post_timestamp": item.get("timestamp", ""),
                "post_caption": item.get("caption", ""),
            }
        )
    return posts


def fetch_comments(client: ApifyClient, post_url: str) -> list[dict]:
    run = client.actor(ACTOR_ID).call(
        run_input={
            "directUrls": [post_url],
            "resultsType": "comments",
            "resultsLimit": COMMENTS_PER_POST_LIMIT,
        }
    )
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    comments = []
    for item in items:
        comments.append(
            {
                "post_url": post_url,
                "comment_id": item.get("id", ""),
                "comment_text": item.get("text", ""),
                "comment_owner_username": item.get("ownerUsername", ""),
                "comment_timestamp": item.get("timestamp", ""),
                "comment_likes_count": item.get("likesCount", ""),
            }
        )
    return comments


def write_csv(posts: list[dict], comments: list[dict], output_path: str) -> None:
    post_by_url = {p["post_url"]: p for p in posts}
    fieldnames = [
        "post_url",
        "post_timestamp",
        "post_caption",
        "comment_id",
        "comment_text",
        "comment_owner_username",
        "comment_timestamp",
        "comment_likes_count",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for comment in comments:
            post = post_by_url.get(comment["post_url"], {})
            writer.writerow(
                {
                    "post_url": comment["post_url"],
                    "post_timestamp": post.get("post_timestamp", ""),
                    "post_caption": post.get("post_caption", ""),
                    "comment_id": comment["comment_id"],
                    "comment_text": comment["comment_text"],
                    "comment_owner_username": comment["comment_owner_username"],
                    "comment_timestamp": comment["comment_timestamp"],
                    "comment_likes_count": comment["comment_likes_count"],
                }
            )


def main() -> None:
    token = os.environ.get("APIFY_API_TOKEN")
    if not token:
        sys.exit("APIFY_API_TOKEN environment variable is not set.")

    end_date = date.today()
    start_date = end_date - timedelta(days=DAYS_BACK)

    client = ApifyClient(token)

    print(f"Fetching posts from {start_date} to {end_date}...")
    posts = fetch_posts(client, start_date)
    print(f"Found {len(posts)} post(s).")

    if not posts:
        print("No posts found in the given date range; nothing to scrape comments for.")
        return

    all_comments = []
    for i, post in enumerate(posts, start=1):
        print(f"Fetching comments for post {i}/{len(posts)}: {post['post_url']}")
        all_comments.extend(fetch_comments(client, post["post_url"]))
    print(f"Found {len(all_comments)} comment(s) total.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(
        OUTPUT_DIR, f"xlsmart_comments_{start_date.isoformat()}_{end_date.isoformat()}.csv"
    )
    write_csv(posts, all_comments, output_path)
    print(f"Wrote {len(all_comments)} comment(s) across {len(posts)} post(s) to {output_path}")


if __name__ == "__main__":
    main()
