"""Scrape the public contribution calendar (no token, no GraphQL) into data/contributions.json."""
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from theme import USER

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"
URL = f"https://github.com/users/{os.environ.get('PROFILE_USER', USER)}/contributions"


def get_html() -> str:
    last = None
    for attempt in range(4):
        try:
            r = requests.get(URL, headers={"User-Agent": "profile-readme-bot/1.0"}, timeout=30)
            r.raise_for_status()
            return r.text
        except requests.RequestException as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise SystemExit(f"fetch failed: {last}")


def parse(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    # Tooltips ("3 contributions on May 4th.") are keyed by the cell id they describe.
    counts: dict[str, int] = {}
    for tip in soup.find_all("tool-tip"):
        m = re.match(r"\s*(No|\d[\d,]*) contributions?", tip.get_text())
        if m:
            counts[tip.get("for", "")] = 0 if m.group(1) == "No" else int(m.group(1).replace(",", ""))
    days = []
    for td in soup.select("td.ContributionCalendar-day[data-date]"):
        days.append({
            "date": td["data-date"],
            "level": int(td.get("data-level", 0)),
            "count": counts.get(td.get("id", ""), 0),
        })
    days.sort(key=lambda d: d["date"])
    return days


def stats(days: list[dict]) -> dict:
    today = datetime.now(timezone.utc).date()
    by = {d["date"]: d["count"] for d in days}
    total = sum(by.values())

    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)

    # Current streak: walk back from today; an empty *today* doesn't break it yet.
    cur, cursor = 0, today
    if by.get(cursor.isoformat(), 0) == 0:
        cursor -= timedelta(days=1)
    while by.get(cursor.isoformat(), 0) > 0:
        cur += 1
        cursor -= timedelta(days=1)

    best = max(days, key=lambda d: d["count"], default={"date": None, "count": 0})
    months: dict[str, int] = {}
    for d in days:
        months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["count"]
    return {
        "total": total,
        "current_streak": cur,
        "longest_streak": longest,
        "best_day": best,
        "active_days": sum(1 for d in days if d["count"] > 0),
        "months": months,
    }


def main() -> None:
    days = parse(get_html())
    if len(days) < 300:  # a healthy calendar has ~365 cells; fewer means GitHub changed its markup
        sys.exit(f"parsed only {len(days)} day cells; refusing to overwrite data")
    payload = {
        "user": USER,
        "fetched": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "days": days,
        "stats": stats(days),
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    s = payload["stats"]
    print(f"{len(days)} days, {s['total']} contributions, streak {s['current_streak']}/{s['longest_streak']}")


if __name__ == "__main__":
    main()

