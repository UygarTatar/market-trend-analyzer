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
**Course:** Agentic AI Systems · **Deadline:** May 31, 2026  
**Deployment:** [HuggingFace Spaces (Gradio)](https://huggingface.co/spaces/UygarTatar/market-trend-analyzer)

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
