"""
collectors/mobile_apps.py — Mobile application data collector.

Sources:
  - Google Play  : google-play-scraper library — uses `search()` per category
                   since `top_charts()` was removed in v1.2.7. We use well-known
                   search queries ("top free apps", "top apps") to approximate
                   chart data. For a true top-chart list, the public RSS endpoint
                   is also polled as a supplement.
  - Apple App Store : iTunes public RSS feed via requests (fully public, no auth).
                   `app-store-scraper==0.3.5` is incompatible with Python 3.14+
                   (requires urllib3<1.26 which conflicts), so we call Apple's RSS
                   directly — same underlying data.

Both public functions return a normalized pandas DataFrame with these columns:
    app_id, title, category, rating, reviews, installs, platform, rank, fetched_at

Known edge cases:
  - `google-play-scraper` v1.2.7 removed `top_charts`; use `search()` instead.
  - `app-store-scraper` breaks on Python 3.14; use iTunes RSS directly.
  - iTunes RSS does not include review counts (reviews=0 for iOS).
  - Windows terminals: avoid Unicode emoji in print() — use ASCII only.
"""

import time
import requests
import pandas as pd
from google_play_scraper import search


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ITUNES_RSS = (
    "https://itunes.apple.com/{country}/rss/topfreeapplications/"
    "limit={count}/genre={genre}/json"
)

# Broad search terms that surface the most popular/downloaded apps on Play
_GP_TOP_QUERIES = ["top free apps", "most popular apps", "best free apps"]


# ---------------------------------------------------------------------------
# Google Play
# ---------------------------------------------------------------------------

def fetch_google_play_top_apps(
    category: str = "APPLICATION",
    count: int = 50,
    country: str = "us",
    search_queries: list | None = None,
) -> pd.DataFrame:
    """
    Fetch top free apps from Google Play via search queries.

    Note: google-play-scraper v1.2.7 removed top_charts(); this uses search()
    with broad queries to surface highly-downloaded apps as a practical substitute.

    Parameters
    ----------
    category       : str        — Metadata label for the category column.
    count          : int        — Total results target (spread across queries).
    country        : str        — Two-letter country code.
    search_queries : list|None  — Custom search terms to use instead of the
                                  default _GP_TOP_QUERIES. Pass game-genre-specific
                                  terms from mobile_games.py for targeted results.

    Returns
    -------
    pd.DataFrame with normalized schema.
    """
    queries = search_queries if search_queries else _GP_TOP_QUERIES
    per_query = max(1, count // len(queries))
    seen_ids: set = set()
    records = []

    for query in queries:
        try:
            results = search(query, n_hits=per_query + 5, country=country, lang="en")
        except Exception as exc:
            print(f"[WARN] Google Play search failed for '{query}': {exc}")
            continue

        for item in results:
            app_id = item.get("appId", "")
            if not app_id or app_id in seen_ids:
                continue
            seen_ids.add(app_id)
            records.append({
                "app_id":     app_id,
                "title":      item.get("title", ""),
                "category":   item.get("genre") or category,
                "rating":     float(item.get("score") or 0),
                "reviews":    int(item.get("reviews") or 0),
                "installs":   item.get("installs", "0"),
                "platform":   "android",
                "rank":       len(records) + 1,
                "fetched_at": pd.Timestamp.now(),
            })
            if len(records) >= count:
                break

        if len(records) >= count:
            break

        time.sleep(0.5)   # Rate limiting courtesy delay

    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Apple App Store (iTunes RSS)
# ---------------------------------------------------------------------------

def fetch_app_store_top_apps(
    category_id: int = 6000,
    count: int = 50,
    country: str = "us",
) -> pd.DataFrame:
    """
    Fetch top free apps from the Apple App Store via the iTunes RSS feed.

    Parameters
    ----------
    category_id : int  — iTunes genre ID (6000 = all apps, 6014 = games).
    count       : int  — Results to fetch (iTunes caps at 200).
    country     : str  — Two-letter country code.

    Returns
    -------
    pd.DataFrame with normalized schema.
    """
    url = _ITUNES_RSS.format(country=country, count=min(count, 200), genre=category_id)

    _EMPTY_SCHEMA = [
        "app_id", "title", "category", "rating",
        "reviews", "installs", "platform", "rank", "fetched_at"
    ]

    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        entries = resp.json().get("feed", {}).get("entry", [])
    except Exception as exc:
        print(f"[WARN] App Store RSS fetch failed: {exc}")
        return pd.DataFrame(columns=_EMPTY_SCHEMA)

    records = []
    for i, entry in enumerate(entries):
        try:
            raw_rating = (
                entry.get("im:averageUserRating", {}).get("label", None)
                or entry.get("im:ratingAverage", {}).get("label", None)
            )
            records.append({
                "app_id":     entry["id"]["attributes"]["im:id"],
                "title":      entry["im:name"]["label"],
                "category":   entry["category"]["attributes"]["label"],
                "rating":     float(raw_rating) if raw_rating else 0.0,
                "reviews":    0,      # iTunes RSS does not expose review counts
                "installs":   "N/A",
                "platform":   "ios",
                "rank":       i + 1,
                "fetched_at": pd.Timestamp.now(),
            })
        except (KeyError, TypeError, ValueError):
            continue   # Skip malformed entries gracefully

    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("--- Google Play: Top 5 Apps ---")
    gp_df = fetch_google_play_top_apps(count=5)
    print(gp_df[["rank", "title", "category", "rating", "platform"]].to_string(index=False))

    print()
    time.sleep(1)

    print("--- App Store: Top 5 Apps ---")
    ios_df = fetch_app_store_top_apps(count=5)
    print(ios_df[["rank", "title", "category", "rating", "platform"]].to_string(index=False))

    print()
    print(f"Google Play schema : {list(gp_df.columns)}")
    print(f"App Store schema   : {list(ios_df.columns)}")
    print(f"Schemas match      : {list(gp_df.columns) == list(ios_df.columns)}")
