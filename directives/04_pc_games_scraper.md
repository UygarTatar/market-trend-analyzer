# Directive: PC Games Scraper

**Goal:** Create the data collector for PC games using the Steam Web API and SteamSpy.

**Inputs:** Refer to `project_plan.md` Section 4.3 (PC Games).
**Outputs:** 
1. Create `collectors/pc_games.py`.

**Rules:**
- Implement `fetch_steam_top_sellers(count=50)` using the Steam featured categories API endpoint.
- Implement `fetch_steam_app_details(app_id)` to get metadata (price, genres, metacritic score).
- Implement `get_steamspy_tags(app_id)` as supplementary data. If SteamSpy fails, degrade gracefully (do not crash).
- **CRITICAL:** The Steam API has rate limits. You MUST implement a delay (e.g., `time.sleep(1)`) between individual app detail requests to avoid HTTP 429 Too Many Requests errors.
- Combine the fetched data into a normalized Pandas DataFrame that matches the existing schema (`app_id`, `title`, `platform`="pc_steam", `rank`, `rating` (metacritic), `genre` (comma-separated if multiple), `fetched_at`).
- At the bottom, add an `if __name__ == "__main__":` block to fetch just the top 5 PC games, handle cp1252 printing securely, and display the DataFrame.
- Remember to use `py -m collectors.pc_games` for execution during your self-testing.

**Known edge cases (learned during execution):**
- Steam `appdetails` returns `"success": false` for some app_ids (DLC, bundles, removed games). Always check `payload.get("success")` and return empty/default dict on failure.
- Metacritic scores (`rating`) will be 0 for most indie/early-access games — this is correct, not a data error. Only ~15% of Steam games have Metacritic entries.
- When `genres` list is empty from the details endpoint (e.g., success=false), fall back to SteamSpy tags for the `genre` column so the field is never blank.
- SteamSpy tags tend to be richer and more descriptive than Steam's own genre list (e.g., "Open World", "Multiplayer" vs "Action").
- The `top_sellers` chart from Steam currently surfaces many early-access/indie titles, not just AAA games. This is normal Steam chart behavior.
- Use `str(app_id)` when keying into the appdetails response — the API returns string keys even when you pass an integer app_id.
- Both Steam detail and SteamSpy calls use `time.sleep(1)` per request = 2s total per game. For 50 games this is ~100 seconds. Plan accordingly.
- Run as: `py -m collectors.pc_games` (module mode required for proper package resolution).

**Status: COMPLETE** — `collectors/pc_games.py` created and verified. 5 games fetched with genres, prices, rate limiting confirmed working (no 429 errors).
