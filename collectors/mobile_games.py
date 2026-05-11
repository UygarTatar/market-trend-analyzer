"""
collectors/mobile_games.py — Mobile games data collector.

Reuses fetch_google_play_top_apps() and fetch_app_store_top_apps() from
mobile_apps.py (DRY). Game-specific search queries are passed per category
so Google Play results are targeted to each genre. The App Store is queried
once with genre ID 6014 (Games) since it returns a unified top-games chart.

Output schema (same as mobile_apps.py, plus `genre` column):
    app_id, title, category, rating, reviews, installs,
    platform, rank, fetched_at, genre
"""

import time
import pandas as pd

from collectors.mobile_apps import (
    fetch_google_play_top_apps,
    fetch_app_store_top_apps,
)


# ---------------------------------------------------------------------------
# Category definitions
# ---------------------------------------------------------------------------

# Google Play game categories mapped to targeted search queries.
# search() is used instead of the removed top_charts(); genre-specific terms
# produce far more accurate results than generic "top free apps" queries.
GOOGLE_PLAY_GAME_CATEGORIES: dict[str, list[str]] = {
    "GAME_ACTION":   ["top action games android", "best action games"],
    "GAME_CASUAL":   ["top casual games android", "best casual games free"],
    "GAME_PUZZLE":   ["top puzzle games android", "best puzzle games free"],
    "GAME_RACING":   ["top racing games android", "best car racing games"],
    "GAME_RPG":      ["top rpg games android", "best role playing games"],
    "GAME_STRATEGY": ["top strategy games android", "best strategy games free"],
}

# Apple App Store: genre 6014 = Games (covers all sub-genres in one chart)
APP_STORE_GAME_CATEGORY_ID = 6014


# ---------------------------------------------------------------------------
# Main collector
# ---------------------------------------------------------------------------

def fetch_all_mobile_game_categories(
    count_per_cat: int = 20,
    country: str = "us",
) -> pd.DataFrame:
    """
    Fetch top games across all major genres from Google Play and App Store.

    Loops over GOOGLE_PLAY_GAME_CATEGORIES, fetching `count_per_cat` games
    per category using genre-specific search queries, then appends one App
    Store batch (top-games chart, genre 6014).

    Parameters
    ----------
    count_per_cat : int  — Games to fetch per Google Play category.
    country       : str  — Two-letter country code.

    Returns
    -------
    pd.DataFrame with all games concatenated, including a `genre` column.
    """
    frames: list[pd.DataFrame] = []

    # --- Google Play: one fetch per genre category ---
    for genre_key, queries in GOOGLE_PLAY_GAME_CATEGORIES.items():
        print(f"  [GP] Fetching {genre_key} ...")
        try:
            df = fetch_google_play_top_apps(
                category=genre_key,
                count=count_per_cat,
                country=country,
                search_queries=queries,    # genre-specific queries (DRY reuse)
            )
            df["genre"] = genre_key
            frames.append(df)
        except Exception as exc:
            print(f"  [WARN] Google Play failed for {genre_key}: {exc}")

        time.sleep(0.5)   # polite delay between category requests

    # --- App Store: single top-games chart fetch ---
    print("  [iOS] Fetching App Store top games (genre 6014) ...")
    try:
        ios_df = fetch_app_store_top_apps(
            category_id=APP_STORE_GAME_CATEGORY_ID,
            count=count_per_cat * len(GOOGLE_PLAY_GAME_CATEGORIES),
            country=country,
        )
        ios_df["genre"] = "GAME_IOS_COMBINED"
        frames.append(ios_df)
    except Exception as exc:
        print(f"  [WARN] App Store games fetch failed: {exc}")

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    return combined


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Fetching 5 games per category ...")
    df = fetch_all_mobile_game_categories(count_per_cat=5)

    print()
    output = df[["genre", "platform", "title", "rating"]].head(20).to_string(index=False)
    print(output.encode("cp1252", errors="replace").decode("cp1252"))
    print()
    print(f"Total rows  : {len(df)}")
    print(f"Genres found: {sorted(df['genre'].unique())}")
    print(f"Platforms   : {sorted(df['platform'].unique())}")
    print(f"Columns     : {list(df.columns)}")
