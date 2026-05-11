"""
collectors/pc_games.py — PC games data collector.

Sources:
  - Steam Web API  : Featured categories endpoint for top sellers (no auth needed).
                     App details endpoint for metadata per game.
  - SteamSpy       : Supplementary genre tags. Gracefully degraded — if it
                     fails for any reason, the row is still kept with empty tags.

Rate limiting:
  - Steam App Details API: ~200 requests / 5 minutes enforced server-side.
    A time.sleep(1) delay between detail calls keeps us well under this limit.
  - SteamSpy is an unofficial API with no published rate limit; 1s delay is used.

Output schema (normalized to match existing project schema):
    app_id, title, platform, rank, rating, genre, reviews, installs,
    category, fetched_at
    + supplementary: price_usd, release_date, steamspy_tags
"""

import time
import requests
import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STEAM_FEATURED_URL  = "https://store.steampowered.com/api/featuredcategories/"
STEAM_DETAILS_URL   = "https://store.steampowered.com/api/appdetails"
STEAMSPY_URL        = "https://steamspy.com/api.php"

_HEADERS = {
    "User-Agent": "MarketTrendBot/1.0 (academic research project)",
    "Accept-Language": "en-US,en;q=0.9",
}

_REQUEST_TIMEOUT = 15   # seconds
_RATE_LIMIT_DELAY = 1   # seconds between Steam detail requests


# ---------------------------------------------------------------------------
# Steam: top sellers list
# ---------------------------------------------------------------------------

def fetch_steam_top_sellers(count: int = 50) -> pd.DataFrame:
    """
    Fetch top-selling games from the Steam featured categories endpoint.

    Returns a lightweight DataFrame with app_id, title, rank, and platform.
    Call fetch_steam_app_details() to enrich with metadata.

    Parameters
    ----------
    count : int — Max number of results to return (capped by Steam response size).

    Returns
    -------
    pd.DataFrame with columns: app_id, title, rank, platform, fetched_at
    """
    try:
        resp = requests.get(STEAM_FEATURED_URL, headers=_HEADERS, timeout=_REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        print(f"[WARN] Steam featured categories fetch failed: {exc}")
        return pd.DataFrame(columns=["app_id", "title", "rank", "platform", "fetched_at"])

    items = data.get("top_sellers", {}).get("items", [])
    records = []
    for i, item in enumerate(items[:count]):
        records.append({
            "app_id":     str(item.get("id", "")),
            "title":      item.get("name", ""),
            "rank":       i + 1,
            "platform":   "pc_steam",
            "fetched_at": pd.Timestamp.now(),
        })

    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Steam: per-app metadata
# ---------------------------------------------------------------------------

def fetch_steam_app_details(app_id: str | int) -> dict:
    """
    Fetch detailed metadata for a single Steam app.

    Parameters
    ----------
    app_id : str | int — Steam application ID.

    Returns
    -------
    dict with keys: genres, price_usd, release_date, rating (metacritic),
                    reviews (0 — not available via this endpoint)
    Empty dict on failure (graceful degradation).
    """
    _EMPTY = {
        "genres": [],
        "price_usd": 0.0,
        "release_date": "",
        "rating": 0,
        "reviews": 0,
    }

    try:
        resp = requests.get(
            STEAM_DETAILS_URL,
            params={"appids": app_id, "cc": "us", "l": "en"},
            headers=_HEADERS,
            timeout=_REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        payload = resp.json().get(str(app_id), {})
    except Exception as exc:
        print(f"[WARN] Steam app details failed for {app_id}: {exc}")
        return _EMPTY

    if not payload.get("success"):
        return _EMPTY

    data = payload.get("data", {})
    genres = [g.get("description", "") for g in data.get("genres", [])]
    price_raw = data.get("price_overview", {}).get("final", 0)

    return {
        "genres":       genres,
        "price_usd":    round(price_raw / 100, 2),
        "release_date": data.get("release_date", {}).get("date", ""),
        "rating":       data.get("metacritic", {}).get("score", 0) or 0,
        "reviews":      0,   # not available from appdetails endpoint
    }


# ---------------------------------------------------------------------------
# SteamSpy: supplementary genre tags
# ---------------------------------------------------------------------------

def get_steamspy_tags(app_id: str | int) -> list[str]:
    """
    Fetch the top 5 genre tags for an app from SteamSpy (supplementary).

    Degrades gracefully — always returns a list (empty on failure).

    Parameters
    ----------
    app_id : str | int — Steam application ID.

    Returns
    -------
    list[str] — Up to 5 tag strings, e.g. ['Action', 'RPG', 'Multiplayer']
    """
    try:
        resp = requests.get(
            STEAMSPY_URL,
            params={"request": "appdetails", "appid": app_id},
            headers=_HEADERS,
            timeout=_REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        tags = list(resp.json().get("tags", {}).keys())
        return tags[:5]
    except Exception:
        return []   # SteamSpy is supplementary — never crash on failure


# ---------------------------------------------------------------------------
# Combined collector
# ---------------------------------------------------------------------------

def fetch_pc_games_with_details(count: int = 50, country: str = "us") -> pd.DataFrame:
    """
    Fetch top Steam sellers and enrich each with app details + SteamSpy tags.

    Applies rate limiting between Steam API calls to stay under the 200 req/5min
    limit. SteamSpy tags are fetched with the same delay.

    Parameters
    ----------
    count   : int — Number of top sellers to collect.
    country : str — Unused here (Steam API is globally US-defaulted), kept for
                    schema consistency with other collectors.

    Returns
    -------
    pd.DataFrame with full normalized schema.
    """
    top_df = fetch_steam_top_sellers(count=count)
    if top_df.empty:
        return top_df

    enriched = []
    for _, row in top_df.iterrows():
        app_id = row["app_id"]
        print(f"  [Steam] Fetching details for app_id={app_id} ({row['title']}) ...")

        details = fetch_steam_app_details(app_id)
        time.sleep(_RATE_LIMIT_DELAY)           # CRITICAL: respect Steam rate limit

        steamspy_tags = get_steamspy_tags(app_id)
        time.sleep(_RATE_LIMIT_DELAY)           # polite delay for SteamSpy too

        enriched.append({
            "app_id":        app_id,
            "title":         row["title"],
            "platform":      "pc_steam",
            "rank":          row["rank"],
            "rating":        details["rating"],
            "genre":         ", ".join(details["genres"]) if details["genres"]
                             else ", ".join(steamspy_tags),   # fallback to tags
            "reviews":       details["reviews"],
            "installs":      "N/A",              # Steam does not publish install counts
            "category":      "PC_GAME",
            "price_usd":     details["price_usd"],
            "release_date":  details["release_date"],
            "steamspy_tags": steamspy_tags,
            "fetched_at":    row["fetched_at"],
        })

    return pd.DataFrame(enriched)


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Fetching top 5 Steam games (with details + SteamSpy) ...")
    print("Note: 2s delay per game due to rate limiting.\n")

    df = fetch_pc_games_with_details(count=5)

    if df.empty:
        print("[ERROR] No data returned.")
    else:
        display_cols = ["rank", "title", "genre", "rating", "price_usd", "platform"]
        output = df[display_cols].to_string(index=False)
        # cp1252-safe print for Windows terminals
        print(output.encode("cp1252", errors="replace").decode("cp1252"))
        print()
        print(f"Total rows : {len(df)}")
        print(f"Columns    : {list(df.columns)}")
