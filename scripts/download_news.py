"""Download Alpaca (Benzinga) news headlines into monthly JSONL files.

Read-only: only GET requests to Alpaca's market-data news API.

Usage:
    python scripts/download_news.py --from 2024-01 --to 2024-12
    python scripts/download_news.py --from 2024-06 --to 2024-06 --content   # include full article text

Output: data/raw/news/YYYY-MM.jsonl, one article per line.
A month is written to a .partial file and renamed only once complete, so an
interrupted run simply redoes that month next time; finished months are skipped.
"""

import argparse
import json
import os
import sys
import time
from datetime import date
from pathlib import Path

import requests
from dotenv import load_dotenv

API = "https://data.alpaca.markets/v1beta1/news"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "news"
REQUEST_INTERVAL = 0.35  # seconds between requests; well under Alpaca's rate limit
FIELDS = ("id", "created_at", "updated_at", "symbols", "source", "author", "headline", "summary", "url")


def months(start: str, end: str):
    y, m = map(int, start.split("-"))
    ey, em = map(int, end.split("-"))
    while (y, m) <= (ey, em):
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def fetch(session: requests.Session, params: dict) -> dict:
    for attempt in range(6):
        r = session.get(API, params=params, timeout=30)
        if r.status_code == 429 or r.status_code >= 500:
            wait = 2 ** attempt
            print(f"  HTTP {r.status_code}, retrying in {wait}s", file=sys.stderr)
            time.sleep(wait)
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f"Giving up after repeated errors: {params}")


def download_month(session, y: int, m: int, content: bool) -> int:
    final = OUT / f"{y:04d}-{m:02d}.jsonl"
    if final.exists():
        print(f"{final.name}: already done, skipping")
        return 0
    partial = final.with_suffix(".jsonl.partial")
    nxt = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)
    params = {
        "start": f"{y:04d}-{m:02d}-01T00:00:00Z",
        "end": f"{nxt.isoformat()}T00:00:00Z",
        "sort": "asc",
        "limit": 50,
        "include_content": str(content).lower(),
    }
    count = 0
    with partial.open("w", encoding="utf-8") as f:
        while True:
            page = fetch(session, params)
            for item in page.get("news", []):
                row = {k: item.get(k) for k in FIELDS}
                if content:
                    row["content"] = item.get("content")
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                count += 1
            token = page.get("next_page_token")
            if not token:
                break
            params["page_token"] = token
            if count % 2500 < 50:
                print(f"  {final.stem}: {count} articles so far")
            time.sleep(REQUEST_INTERVAL)
    partial.rename(final)
    print(f"{final.name}: {count} articles")
    return count


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--from", dest="start", required=True, help="first month, YYYY-MM")
    p.add_argument("--to", dest="end", required=True, help="last month, YYYY-MM")
    p.add_argument("--content", action="store_true", help="also save full article text (much larger)")
    a = p.parse_args()

    load_dotenv(ROOT / ".env")
    key, secret = os.getenv("ALPACA_API_KEY_ID"), os.getenv("ALPACA_API_SECRET_KEY")
    if not key or not secret:
        sys.exit("Set ALPACA_API_KEY_ID and ALPACA_API_SECRET_KEY in .env (see .env.example).")

    OUT.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret})

    total = sum(download_month(session, y, m, a.content) for y, m in months(a.start, a.end))
    print(f"Done: {total} new articles in {OUT}")


if __name__ == "__main__":
    main()
