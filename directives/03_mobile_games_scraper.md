# Directive: Mobile Games Scraper

**Goal:** Create the data collector for mobile games across major genres from Google Play and the Apple App Store.

**Inputs:** Refer to `project_plan.md` Section 4.2 (Mobile Games).
**Outputs:** 
1. Create `collectors/mobile_games.py`.

**Rules:**
- Write DRY (Don't Repeat Yourself) code. Import and reuse the `fetch_google_play_top_apps` and `fetch_app_store_top_apps` functions you just built in `collectors/mobile_apps.py`.
- Define the specific game categories (e.g., GAME_ACTION, GAME_CASUAL, GAME_PUZZLE) for Google Play, and use genre ID 6014 for the App Store.
- Create a function `fetch_all_mobile_game_categories()` that loops through these categories, calls the imported functions, and concatenates all results into a single Pandas DataFrame.
- Add a new column called `genre` to the final DataFrame to indicate the specific game category.
- At the bottom of the script, add an `if __name__ == "__main__":` block that fetches just 5 games per category and prints the DataFrame head and total row count to verify it works deterministically.
- Keep previous learnings in mind (Windows cp1252 encoding, `py` command).

**Known edge cases (learned during execution):**
- Game titles from Google Play often contain non-ASCII characters (e.g., `\uff1a` full-width colon). When printing to Windows cp1252 terminals, use `.encode("cp1252", errors="replace").decode("cp1252")` on the string before printing.
- `fetch_google_play_top_apps` was updated to accept an optional `search_queries` parameter to support genre-specific queries (e.g., "top action games android"). This makes reuse DRY without duplicating the fetch loop.
- Google Play search results for game categories can include non-game apps if queries are too broad. Use specific terms like "top action games android" rather than "top free games".
- App Store uses a single `GAME_IOS_COMBINED` genre label since the iTunes RSS endpoint (genre 6014) returns a unified top-games chart, not per-sub-genre breakdowns.
- Run as a module (`py -m collectors.mobile_games`), not as a script, to ensure relative imports from `collectors.mobile_apps` resolve correctly.

**Status: COMPLETE** — `collectors/mobile_games.py` created and verified. 60 rows returned across 7 genres (6 GP + 1 iOS), both platforms confirmed.