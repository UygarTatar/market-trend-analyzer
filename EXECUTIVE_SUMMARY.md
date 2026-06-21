# 🌌 ONYX: Agentic Market Intelligence System
## Executive Summary

**Course:** Agentic AI Systems (Term Project)  
**Team Members:** Uygar Tatar (Student ID: 2202400) & Muhammed Buğra Çiftçi (Student ID: 2101860)  
**Project Deployment:** [HuggingFace Spaces (Gradio)](https://huggingface.co/spaces/UygarTatar/market-trend-analyzer)

---

### 1. The Vision and Problem Statement
In the fast-moving digital economy, understanding cross-platform trends in mobile and PC gaming/apps is critical for product managers, indie developers, and marketing analysts. However, existing market intelligence solutions (such as AppMagic, SensorTower, and data.ai) are gated behind prohibitively expensive enterprise pricing. Furthermore, existing pipelines require manual dashboard consolidation and reporting, leading to slow and error-prone decision cycles.

**ONYX** is an autonomous, end-to-end data engineering and agentic intelligence platform designed to scout, analyze, and report on digital market opportunities across the global app and gaming ecosystem. By leverage free, public data sources and combining them with state-of-the-art Large Language Models (LLMs), ONYX automates the entire lifecycle of market analysis.

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
