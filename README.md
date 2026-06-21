---
title: "ONYX: Agentic Market Intelligence"
emoji: "🌌"
colorFrom: blue
colorTo: indigo
sdk: gradio
python_version: "3.11"
app_file: app.py
pinned: true
---

# 🌌 ONYX: Agentic Market Intelligence System

> An autonomous, end-to-end data engineering platform that scouts, analyzes, and reports on digital market opportunities across the global gaming and app ecosystem.

**Team:** Uygar Tatar (2202400) · Muhammed Buğra Çiftçi (2101860)  
**Course:** (BAU) SEN4018 (1) Data Science with Python 25/26 · 
**Deployment:** [HuggingFace Spaces (Gradio)](https://huggingface.co/spaces/UygarTatar/market-trend-analyzer)  
**Project Documentation:** [📋 Executive Summary](EXECUTIVE_SUMMARY.md) · [⚙️ Practitioner's Notes](PRACTITIONERS_NOTES.md)

---

## 🚀 What It Does

ONYX is a fully agentic market intelligence system. You ask a natural-language question about the digital market, and the system autonomously:

1. **Collects live data** from Google Play, Apple App Store, Steam, and Reddit
2. **Computes trend scores** using a weighted algorithm (rank velocity + review delta + Reddit sentiment)
3. **Detects cross-platform patterns** — titles and genres trending across mobile and PC simultaneously
4. **Generates a structured analyst report** via Gemini Flash LLM
5. **Self-evaluates and revises** the report against a 5-criteria rubric (up to 2 revision passes)
6. **Renders visualizations** — trend bar charts, top-movers tables, and genre distribution pies

---

## 📄 Submission Deliverables

Select a section below to expand the full documentation directly on this page:

<details>
<summary><b>📋 Click to expand: 1. Executive Summary</b></summary>

### 1. The Vision and Problem Statement
In the fast-moving digital economy, understanding cross-platform trends in mobile and PC gaming/apps is critical for product managers, indie developers, and marketing analysts. However, existing market intelligence solutions (such as AppMagic, SensorTower, and data.ai) are gated behind prohibitively expensive enterprise pricing. Furthermore, existing pipelines require manual dashboard consolidation and reporting, leading to slow and error-prone decision cycles.

**ONYX** is an autonomous, end-to-end data engineering and agentic intelligence platform designed to scout, analyze, and report on digital market opportunities across the global app and gaming ecosystem. By leveraging free, public data sources and combining them with state-of-the-art Large Language Models (LLMs), ONYX automates the entire lifecycle of market analysis.

### 2. High-Level System Architecture
ONYX is designed around a **3-Layer Architecture** to bridge the gap between probabilistic AI reasoning and deterministic software execution:

```
                  ┌────────────────────────────────────────┐
                  │          USER QUERY (Gradio UI)        │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │    ORCHESTRATION LAYER (ReAct Agent)   │
                  │        (gemini-3.1-flash-lite)         │
                  └───────────────────┬────────────────────┘
                                      │  Uses 13 SOP Directives
                                      ▼
                  ┌────────────────────────────────────────┐
                  │     EXECUTION LAYER (Python Tools)     │
                  │  • Data Ingestion   • Trend Scoring    │
                  │  • SQLite Storage   • Report Generator │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │      EVALUATOR & REVISION LOOP         │
                  │    (Auto-evaluates & rewrites report)  │
                  └────────────────────────────────────────┘
```

*   **Layer 1: Directive (SOPs):** Thirteen Standard Operating Procedures (SOPs) written in Markdown reside in `directives/`. They govern the precise rules and workflows for every stage of the system.
*   **Layer 2: Orchestration (Agent):** A LangChain ReAct agent utilizing `gemini-3.1-flash-lite` coordinates the analysis, deciding which execution tools to trigger based on the user's natural language queries.
*   **Layer 3: Execution (Deterministic Scripts):** Modular Python scripts handle data collection (Google Play, App Store RSS, Steam Web API, Reddit PRAW), mathematical trend score computation, local SQLite snapshotting, and Plotly visualization rendering.

### 3. Core Innovations and Capabilities
1.  **Unified Trend Score Formula:** ONYX aggregates data points across platforms (mobile rank change, review velocity, and Reddit community sentiment) into a single mathematical score ($TrendScore \approx -1.0 \text{ to } +1.0$) to rank market movers objectively.
2.  **Cross-Platform Pattern Detection:** The engine automatically monitors and highlights genre-level overlaps and same-title migrations (e.g., titles trending on both Steam and mobile stores simultaneously) to detect mainstream gaming spillover.
3.  **Self-Evaluating Analyst Loop:** To ensure report quality, ONYX routes generated summaries through an autonomous evaluator LLM. Using a strict 5-criteria grading rubric, the system scores the output and triggers up to two recursive correction passes if the quality threshold ($< 0.7$) is not met.
4.  **Stealth UI Dashboard:** Gradio-powered command center featuring interactive charts (Plotly/Matplotlib), a live Database Intelligence Hub showing data density, and an accordion exposing the agent's real-time reasoning logs.

### 4. Project Achievements & Impact
*   **Zero-Maintenance Data Pipeline:** Run on a nightly GitHub Actions CRON workflow that refreshes the database (`market_analyzer.db`) and commits updates directly to HuggingFace Spaces.
*   **High LLM Reliability:** The 3-layer architecture separates concerns, yielding a system that does not hallucinate data points or get trapped in infinite agent execution loops.
*   **Accessible Insights:** Empowers indie developers and researchers with professional-grade, self-audited market analyst reports completely free of charge.

</details>

<details>
<summary><b>⚙️ Click to expand: 2. Practitioner's Notes & Engineering Reference</b></summary>

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

Reports can sometimes omit sections or fail to mention charts. ONYX implements an LLM-in-the-loop self-correction flow in `reporting/revision.py` using an evaluator assess framework based on 5 criteria:

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

The criteria assessed by the evaluator (each yielding a $0$ or $1$ score) are:
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
3.  **Create Tool:** In `agent/tools.py`, create a new tool wrapper.
4.  **Register Tool:** Append the new tool to `ALL_TOOLS` array in `agent/tools.py`.
5.  **Write Directive:** Create `directives/14_your_source_scraper.md` outlining the rules.

</details>

---

## 🏗️ Architecture

```
User Query (Gradio UI)
        ↓
  LangChain ReAct Agent  (gemini-3.1-flash-lite)
        ↓
  ┌─────────────────────────────────┐
  │         Agent Tools             │
  │  • collect_mobile_app_data      │
  │  • collect_mobile_game_data     │
  │  • collect_pc_game_data         │
  │  • compute_trends               │
  │  • detect_cross_platform        │
  │  • generate_trend_report        │
  └─────────────────────────────────┘
        ↓
  SQLite (Snapshotted Historical Data)
        ↓
  Report Generator (Gemini Flash)
        ↓
  Evaluator LLM → Revision Loop (max 2x)
        ↓
  Final Report + Charts → Gradio UI
```

### 3-Layer Design

| Layer | Role | Location |
|-------|------|----------|
| **Directive** | SOPs defining goals, inputs, outputs | `directives/` (13 markdown SOPs) |
| **Orchestration** | ReAct agent — routing, decisions, error handling | `agent/` |
| **Execution** | Deterministic Python scripts | `collectors/`, `analysis/`, `reporting/`, `visualization/`, `database/` |

---

## 📁 Repository Structure

```
market-trend-analyzer/
├── app.py                        # Gradio entry point — ONYX Stealth UI
├── requirements.txt
├── .env.example                  # API key template
│
├── agent/
│   ├── react_agent.py            # LangChain ReAct agent + deep logging
│   ├── tools.py                  # 6 agent tools registered with @tool
│   ├── prompts.py                # System prompt + 5-criteria evaluator prompt
│   └── memory.py                 # SQLite-backed session memory
│
├── collectors/
│   ├── mobile_apps.py            # Google Play + Apple App Store (iTunes RSS)
│   ├── mobile_games.py           # Game category scrapers (6 genres)
│   ├── pc_games.py               # Steam Web API + SteamSpy enrichment
│   └── reddit_sentiment.py       # PRAW — r/androidgaming, r/iosgaming, r/pcgaming
│
├── analysis/
│   ├── trend_score.py            # Weighted trend formula (rank 40% + reviews 30% + sentiment 30%)
│   ├── cross_platform.py         # Title and genre overlap detection across platforms
│   ├── snapshot.py               # 7-day rolling snapshot save/load
│   └── stats.py                  # Intelligence Hub statistics for the UI
│
├── reporting/
│   ├── generator.py              # Gemini Flash structured report writer
│   ├── evaluator.py              # Gemini Flash rubric evaluation → JSON score
│   └── revision.py               # Revision loop (threshold 0.7/1.0, max 2 attempts)
│
├── visualization/
│   ├── charts.py                 # Trend bar chart, top-movers table, genre pie
│   └── templates.py              # Chart layout defaults
│
├── database/
│   ├── schema.sql                # snapshots, trend_scores, reports tables
│   ├── db.py                     # get_connection() with auto-schema init
│   └── market_analyzer.db        # Live SQLite database (tracked via Git LFS)
│
├── directives/                   # 13 SOPs governing each pipeline stage
├── scripts/
│   ├── collect_all.py            # Batch collection script (used by GitHub Actions)
│   └── master_test.py            # End-to-end smoke test
│
├── tests/
│   ├── test_collectors.py
│   ├── test_trend_score.py
│   ├── test_agent.py
│   └── test_evaluator.py
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   └── 02_trend_score_tuning.ipynb
│
└── .github/workflows/
    ├── daily_update.yml          # Nightly scraper (00:00 UTC) + HuggingFace sync
    └── hf_sync.yml               # Manual HuggingFace deployment trigger
```

---

## 🧠 Key Components

### Trend Score Formula

```
score = (rank_change × 0.4) + (review_delta × 0.3) + (sentiment_shift × 0.3)
```

- **rank_change**: `(old_rank - new_rank) / old_rank` — normalized chart momentum
- **review_delta**: `(reviews_now - reviews_7d) / reviews_7d` — volume velocity
- **sentiment_shift**: `(avg_upvote_ratio - 0.5)` — Reddit community signal

Score range: approximately `−1.0` to `+1.0`

### Evaluator Rubric (5 Criteria)

Each generated report is automatically graded by a second LLM call:

| Criterion | Weight |
|-----------|--------|
| All 3 market categories covered | 0.2 |
| ≥ 3 numeric data points | 0.2 |
| Cross-market comparison section present | 0.2 |
| Visualization reference included | 0.2 |
| Clear conclusion / recommendation | 0.2 |

Reports scoring `< 0.7` trigger an automatic revision pass (max 2 attempts).

### Data Sources

| Source | Library / API | Data |
|--------|--------------|------|
| Google Play | `google-play-scraper` | Top charts, ratings, installs, genres |
| Apple App Store | iTunes RSS API (public) | Top free apps/games by category |
| Steam | Steam Web API + SteamSpy | Top sellers, genres, pricing, reviews |
| Reddit | PRAW (`r/androidgaming`, `r/iosgaming`, `r/pcgaming`, etc.) | Upvote ratio, comment count, post velocity |

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **LLM / Agent** | Google Gemini Flash (`gemini-3.1-flash-lite`) via LangChain ReAct |
| **Agent Framework** | LangChain 0.2.x (`create_react_agent` + `AgentExecutor`) |
| **Web UI** | Gradio (latest v5) — dark ONYX Stealth theme |
| **Database** | SQLite (`database/market_analyzer.db`) |
| **Data Collection** | `google-play-scraper`, `praw`, `requests`, `feedparser` |
| **Data Processing** | Pandas 2.2, NumPy 1.26 |
| **Visualization** | Matplotlib 3.9 + Plotly 5.24 (+ Kaleido for static export) |
| **Automation** | GitHub Actions (nightly cron + HuggingFace sync) |
| **Deployment** | HuggingFace Spaces (CPU Basic, free tier) |

---

## ⚙️ Installation & Local Setup

### Prerequisites

- Python 3.11+
- A Google Gemini API key ([get one here](https://console.cloud.google.com/))

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/UygarTatar/market-trend-analyzer.git
cd market-trend-analyzer

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
copy .env.example .env
# Edit .env and set your GOOGLE_API_KEY

# 5. (Optional) Pre-populate the database with one collection run
python scripts/collect_all.py

# 6. Launch the Gradio app
python app.py
```

The UI will be available at `http://localhost:7860`.

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | ✅ Yes | Gemini API key for LLM + agent |
| `DB_PATH` | Optional | Path to SQLite DB (default: `database/market_analyzer.db`) |

> Reddit credentials are **not required** — Reddit sentiment gracefully degrades to `0.0` if unavailable.

---

## 🤖 CI/CD — GitHub Actions

Two automated workflows keep the live data fresh:

| Workflow | Schedule | Description |
|----------|----------|-------------|
| `daily_update.yml` | `00:00 UTC` (nightly) | Runs `scripts/collect_all.py`, then pushes the updated `market_analyzer.db` to HuggingFace Spaces |
| `hf_sync.yml` | Manual trigger | Deploys code changes to HuggingFace Spaces |

**Secrets required in GitHub repository settings:**
- `GOOGLE_API_KEY`
- `HF_TOKEN` (HuggingFace write token)

---

## 📊 Gradio UI — ONYX Stealth Design

The interface features a high-contrast dark aesthetic (`#0A0A0A` background, Electric Cyan `#00FFD5` accents) with two tabs:

- **🤖 Command Center** — Natural-language query input, agent reasoning log accordion, final report output, and trend bar chart. Includes 4 strategic preset queries.
- **📊 Intelligence Hub** — Real-time database statistics (total data points, 24h additions, active entities), high-velocity trend leaderboard, and system health status.

---

## 🧪 Testing

```bash
# Unit tests
python -m pytest tests/test_trend_score.py   # Trend score formula
python -m pytest tests/test_collectors.py    # Steam + scraper smoke tests
python -m pytest tests/test_evaluator.py     # Evaluator JSON parsing

# Integration test (requires GOOGLE_API_KEY)
python -m pytest tests/test_agent.py

# Full end-to-end smoke test
python scripts/master_test.py
```

---

## 👥 Team

| Member | Student ID | Primary Responsibilities |
|--------|-----------|--------------------------|
| **Uygar Tatar** | 2202400 | Data collectors, trend scoring engine, database layer, visualization, cross-platform analysis |
| **Muhammed Buğra Çiftçi** | 2101860 | ReAct agent, LangChain tools, report generator, evaluator, revision loop, Gradio UI, HuggingFace deployment |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
