# Directive: Mobile Apps Scraper

**Goal:** Create the data collector for mobile applications from Google Play and the Apple App Store.

**Inputs:** Refer to `project_plan.md` Section 4.1 (Mobile Apps).
**Outputs:** 
1. Create `collectors/mobile_apps.py`.

**Rules:**
- Implement `fetch_google_play_top_apps` and `fetch_app_store_top_apps` functions using `google-play-scraper` and `app-store-scraper`.
- Both functions MUST return normalized Pandas DataFrames with identical schemas (`app_id`, `title`, `category`, `rating`, `reviews`, `platform`, `rank`, `fetched_at`).
- Remember previous learnings: Use `py` for execution and avoid Unicode emojis in print statements due to Windows cp1252 encoding limits.
- At the bottom of the script, add an `if __name__ == "__main__":` block that fetches just the top 5 apps from each store and prints the DataFrame heads to verify it works deterministically.

**Known edge cases (learned during execution):**
- `google-play-scraper==1.2.7` removed `top_charts()` — it no longer exists. Use `search()` with broad queries ("top free apps") as a practical substitute. The `search()` function surfaces highly-rated/downloaded apps that closely mirror chart data.
- `app-store-scraper==0.3.5` is broken on Python 3.14 — it requires `requests==2.23.0` and `urllib3<1.26`, which conflict with modern Python. Use the **Apple iTunes RSS feed directly** (`https://itunes.apple.com/{country}/rss/topfreeapplications/limit={count}/genre={genre}/json`) — same data, no auth required.
- `pandas==2.2.2` has no pre-built wheel for Python 3.14 — pip installed `pandas==3.0.2` (the compatible wheel) instead. Pin `pandas` without a version in requirements.txt for Python 3.14+ environments.
- iTunes RSS does not include review counts — `reviews` will always be 0 for iOS rows.
- Schema column `installs` will be `"N/A"` for iOS (App Store does not expose install counts).
- After the broken `app-store-scraper` install downgrades requests/urllib3, restore them with: `py -m pip install --upgrade requests urllib3`

**Status: COMPLETE** — `collectors/mobile_apps.py` created and verified. Both collectors return live data with matching schemas (confirmed `Schemas match: True`).