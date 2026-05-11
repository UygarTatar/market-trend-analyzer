# Agentic Digital Market Trend Analyzer — Comprehensive Project Plan

> **Team:** Uygar Tatar (2202400) · Muhammed Buğra Çiftçi (2101860)
> **Deadline:** May 31, 2026 · **Deployment:** HuggingFace Spaces (Gradio)

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Structure](#2-repository-structure)
3. [Environment Setup](#3-environment-setup)
4. [Data Collection Layer](#4-data-collection-layer)
5. [Trend Detection Engine](#5-trend-detection-engine)
6. [LangChain ReAct Agent](#6-langchain-react-agent)
7. [Report Generation](#7-report-generation)
8. [Evaluator LLM & Revision Loop](#8-evaluator-llm--revision-loop)
9. [Visualization Layer](#9-visualization-layer)
10. [Database Layer](#10-database-layer)
11. [Gradio Web Interface](#11-gradio-web-interface)
12. [HuggingFace Spaces Deployment](#12-huggingface-spaces-deployment)
13. [Testing Strategy](#13-testing-strategy)
14. [Weekly Sprint Plan](#14-weekly-sprint-plan)
15. [Risk Register](#15-risk-register)
16. [Team Responsibility Matrix](#16-team-responsibility-matrix)
17. [Definition of Done](#17-definition-of-done)

---

## 1. Project Overview

### Goal
Build an end-to-end agentic AI system that autonomously collects, analyzes, and reports on trends across three digital market categories: **Mobile Apps**, **Mobile Games**, and **PC Games** — and delivers structured analyst-quality reports through an interactive web UI.

### Core User Journey
```
User submits natural-language query
        ↓
Agent collects live data from 3 market sources
        ↓
Trend scores computed per category
        ↓
Cross-platform patterns detected
        ↓
Gemini 1.5 Pro generates narrative report + visualizations
        ↓
Gemini 1.5 Flash evaluates report against rubric
        ↓
Revision pass if score < 3.5/5 (max 2 attempts)
        ↓
Final formatted report returned to user in Gradio UI
```

### Key Constraints
- All data sources must be **free and programmatically accessible**
- No enterprise APIs (SensorTower, data.ai, AppMagic)
- Single-file Gradio app deployable on **HuggingFace Spaces free tier**
- Trend window: **7-day rolling** (academic timeline constraint)
- Max revision attempts: **2**

---

## 2. Repository Structure

```
market-trend-analyzer/
│
├── app.py                        # Gradio entry point (HuggingFace Spaces)
├── requirements.txt
├── .env.example                  # API key template (never commit .env)
├── README.md
│
├── agent/
│   ├── __init__.py
│   ├── react_agent.py            # LangChain ReAct agent core
│   ├── tools.py                  # Tool registry (all agent tools defined here)
│   ├── prompts.py                # System prompts for generator + evaluator
│   └── memory.py                 # SQLite-backed agent session memory
│
├── collectors/
│   ├── __init__.py
│   ├── mobile_apps.py            # google-play-scraper + app-store-scraper
│   ├── mobile_games.py           # Same libs, GAME category filter
│   ├── pc_games.py               # Steam Web API + SteamSpy
│   └── reddit_sentiment.py       # PRAW — r/androidgaming, r/iosgaming, etc.
│
├── analysis/
│   ├── __init__.py
│   ├── trend_score.py            # compute_trend_score() formula
│   ├── cross_platform.py         # detect_overlap() across all 3 categories
│   └── snapshot.py               # Save/load market snapshots to SQLite
│
├── reporting/
│   ├── __init__.py
│   ├── generator.py              # Gemini 1.5 Pro report generation
│   ├── evaluator.py              # Gemini 1.5 Flash rubric evaluation
│   └── revision.py               # Revision loop orchestration
│
├── visualization/
│   ├── __init__.py
│   ├── charts.py                 # Matplotlib + Plotly chart builders
│   └── templates.py              # Chart layout defaults
│
├── database/
│   ├── __init__.py
│   ├── schema.sql                # SQLite schema definitions
│   └── db.py                     # DB connection + CRUD helpers
│
├── tests/
│   ├── test_collectors.py
│   ├── test_trend_score.py
│   ├── test_agent.py
│   └── test_evaluator.py
│
└── notebooks/
    ├── 01_data_exploration.ipynb
    └── 02_trend_score_tuning.ipynb
```

---

## 3. Environment Setup

### 3.1 Python Version
Use **Python 3.11** (stable, compatible with all listed libraries).

### 3.2 Requirements (`requirements.txt`)
```
# Core agent framework
langchain==0.2.16
langchain-google-genai==1.0.10

# LLM
google-generativeai==0.7.2

# Data collection
google-play-scraper==1.2.7
app-store-scraper==0.3.5
praw==7.7.1
requests==2.32.3

# Data processing
pandas==2.2.2
numpy==1.26.4

# Visualization
matplotlib==3.9.2
plotly==5.24.1
kaleido==0.2.1            # Plotly static image export

# Web UI
gradio==4.44.0

# Database
# sqlite3 is built into Python — no pip install needed

# Utilities
python-dotenv==1.0.1
tenacity==8.5.0           # Retry logic for API calls
```

### 3.3 API Keys Needed
| Key | Where to get | Free? |
|-----|-------------|-------|
| `GOOGLE_API_KEY` | console.cloud.google.com | Yes (Gemini quota) |
| `REDDIT_CLIENT_ID` | reddit.com/prefs/apps | Yes |
| `REDDIT_CLIENT_SECRET` | Same as above | Yes |
| `REDDIT_USER_AGENT` | Any string (e.g. `MarketBot/1.0`) | Yes |

### 3.4 `.env.example`
```
GOOGLE_API_KEY=your_gemini_api_key_here
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=MarketTrendBot/1.0
```

---

## 4. Data Collection Layer

### 4.1 Mobile Apps (`collectors/mobile_apps.py`)

**Source:** `google-play-scraper` (Android) + `app-store-scraper` (iOS)

```python
from google_play_scraper import top_charts, app
from app_store_scraper import AppStore
import pandas as pd

def fetch_google_play_top_apps(category="APPLICATION", count=50, country="us"):
    """Fetch top free apps from Google Play."""
    results = top_charts(
        chart="topselling_free",
        category=category,
        country=country,
        count=count
    )
    records = []
    for item in results:
        records.append({
            "app_id": item["appId"],
            "title": item["title"],
            "category": item["genre"],
            "rating": item.get("score", 0),
            "reviews": item.get("reviews", 0),
            "installs": item.get("installs", "0"),
            "platform": "android",
            "rank": item.get("rank", 0),
            "fetched_at": pd.Timestamp.now()
        })
    return pd.DataFrame(records)

def fetch_app_store_top_apps(category_id=6000, count=50, country="us"):
    """Fetch top apps from Apple App Store."""
    import requests
    url = (
        f"https://itunes.apple.com/{country}/rss/topfreeapplications/"
        f"limit={count}/genre={category_id}/json"
    )
    resp = requests.get(url, timeout=10)
    entries = resp.json()["feed"]["entry"]
    records = []
    for i, entry in enumerate(entries):
        records.append({
            "app_id": entry["id"]["attributes"]["im:id"],
            "title": entry["im:name"]["label"],
            "category": entry["category"]["attributes"]["label"],
            "rating": float(entry.get("im:averageUserRating", {}).get("label", 0) or 0),
            "reviews": 0,  # RSS doesn't include review count
            "platform": "ios",
            "rank": i + 1,
            "fetched_at": pd.Timestamp.now()
        })
    return pd.DataFrame(records)
```

**Notes:**
- `google-play-scraper` handles JavaScript rendering internally — no headless browser needed.
- Apple App Store RSS feed is fully public and does not require credentials.
- Both functions return normalized DataFrames with the same schema for easy merging.

### 4.2 Mobile Games (`collectors/mobile_games.py`)

Same libraries as above, different category filters:

```python
GOOGLE_PLAY_GAME_CATEGORIES = [
    "GAME_ACTION", "GAME_CASUAL", "GAME_PUZZLE",
    "GAME_RACING", "GAME_RPG", "GAME_STRATEGY"
]

APP_STORE_GAME_CATEGORY_ID = 6014  # Games category ID

def fetch_all_mobile_game_categories(count_per_cat=20):
    """Fetch games across all major genres."""
    frames = []
    for cat in GOOGLE_PLAY_GAME_CATEGORIES:
        df = fetch_google_play_top_apps(category=cat, count=count_per_cat)
        df["genre"] = cat
        frames.append(df)
    return pd.concat(frames, ignore_index=True)
```

### 4.3 PC Games (`collectors/pc_games.py`)

**Primary source:** Steam Web API (no authentication for public endpoints)
**Supplementary:** SteamSpy (genre enrichment, optional)

```python
import requests
import pandas as pd

STEAM_TOP_SELLERS_URL = "https://store.steampowered.com/api/featuredcategories/"
STEAM_APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails"
STEAM_REVIEWS_URL = "https://store.steampowered.com/appreviews/{app_id}"

def fetch_steam_top_sellers(count=50):
    """Fetch top-selling games from Steam."""
    resp = requests.get(STEAM_TOP_SELLERS_URL, timeout=15)
    items = resp.json()["top_sellers"]["items"][:count]
    records = []
    for i, item in enumerate(items):
        records.append({
            "app_id": item["id"],
            "title": item["name"],
            "rank": i + 1,
            "platform": "pc_steam",
            "fetched_at": pd.Timestamp.now()
        })
    return pd.DataFrame(records)

def fetch_steam_app_details(app_id):
    """Fetch detailed metadata for a single Steam app."""
    resp = requests.get(
        STEAM_APP_DETAILS_URL,
        params={"appids": app_id, "cc": "us"},
        timeout=10
    )
    data = resp.json().get(str(app_id), {}).get("data", {})
    return {
        "genres": [g["description"] for g in data.get("genres", [])],
        "price_usd": data.get("price_overview", {}).get("final", 0) / 100,
        "release_date": data.get("release_date", {}).get("date", ""),
        "review_score": data.get("metacritic", {}).get("score", 0)
    }

def get_steamspy_tags(app_id):
    """Optional: enriched genre tags from SteamSpy."""
    try:
        url = f"https://steamspy.com/api.php?request=appdetails&appid={app_id}"
        resp = requests.get(url, timeout=10)
        return list(resp.json().get("tags", {}).keys())[:5]
    except Exception:
        return []  # Graceful degradation — SteamSpy is supplementary
```

**Rate limiting note:** Steam API limits to ~200 requests/5 minutes. Add `time.sleep(1)` between `fetch_steam_app_details` calls in loops.

### 4.4 Reddit Sentiment (`collectors/reddit_sentiment.py`)

```python
import praw
import os
import pandas as pd

SUBREDDITS = {
    "mobile_apps": ["androidapps", "iosapps"],
    "mobile_games": ["AndroidGaming", "iosgaming"],
    "pc_games": ["pcgaming", "Games", "Steam"]
}

def init_reddit():
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "MarketTrendBot/1.0")
    )

def fetch_subreddit_posts(subreddit_name, limit=50, time_filter="week"):
    """Fetch top posts from a subreddit over the past week."""
    reddit = init_reddit()
    sub = reddit.subreddit(subreddit_name)
    records = []
    for post in sub.top(time_filter=time_filter, limit=limit):
        records.append({
            "title": post.title,
            "score": post.score,
            "num_comments": post.num_comments,
            "upvote_ratio": post.upvote_ratio,
            "created_utc": pd.Timestamp.fromtimestamp(post.created_utc),
            "subreddit": subreddit_name
        })
    return pd.DataFrame(records)

def aggregate_sentiment_by_category(category):
    """Aggregate post engagement metrics as a sentiment proxy."""
    frames = [fetch_subreddit_posts(sub) for sub in SUBREDDITS[category]]
    df = pd.concat(frames, ignore_index=True)
    return {
        "avg_score": df["score"].mean(),
        "total_comments": df["num_comments"].sum(),
        "avg_upvote_ratio": df["upvote_ratio"].mean(),
        "post_count": len(df)
    }
```

---

## 5. Trend Detection Engine

### 5.1 Snapshot Storage (`analysis/snapshot.py`)

Before computing trends, you need two snapshots: **today** and **7 days ago**. The DB stores these rolling snapshots.

```python
from database.db import get_connection
import pandas as pd

def save_snapshot(df: pd.DataFrame, category: str):
    """Save a market snapshot to the database."""
    conn = get_connection()
    df["category"] = category
    df["snapshot_date"] = pd.Timestamp.now().date()
    df.to_sql("snapshots", conn, if_exists="append", index=False)
    conn.close()

def load_snapshot(category: str, days_ago: int = 7) -> pd.DataFrame:
    """Load a snapshot from N days ago."""
    conn = get_connection()
    target_date = (pd.Timestamp.now() - pd.Timedelta(days=days_ago)).date()
    query = """
        SELECT * FROM snapshots
        WHERE category = ? AND snapshot_date = ?
    """
    df = pd.read_sql(query, conn, params=[category, target_date])
    conn.close()
    return df
```

### 5.2 Trend Score Formula (`analysis/trend_score.py`)

```python
def compute_trend_score(rank_change: float, review_delta: float, sentiment_shift: float) -> float:
    """
    Compute a weighted trend score for a market category.

    Parameters
    ----------
    rank_change     : float — position improvement in top charts, normalized 0–1.
                      Positive = moved UP in rankings. Formula: (old_rank - new_rank) / old_rank
    review_delta    : float — % increase in total review volume over 7 days.
                      Formula: (reviews_now - reviews_7d_ago) / reviews_7d_ago
    sentiment_shift : float — change in average rating over 7 days, range -1 to +1.
                      Formula: (avg_rating_now - avg_rating_7d_ago) / 5.0  (normalized to max 5-star)

    Returns
    -------
    float — trend score in range approximately -1 to +1
    """
    score = (rank_change * 0.4) + (review_delta * 0.3) + (sentiment_shift * 0.3)
    return round(score, 3)


def compute_category_trend(current_df, previous_df, sentiment_data) -> dict:
    """
    Compute aggregate trend metrics for a full market category DataFrame.

    Returns a dict with trend_score, top_movers, and interpretation.
    """
    if previous_df.empty:
        return {"trend_score": 0.0, "top_movers": [], "note": "No 7-day baseline available yet"}

    # Rank change: merge on app_id, compute rank delta
    merged = current_df.merge(previous_df[["app_id", "rank"]], on="app_id", suffixes=("_now", "_7d"))
    merged["rank_change"] = (merged["rank_7d"] - merged["rank_now"]) / merged["rank_7d"].clip(lower=1)

    # Review delta
    if "reviews" in current_df.columns and "reviews" in previous_df.columns:
        rev_merged = current_df.merge(previous_df[["app_id", "reviews"]], on="app_id", suffixes=("_now", "_7d"))
        review_delta = ((rev_merged["reviews_now"] - rev_merged["reviews_7d"]) / rev_merged["reviews_7d"].clip(lower=1)).mean()
    else:
        review_delta = 0.0

    # Sentiment shift from Reddit proxy
    sentiment_shift = sentiment_data.get("avg_upvote_ratio", 0.5) - 0.5  # Normalize around 0

    score = compute_trend_score(
        rank_change=merged["rank_change"].mean(),
        review_delta=review_delta,
        sentiment_shift=sentiment_shift
    )

    top_movers = (
        merged.nlargest(5, "rank_change")[["app_id", "title", "rank_change"]]
        .to_dict(orient="records")
    )

    return {
        "trend_score": score,
        "top_movers": top_movers,
        "rank_change_avg": round(merged["rank_change"].mean(), 3),
        "review_delta": round(review_delta, 3),
        "sentiment_shift": round(sentiment_shift, 3)
    }
```

### 5.3 Cross-Platform Pattern Detection (`analysis/cross_platform.py`)

```python
def detect_overlap(category_results: dict) -> dict:
    """
    Identify apps/games appearing across platforms and shared genre trends.

    Parameters
    ----------
    category_results : dict — keys are 'mobile_apps', 'mobile_games', 'pc_games'
                       each value is a DataFrame of top items for that category
    """
    # 1. Title-based overlap (same game on mobile + PC)
    mobile_titles = set(category_results["mobile_games"]["title"].str.lower())
    pc_titles = set(category_results["pc_games"]["title"].str.lower())
    cross_platform_titles = mobile_titles & pc_titles

    # 2. Genre trend overlap
    genre_trends = {}
    for category, df in category_results.items():
        if "genre" in df.columns:
            top_genre = df["genre"].value_counts().idxmax()
            genre_trends[category] = top_genre

    return {
        "cross_platform_titles": list(cross_platform_titles),
        "dominant_genre_per_category": genre_trends,
        "shared_genre_trend": _find_shared_genre(genre_trends)
    }

def _find_shared_genre(genre_trends: dict) -> str:
    """Return the genre appearing most commonly across categories."""
    all_genres = list(genre_trends.values())
    if not all_genres:
        return "N/A"
    from collections import Counter
    return Counter(all_genres).most_common(1)[0][0]
```

---

## 6. LangChain ReAct Agent

### 6.1 Tool Registry (`agent/tools.py`)

```python
from langchain.tools import tool
from collectors import mobile_apps, mobile_games, pc_games, reddit_sentiment
from analysis import trend_score, cross_platform, snapshot
from reporting import generator

@tool
def collect_mobile_app_data(country: str = "us") -> str:
    """Collect current top mobile app rankings from Google Play and App Store."""
    gp_df = mobile_apps.fetch_google_play_top_apps(count=50, country=country)
    ios_df = mobile_apps.fetch_app_store_top_apps(count=50, country=country)
    snapshot.save_snapshot(gp_df, "mobile_apps_android")
    snapshot.save_snapshot(ios_df, "mobile_apps_ios")
    return f"Collected {len(gp_df)} Android apps and {len(ios_df)} iOS apps."

@tool
def collect_mobile_game_data(country: str = "us") -> str:
    """Collect current top mobile game rankings across all major genres."""
    df = mobile_games.fetch_all_mobile_game_categories(count_per_cat=20)
    snapshot.save_snapshot(df, "mobile_games")
    return f"Collected {len(df)} mobile game entries across {df['genre'].nunique()} genres."

@tool
def collect_pc_game_data() -> str:
    """Collect current top-selling PC games from Steam."""
    df = pc_games.fetch_steam_top_sellers(count=50)
    snapshot.save_snapshot(df, "pc_games")
    return f"Collected {len(df)} Steam top sellers."

@tool
def compute_trends(category: str) -> str:
    """
    Compute trend scores for a given category.
    category must be one of: mobile_apps, mobile_games, pc_games
    """
    current = snapshot.load_snapshot(category, days_ago=0)
    previous = snapshot.load_snapshot(category, days_ago=7)
    sentiment = reddit_sentiment.aggregate_sentiment_by_category(category)
    result = trend_score.compute_category_trend(current, previous, sentiment)
    return str(result)

@tool
def detect_cross_platform_patterns() -> str:
    """Detect overlapping titles and genre trends across all three market categories."""
    data = {
        "mobile_apps": snapshot.load_snapshot("mobile_apps", days_ago=0),
        "mobile_games": snapshot.load_snapshot("mobile_games", days_ago=0),
        "pc_games": snapshot.load_snapshot("pc_games", days_ago=0)
    }
    result = cross_platform.detect_overlap(data)
    return str(result)

@tool
def generate_trend_report(user_query: str, analysis_data: str) -> str:
    """Generate a full market trend report using Gemini 1.5 Pro."""
    return generator.generate_report(user_query, analysis_data)

ALL_TOOLS = [
    collect_mobile_app_data,
    collect_mobile_game_data,
    collect_pc_game_data,
    compute_trends,
    detect_cross_platform_patterns,
    generate_trend_report
]
```

### 6.2 Agent Core (`agent/react_agent.py`)

```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from agent.tools import ALL_TOOLS
from agent.prompts import SYSTEM_PROMPT
import os

def build_agent() -> AgentExecutor:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3
    )

    prompt = hub.pull("hwchase17/react")  # Standard ReAct prompt template

    agent = create_react_agent(llm=llm, tools=ALL_TOOLS, prompt=prompt)

    return AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True,
        return_intermediate_steps=True
    )

def run_agent(user_query: str) -> str:
    agent_executor = build_agent()
    result = agent_executor.invoke({"input": user_query})
    return result["output"]
```

### 6.3 System Prompt (`agent/prompts.py`)

```python
SYSTEM_PROMPT = """
You are a market intelligence analyst AI. Your job is to autonomously collect,
analyze, and synthesize trends across three digital market categories:
Mobile Apps, Mobile Games, and PC Games.

For every query, you MUST:
1. Collect fresh data from all three market categories
2. Compute trend scores for each category
3. Detect cross-platform patterns
4. Generate a structured analyst report with visualizations

Your report MUST include:
- Coverage of all 3 market categories
- At least 3 specific numeric data points
- A cross-market comparison section
- A reference to at least one data visualization
- A clear conclusion or recommendation

Always reason step-by-step before choosing your next action.
"""

EVALUATOR_PROMPT = """
You are a strict structural report evaluator. Evaluate the following market report
against exactly these 5 criteria. For each criterion, output 1 if it passes, 0 if it fails.
Output ONLY a JSON object in this exact format:

{
  "all_3_categories_covered": 0 or 1,
  "three_numeric_datapoints": 0 or 1,
  "cross_market_comparison": 0 or 1,
  "visualization_reference": 0 or 1,
  "clear_conclusion": 0 or 1,
  "total_score": float (sum / 5),
  "feedback": "brief feedback for revision if score < 0.7"
}

Report to evaluate:
{report}
"""
```

---

## 7. Report Generation

### `reporting/generator.py`

```python
import google.generativeai as genai
import os

def generate_report(user_query: str, analysis_data: str) -> str:
    """
    Use Gemini 1.5 Pro to generate a structured market trend report.
    """
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-pro")

    prompt = f"""
You are a senior market intelligence analyst. Based on the following data, write a
comprehensive market trend report that answers the user's question.

User Question: {user_query}

Market Data:
{analysis_data}

Your report must follow this structure:
## Executive Summary
## Mobile Apps Trends
## Mobile Games Trends
## PC Games Trends
## Cross-Platform Analysis
## Key Data Points (include at least 3 numeric values)
## Visualizations (describe what charts were generated)
## Conclusion & Recommendations

Write in a professional but accessible tone suitable for product managers and developers.
"""
    response = model.generate_content(prompt)
    return response.text
```

---

## 8. Evaluator LLM & Revision Loop

### `reporting/evaluator.py`

```python
import google.generativeai as genai
import json
import os
from agent.prompts import EVALUATOR_PROMPT

def evaluate_report(report: str) -> dict:
    """
    Use Gemini 1.5 Flash to evaluate a report against the 5-criteria rubric.
    Returns a dict with criterion scores, total_score, and feedback.
    """
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = EVALUATOR_PROMPT.format(report=report)
    response = model.generate_content(prompt)

    # Strip markdown fences if present
    raw = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(raw)
```

### `reporting/revision.py`

```python
from reporting.generator import generate_report
from reporting.evaluator import evaluate_report

MAX_REVISION_ATTEMPTS = 2
PASSING_THRESHOLD = 0.7  # 3.5 / 5 criteria = 0.7

def generate_with_evaluation(user_query: str, analysis_data: str) -> dict:
    """
    Generate a report, evaluate it, and revise if needed.
    Returns the best-scoring report regardless of outcome.
    """
    best_report = None
    best_score = -1
    attempt = 0

    while attempt < MAX_REVISION_ATTEMPTS:
        if attempt == 0:
            report = generate_report(user_query, analysis_data)
        else:
            # Include evaluator feedback in revision prompt
            revision_context = f"""
Previous report scored {eval_result['total_score']:.1f}/1.0.
Evaluator feedback: {eval_result['feedback']}

Please revise the report to address these specific issues.

Original data:
{analysis_data}
"""
            report = generate_report(user_query, revision_context)

        eval_result = evaluate_report(report)
        score = eval_result.get("total_score", 0)

        if score > best_score:
            best_score = score
            best_report = report

        if score >= PASSING_THRESHOLD:
            break

        attempt += 1

    return {
        "report": best_report,
        "final_score": best_score,
        "attempts": attempt + 1,
        "passed_evaluation": best_score >= PASSING_THRESHOLD
    }
```

---

## 9. Visualization Layer

### `visualization/charts.py`

```python
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import io
import base64

def create_trend_score_bar(category_scores: dict) -> str:
    """
    Bar chart comparing trend scores across 3 categories.
    Returns base64-encoded PNG for embedding in Gradio.
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    categories = list(category_scores.keys())
    scores = list(category_scores.values())
    colors = ["#4CAF50" if s > 0 else "#F44336" for s in scores]

    ax.bar(categories, scores, color=colors, edgecolor="white")
    ax.axhline(y=0, color="black", linewidth=0.8, linestyle="--")
    ax.set_title("7-Day Trend Scores by Market Category", fontsize=14, fontweight="bold")
    ax.set_ylabel("Trend Score")
    ax.set_ylim(-1, 1)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def create_top_movers_table(top_movers: list, category: str) -> go.Figure:
    """
    Interactive Plotly table of top-moving apps/games.
    """
    if not top_movers:
        return go.Figure()

    df = pd.DataFrame(top_movers)
    df["rank_change"] = (df["rank_change"] * 100).round(1).astype(str) + "%"

    fig = go.Figure(data=[go.Table(
        header=dict(values=["Title", "Rank Change"], fill_color="#1E3A5F", font=dict(color="white", size=13)),
        cells=dict(values=[df["title"], df["rank_change"]], fill_color="#F5F5F5", font=dict(size=12))
    )])
    fig.update_layout(title=f"Top Movers — {category.replace('_', ' ').title()}", margin=dict(l=10, r=10, t=40, b=10))
    return fig

def create_genre_distribution_pie(genre_counts: dict, title: str) -> go.Figure:
    """Pie chart of genre distribution within a category."""
    labels = list(genre_counts.keys())
    values = list(genre_counts.values())
    fig = px.pie(names=labels, values=values, title=title, hole=0.3)
    return fig
```

---

## 10. Database Layer

### `database/schema.sql`

```sql
CREATE TABLE IF NOT EXISTS snapshots (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id      TEXT NOT NULL,
    title       TEXT,
    category    TEXT NOT NULL,       -- 'mobile_apps', 'mobile_games', 'pc_games'
    platform    TEXT,                -- 'android', 'ios', 'pc_steam'
    genre       TEXT,
    rank        INTEGER,
    rating      REAL,
    reviews     INTEGER,
    installs    TEXT,
    snapshot_date DATE NOT NULL,
    fetched_at  TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS trend_scores (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    category        TEXT NOT NULL,
    trend_score     REAL,
    rank_change_avg REAL,
    review_delta    REAL,
    sentiment_shift REAL,
    computed_at     TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS reports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    query           TEXT,
    report_text     TEXT,
    eval_score      REAL,
    attempts        INTEGER,
    created_at      TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_snapshots_category_date
    ON snapshots(category, snapshot_date);
```

### `database/db.py`

```python
import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "market_data.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _initialize_schema(conn)
    return conn

def _initialize_schema(conn):
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path) as f:
        conn.executescript(f.read())
    conn.commit()
```

---

## 11. Gradio Web Interface

### `app.py`

```python
import gradio as gr
from agent.react_agent import run_agent
from reporting.revision import generate_with_evaluation
from dotenv import load_dotenv

load_dotenv()

EXAMPLE_QUERIES = [
    "What genres are trending this week across mobile and PC?",
    "Which apps have seen the biggest rating improvements in the last 7 days?",
    "Are there any titles dominating both mobile and PC charts right now?",
    "What monetization trends are emerging in mobile games?"
]

def analyze_market(query: str, progress=gr.Progress()):
    if not query.strip():
        return "Please enter a query.", "", 0

    progress(0, desc="Collecting market data...")
    try:
        progress(0.3, desc="Running trend analysis...")
        raw_result = run_agent(query)

        progress(0.7, desc="Evaluating report quality...")
        # run_agent already handles generation + evaluation internally
        # Return the agent's output directly
        return raw_result, "✅ Analysis complete", 1.0

    except Exception as e:
        return f"Error: {str(e)}", "❌ Analysis failed", 0

with gr.Blocks(title="Digital Market Trend Analyzer", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 📊 Agentic Digital Market Trend Analyzer
    *Autonomous trend analysis across Mobile Apps, Mobile Games, and PC Games*
    """)

    with gr.Row():
        with gr.Column(scale=2):
            query_box = gr.Textbox(
                label="Your Market Research Question",
                placeholder="e.g. What genres are trending this week?",
                lines=2
            )
            with gr.Row():
                submit_btn = gr.Button("🔍 Analyze Market", variant="primary")
                clear_btn = gr.Button("Clear")

            gr.Examples(examples=EXAMPLE_QUERIES, inputs=query_box, label="Example Queries")

        with gr.Column(scale=1):
            status_box = gr.Textbox(label="Status", interactive=False)
            eval_score = gr.Slider(label="Report Quality Score", minimum=0, maximum=1, interactive=False)

    with gr.Row():
        report_output = gr.Markdown(label="Market Trend Report")

    submit_btn.click(fn=analyze_market, inputs=query_box, outputs=[report_output, status_box, eval_score])
    clear_btn.click(fn=lambda: ("", "", 0), outputs=[report_output, status_box, eval_score])

if __name__ == "__main__":
    demo.launch(share=False)
```

---

## 12. HuggingFace Spaces Deployment

### Steps

1. Create a new Space at [huggingface.co/spaces](https://huggingface.co/spaces)
   - SDK: **Gradio**
   - Hardware: **CPU Basic (free)**

2. Add secrets in Space settings (never put API keys in code):
   - `GOOGLE_API_KEY`
   - `REDDIT_CLIENT_ID`
   - `REDDIT_CLIENT_SECRET`
   - `REDDIT_USER_AGENT`

3. Push your repo:
   ```bash
   git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/market-trend-analyzer
   git push hf main
   ```

4. The Space auto-detects `app.py` as the entry point and `requirements.txt` for dependencies.

### `README.md` Header (for HuggingFace)

```yaml
---
title: Digital Market Trend Analyzer
emoji: 📊
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
---
```

---

## 13. Testing Strategy

### Unit Tests

**`tests/test_trend_score.py`**
```python
from analysis.trend_score import compute_trend_score

def test_positive_trend():
    score = compute_trend_score(rank_change=0.5, review_delta=0.3, sentiment_shift=0.2)
    assert 0 < score < 1

def test_negative_trend():
    score = compute_trend_score(rank_change=-0.5, review_delta=-0.2, sentiment_shift=-0.3)
    assert score < 0

def test_weights_sum():
    # All signals at max = 1.0 score
    score = compute_trend_score(1.0, 1.0, 1.0)
    assert score == 1.0
```

**`tests/test_collectors.py`**
```python
from collectors.pc_games import fetch_steam_top_sellers

def test_steam_returns_data():
    df = fetch_steam_top_sellers(count=10)
    assert len(df) > 0
    assert "title" in df.columns
    assert "rank" in df.columns

def test_steam_rank_sequential():
    df = fetch_steam_top_sellers(count=10)
    assert df["rank"].min() == 1
```

### Integration Test
```python
# tests/test_agent.py
from agent.react_agent import run_agent

def test_agent_returns_report():
    result = run_agent("What are the top trending genres this week?")
    assert isinstance(result, str)
    assert len(result) > 200  # Non-trivial output
```

### Manual QA Checklist
- [ ] All 3 data collectors return non-empty DataFrames
- [ ] Trend scores are computed within range [-1, 1]
- [ ] Evaluator returns valid JSON with all 5 criteria
- [ ] Revision loop stops at max 2 attempts
- [ ] Gradio UI loads without error
- [ ] Example queries all produce reports
- [ ] HuggingFace Space loads and accepts queries

---

## 14. Weekly Sprint Plan

### Week 1: May 5–11 — Data Collection Pipeline
**Owner: Uygar Tatar**

| Task | Description | Done When |
|------|-------------|-----------|
| Implement `mobile_apps.py` | Google Play + App Store scrapers | Returns normalized DataFrame |
| Implement `mobile_games.py` | Game category scrapers | Covers 6+ genre categories |
| Implement `pc_games.py` | Steam API + SteamSpy | Top 50 sellers with metadata |
| Implement `reddit_sentiment.py` | PRAW integration | Returns sentiment dict per category |
| Implement `database/` | Schema + DB helpers | Snapshots save and load correctly |
| Implement `analysis/snapshot.py` | Save/load snapshots | 7-day lookback works |
| Implement `analysis/trend_score.py` | compute_trend_score() | Unit tests pass |
| Write `tests/test_collectors.py` | Smoke tests for all collectors | All pass |

**Deliverable:** All collectors working locally, data saves to SQLite, trend scores compute.

---

### Week 2: May 12–18 — Agent & Decision Loop
**Owner: Muhammed Buğra Çiftçi**

| Task | Description | Done When |
|------|-------------|-----------|
| Implement `agent/tools.py` | All 6 agent tools registered | Tools callable individually |
| Implement `agent/react_agent.py` | LangChain ReAct agent | Agent completes 3-step collection |
| Implement `agent/prompts.py` | System + evaluator prompts | Prompts produce correct LLM output |
| Implement `analysis/cross_platform.py` | detect_overlap() | Returns cross-platform dict |
| Local end-to-end test | Run agent with sample query | Full pipeline completes |
| Write `tests/test_agent.py` | Integration test | Agent returns non-empty report |

**Deliverable:** Agent runs locally, collects all data, produces raw analysis.

---

### Week 3: May 19–25 — Report Generation + Evaluation
**Owner: Both**

| Task | Description | Done When |
|------|-------------|-----------|
| Implement `reporting/generator.py` | Gemini 1.5 Pro report writer | Returns structured markdown report |
| Implement `reporting/evaluator.py` | Gemini 1.5 Flash rubric check | Returns valid JSON with 5 scores |
| Implement `reporting/revision.py` | Revision loop with max 2 attempts | Loop exits correctly in all cases |
| Implement `visualization/charts.py` | Trend bar + movers table + genre pie | Charts render without error |
| End-to-end test with evaluation | Full pipeline including revision | Passing score on 3 example queries |
| Write `tests/test_evaluator.py` | Unit tests for evaluator | JSON parse succeeds on all outputs |

**Deliverable:** Full pipeline: collect → analyze → generate → evaluate → revise → output.

---

### Week 4: May 26–31 — UI, Deployment & Submission
**Owner: Muhammed Buğra Çiftçi (UI) + Uygar Tatar (polish)**

| Task | Description | Done When |
|------|-------------|-----------|
| Build `app.py` Gradio interface | Query box, output, status, examples | UI loads locally |
| Add visualizations to UI | Charts appear in Gradio output | Charts render inline |
| Create HuggingFace Space | Push repo, add secrets | Space loads publicly |
| Manual QA on deployed Space | Test all example queries live | All 4 examples return reports |
| Update blog post | Add deployed link + retrospective | Post published on Medium |
| Final code cleanup | Remove debug prints, add docstrings | Code is clean and readable |
| Submit MS Teams link | Submit HuggingFace Space URL | ✅ Done |

**Deliverable:** Public HuggingFace Space URL, updated blog post, final submission.

---

## 15. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Google Play scraper blocked by bot detection | Medium | High | Use `google-play-scraper` library (handles internally); add retry with exponential backoff via `tenacity` |
| No 7-day baseline data in first week | High | Medium | Supplement with public Kaggle datasets for historical data; clearly note limitation in report |
| Gemini API rate limits exceeded | Low | High | Cache generated reports in SQLite; add `time.sleep()` between API calls |
| SteamSpy API unavailable | Medium | Low | System designed to degrade gracefully; Steam API alone is sufficient |
| Reddit API auth fails | Low | Medium | Reddit sentiment is supplementary; set `sentiment_shift = 0.0` as fallback |
| HuggingFace free tier timeout | Medium | Medium | Keep Gradio app stateless; reduce default `count` parameters for faster responses |
| Evaluator LLM returns malformed JSON | Medium | Medium | Wrap in try/except; assign score of 0 and trigger revision on parse failure |
| LangChain agent hits max_iterations | Low | High | Set `max_iterations=10`; design tools to be efficient and complete in 6–8 steps |

---

## 16. Team Responsibility Matrix

| Component | Primary Owner | Secondary |
|-----------|--------------|-----------|
| `collectors/mobile_apps.py` | Uygar | — |
| `collectors/mobile_games.py` | Uygar | — |
| `collectors/pc_games.py` | Uygar | — |
| `collectors/reddit_sentiment.py` | Uygar | — |
| `analysis/trend_score.py` | Uygar | — |
| `analysis/cross_platform.py` | Uygar | Buğra |
| `analysis/snapshot.py` | Uygar | — |
| `database/` | Uygar | — |
| `visualization/charts.py` | Uygar | — |
| `agent/tools.py` | Buğra | — |
| `agent/react_agent.py` | Buğra | — |
| `agent/prompts.py` | Buğra | — |
| `reporting/generator.py` | Buğra | — |
| `reporting/evaluator.py` | Buğra | — |
| `reporting/revision.py` | Buğra | — |
| `app.py` (Gradio UI) | Buğra | — |
| HuggingFace Spaces deployment | Buğra | Uygar |
| Unit tests | Both | — |
| Blog post updates | Both | — |

---

## 17. Definition of Done

The project is complete when all of the following are true:

- [ ] All four data sources return live data (Google Play, App Store, Steam, Reddit)
- [ ] Trend scores are computed for all three market categories
- [ ] Cross-platform pattern detection identifies shared titles and genres
- [ ] Gemini 1.5 Pro generates a structured report with all required sections
- [ ] Gemini 1.5 Flash evaluates reports against the 5-criteria rubric
- [ ] Revision loop operates correctly with max 2 attempts
- [ ] At least 2 chart types render correctly in the Gradio UI
- [ ] The HuggingFace Space is publicly accessible and responds to queries within 60 seconds
- [ ] All 4 example queries produce non-empty reports
- [ ] Unit tests pass for trend score computation and evaluator JSON parsing
- [ ] Blog post is updated with the live demo link and a development retrospective
- [ ] MS Teams submission link is submitted before May 31, 2026

---

*Last updated: May 2026 · Agentic AI Systems Course*
