# Directive: Agent Tool Registry (Section 6.1)

**Goal:** Create a centralized registry where our scrapers and analysis functions are wrapped as LangChain Tools.

**Inputs:** Refer to `project_plan.md` Section 6.1.
**Outputs:** 1. Create `agent/tools.py`.

**Rules:**
- **Standardization:** Every tool must use the `@tool` decorator from `langchain.tools`.
- **Tool Definitions:** Implement wrappers for the following:
    - `collect_mobile_app_data`: Calls `mobile_apps.py` functions and saves snapshots.
    - `collect_mobile_game_data`: Calls `mobile_games.py` and saves snapshots.
    - `collect_pc_game_data`: Calls `pc_games.py` and saves snapshots.
    - `compute_category_trends`: Takes a category name, loads snapshots from `analysis/snapshot.py`, and calls `analysis/trend_score.py`.
    - `get_community_sentiment`: Calls `reddit_sentiment.py`.
- **Docstrings are Mandatory:** Each tool MUST have a detailed docstring (e.g., "Use this tool to fetch live rankings for PC games from Steam"). The LLM uses these docstrings to decide which tool to pick.
- **Data Flow:** Tools should return a string summary of what they did (e.g., "Successfully collected 50 apps and saved to DB") to keep the agent's context window clean.
- **Import Handling:** Ensure proper relative imports (e.g., `from collectors import mobile_apps`).

**Known edge cases (learned during execution):**
- Dependency Resolution: The project now uses **Python 3.11.9** as recommended. The `app-store-scraper` package was removed from `requirements.txt` because its strict `urllib3<1.26` requirement conflicted with modern packages like `gradio`. Since `mobile_apps.py` already implements direct RSS fetching, this package was redundant.
- Virtual Environment: All tools and scrapers should be run within the established `venv` to ensure stable library versions (Pandas 2.2.2, LangChain 0.2.16, etc.).
- Missing Abstractions: The directive assumed `analysis/snapshot.py` existed, but it had to be created from the `project_plan.md` definitions to support the `load_snapshot` and `save_snapshot` calls within the tools.
- Circular Imports: To avoid potential circular imports between collectors and tools, absolute imports from the project root were used, and the root was added to `sys.path`.

**Status: COMPLETE** — `agent/tools.py` created and LangChain tools registry established. `analysis/snapshot.py` created to support data persistence within the tools.