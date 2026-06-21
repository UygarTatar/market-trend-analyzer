# 🌌 ONYX: Agentic Market Intelligence System
## Practitioner's Notes & Engineering Reference

This document provides developer-level documentation of technical design decisions, engineering trade-offs, algorithms, and troubleshooting steps for the ONYX platform.

---

### 1. Architectural Patterns & Core Decisions

#### 1.1 The 3-Layer Architecture
Pure LLM agents suffer from compound errors: if each tool execution has a 90% success rate, a 5-step agent loop succeeds only 59% of the time. To solve this, ONYX isolates concerns into three layers:
1.  **Directive (`directives/`):** Contains natural-language Markdown files representing SOPs (Standard Operating Procedures). They serve as the system's "source of truth" instructions.
2.  **Orchestration (`agent/`):** LangChain ReAct agent utilizing `gemini-3.1-flash-lite` parses the directives, matches user intent to a tool, and executes it.
3.  **Execution (`collectors/`, `analysis/`, `reporting/`):** Pure, deterministic Python code. It receives parameters from the agent, performs operations (API calls, SQL queries), and returns structured outputs. **No AI decision-making happens here.**

#### 1.2 Model Selection Choice
We chose `gemini-3.1-flash-lite` for the entire system:
*   **Agent Orchestration:** Low latency, high tool-calling precision, and handles parsing errors reliably via `handle_parsing_errors=True`.
*   **Report Generation & Evaluation:** Generates highly structured Markdown report sections while remaining cost-efficient.
*   **Context Efficiency:** Fits the combined prompt, context histories, and raw database strings comfortably.

---

### 2. Ingestion & Data Engineering

#### 2.1 Scraping Public APIs Without Keys
A core constraint of the project was relying purely on free and public resources:
*   **Google Play:** Uses `google-play-scraper`, which requests endpoints directly and parses raw responses without needing a developer account.
*   **Apple App Store:** Rather than scraping the HTML directly, we query the public iTunes RSS Feed JSON endpoints (e.g. `https://itunes.apple.com/us/rss/topfreeapplications/limit=50/genre=6014/json`). This has zero rate limits and responds with rapid JSON structures.
*   **Steam:** Pulls featured categories from the public Steam API. To enrich data with genre and price details, it loops through app IDs with `https://store.steampowered.com/api/appdetails`.
*   **SteamSpy Integration:** SteamSpy is used as a fallback to fetch genre tags (e.g. `https://steamspy.com/api.php?request=appdetails&appid=X`). If SteamSpy rate-limits or fails, the code defaults back to standard Steam genre lists.

#### 2.2 Graceful Degradation (Reddit Sentiment)
PRAW (Python Reddit API Wrapper) is utilized to fetch posts from subreddits like `r/androidgaming`, `r/iosgaming`, and `r/pcgaming`.
*   If `REDDIT_CLIENT_ID` or `REDDIT_CLIENT_SECRET` are not set in the `.env` file, the crawler catches the authorization error and degrades gracefully.
*   Reddit sentiment metrics (upvote ratio, post velocity) default to a neutral baseline of `0.5` rating and empty arrays, allowing the rest of the application to run smoothly without failing.

---

### 3. Mathematics of the Trend Engine

#### 3.1 The Mathematical Trend Score Formula
To compare mobile apps, mobile games, and PC games on equal footing, the engine uses a weighted scoring formula:

$$TrendScore = (W_1 \times NormalizedRank) + (W_2 \times Rating) + (W_3 \times SentimentScore) + (W_4 \times \log_{10}(ReviewCount))$$

Where the weights are defined as:
*   $W_1 = 0.4$ (Rank Velocity - reflects chart momentum)
*   $W_2 = 0.2$ (User Ratings - reflects product quality)
*   $W_3 = 0.3$ (Reddit Sentiment - reflects community buzz)
*   $W_4 = 0.1$ (Review Count log scale - reflects overall popularity)

#### 3.2 Handling Mathematical Edge Cases
*   **Rank Normalization:** In store rankings, $1$ is the best and $100$ is worse. We use $NormalizedRank = \frac{1.0}{\text{rank}}$ (enforced for $\text{rank} > 0$). This correctly scales the top positions exponentially higher.
*   **Log scale on Reviews:** Review counts can range from $0$ to millions. To prevent mega-apps from distorting the metrics, we compute the base-10 logarithm: $\log_{10}(\text{reviews} + 1)$.
*   **Division-by-Zero:** Any division is wrapped in `clip(lower=1)` when comparing historical snapshots to current ones.

---

### 4. Self-Correcting Quality Control Loop

Reports can sometimes omit sections or fail to mention charts. ONYX implements an LLM-in-the-loop self-correction flow in `reporting/revision.py`:

```
           ┌───────────────────────────────┐
           │      Generate Report Text     │
           └───────────────┬───────────────┘
                           │
                           ▼
           ┌───────────────────────────────┐
           │    Gemini flash Evaluator     │
           │  (Grades against 5 criteria)  │
           └───────────────┬───────────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
       Score >= 0.7?               Score < 0.7?
             │                           │
             │                           ▼
             │               ┌───────────────────────┐
             │               │ Inject Feedback       │
             │               │ & Run Revision Loop   │
             │               │ (Max 2 Attempts)      │
             │               └───────────┬───────────┘
             │                           │
             ├───────────────────────────┘
             ▼
     Display Report to UI
```

The evaluator assesses the following criteria (each yielding a $0$ or $1$ score):
1.  All 3 market categories covered.
2.  $\ge 3$ numeric data points included.
3.  Cross-market comparison section present.
4.  Visualization reference included.
5.  Clear conclusion / recommendation provided.

If the combined average score is $< 0.7$ (meaning $<4/5$ criteria passed), the JSON feedback is fed back into the model context, prompting Gemini to fix the specific deficiencies in a revision pass.

---

### 5. Deployment and CI/CD Automation

#### 5.1 Nightly Database Updates
Because data collection is time-consuming and API quotas are limited during active user sessions, we decouple active UI usage from heavy crawling:
*   A GitHub Actions workflow (`.github/workflows/daily_update.yml`) runs nightly at `00:00 UTC`.
*   It runs `scripts/collect_all.py` to scrape fresh data, compute trend scores, and update the SQLite file `database/market_analyzer.db`.
*   It then logs into HuggingFace Spaces using a write token (`HF_TOKEN`) and pushes the updated database file.
*   Users loading the Gradio app see pre-computed trend leaderboards instantly without waiting for a crawler.

#### 5.2 Gradio UI Design Details
To match a professional developer dashboard, the standard Gradio theme was customized using styling injection:
*   A dark-mode style is enforced via CSS variables (`#0A0A0A` background and `#141414` card grids).
*   High contrast cyan accents (`#00FFD5`) highlight execution buttons and UI elements.
*   The "Agent Reasoning Log" accordion uses raw string logging saved in `.tmp/agent_debug.log` to print the ReAct agent's thoughts in real time.

---

### 6. Developer Runbook & Extensibility

#### 6.1 Executing Tests
Validate system integrity by running the test suite:
```bash
# Run unit tests for data extraction, formula scoring, and evaluation
python -m pytest tests/test_trend_score.py
python -m pytest tests/test_collectors.py
python -m pytest tests/test_evaluator.py

# Run integration tests
python -m pytest tests/test_agent.py

# Run end-to-end integration test (simulates UI action)
python scripts/master_test.py
```

#### 6.2 How to Add a New Data Collector
1.  **Create Collector:** Add a script in `collectors/your_source.py` implementing a function `fetch_your_source() -> pd.DataFrame` returning `[app_id, title, genre, rank, rating, reviews, platform, fetched_at]`.
2.  **Update Database Schema:** If the new platform needs unique columns, update `database/schema.sql`.
3.  **Create Tool:** In `agent/tools.py`, create a new tool wrapper:
    ```python
    @tool
    def collect_your_source_data() -> str:
        """Detailed description for the agent."""
        df = your_source.fetch_your_source()
        snapshot.save_snapshot(df, "your_source_category")
        return f"Successfully scouted {len(df)} records."
    ```
4.  **Register Tool:** Append the new tool to `ALL_TOOLS` array in `agent/tools.py`. The agent will automatically discover it.
5.  **Write Directive:** Create `directives/14_your_source_scraper.md` outlining the rules.
