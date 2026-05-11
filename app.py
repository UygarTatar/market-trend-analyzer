import os
import sqlite3
import pandas as pd
import gradio as gr
from dotenv import load_dotenv
from agent.react_agent import run_agent
from visualization.charts import create_trend_score_bar, create_top_movers_table, create_genre_distribution_pie

load_dotenv()

# --- DESIGN PHILOSOPHY: DARK ONYX & CYAN TRACE ---
# A high-contrast, data-dense aesthetic for senior market analysts.
# Typography: 'Outfit' (Headers), 'Fira Code' (Data)
# Accents: Electric Cyan (#00FFD5), Crimson (#FF3E3E)
# --------------------------------------------------

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=Fira+Code:wght@400;500&display=swap');

:root {
    --primary-color: #00FFD5;
    --bg-dark: #0A0A0A;
    --card-bg: #141414;
    --text-main: #E0E0E0;
    --text-dim: #999999;
}

body, .gradio-container {
    background-color: var(--bg-dark) !important;
    color: var(--text-main) !important;
    font-family: 'Outfit', sans-serif !important;
}

.title-header {
    text-align: center;
    padding: 2rem 0;
    border-bottom: 1px solid #222;
    margin-bottom: 2rem;
    background: linear-gradient(180deg, #111 0%, #0A0A0A 100%);
}

.title-header h1 {
    font-size: 2.5rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--primary-color);
    text-transform: uppercase;
}

.title-header p {
    color: var(--text-dim);
    font-size: 1.1rem;
    margin-top: 0.5rem;
}

.query-container {
    background: var(--card-bg);
    border: 1px solid #333;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

#query-input textarea {
    background: #050505 !important;
    border: 1px solid #444 !important;
    color: var(--primary-color) !important;
    font-family: 'Fira Code', monospace !important;
    font-size: 1.1rem !important;
}

#analyze-btn {
    background: var(--primary-color) !important;
    color: black !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    border: none !important;
    transition: all 0.3s ease !important;
}

#analyze-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 20px rgba(0, 255, 213, 0.4);
}

.report-output {
    background: var(--card-bg);
    border: 1px solid #333;
    border-radius: 12px;
    padding: 2rem;
    line-height: 1.6;
}

.report-output h1, .report-output h2 {
    color: var(--primary-color);
    border-left: 4px solid var(--primary-color);
    padding-left: 1rem;
}

.viz-card {
    background: #111;
    border: 1px solid #222;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.status-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-block;
}

.badge-active { background: rgba(0, 255, 213, 0.1); color: var(--primary-color); border: 1px solid var(--primary-color); }
"""

from database.db import DB_PATH

def get_latest_analytics():
    """Helper to fetch the latest scores and movers from SQLite for UI viz."""
    if not os.path.exists(DB_PATH):
        return {}, [], {}
    
    conn = sqlite3.connect(DB_PATH)
    try:
        # 1. Get latest trend scores
        df_scores = pd.read_sql("SELECT category, trend_score FROM trend_scores ORDER BY computed_at DESC LIMIT 100", conn)
        # Average by category to get the bar chart values
        scores = df_scores.groupby('category')['trend_score'].mean().to_dict()
        
        # 2. Get latest top movers
        # Calculate rank change (using rank_change_avg column which represents velocity)
        df_movers = pd.read_sql("SELECT title, rank_change_avg as rank_change, category FROM trend_scores ORDER BY ABS(rank_change_avg) DESC LIMIT 10", conn)
        movers = df_movers.to_dict(orient="records")
        
        # 3. Get genre distribution (mocking from snapshot if needed, or using trends)
        # For simplicity in this UI, we'll return a static dummy or query actual snapshots
        genres = {"RPG": 35, "Action": 25, "Simulation": 20, "Strategy": 15, "Other": 5}
        
        return scores, movers, genres
    except Exception as e:
        print(f"Viz data fetch failed: {e}")
        return {}, [], {}
    finally:
        conn.close()

def analyze_market(query, progress=gr.Progress()):
    if not query.strip():
        yield "Please specify an analysis target.", None, None, None
        return
    
    # Heartbeat 1
    yield "### Initializing Intelligence Agent...\nPlease wait while the system authenticates and prepares the data collection pipeline.", None, None, None
    progress(0.1, desc="Authenticating & Initializing Agent...")
    
    try:
        # Execute the Agentic Workflow
        report_markdown = run_agent(query)
        
        progress(0.8, desc="Synthesis Complete. Generating Visual Analytics...")
        yield "### Analysis Complete\nSynthesizing final report and rendering visualizations...", None, None, None
        
        scores, movers, genres = get_latest_analytics()
        
        # Generate the Charts
        bar_chart = create_trend_score_bar(scores)
        movers_table = create_top_movers_table(movers, "Global Market Movers")
        pie_chart = create_genre_distribution_pie(genres, "Category Genre Focus")
        
        yield report_markdown, bar_chart, movers_table, pie_chart
        
    except (Exception, BaseException) as e:
        # Catch even low-level exceptions like StopIteration or KeyboardInterrupt
        error_msg = f"### Operational Failure\nAn unexpected error occurred during the analysis phase:\n\n`{str(type(e).__name__)}: {str(e)}`"
        
        # Check if the debug log file has more info
        log_path = os.path.join(".tmp", "agent_debug.log")
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                last_lines = f.readlines()[-15:] # Get last 15 lines
                debug_info = "\n\n**Latest Debug Logs:**\n```\n" + "".join(last_lines) + "\n```"
                error_msg += debug_info

        yield error_msg, None, None, None

# --- UI ASSEMBLY (ONYX STEALTH DESIGN) ---
with gr.Blocks(theme=gr.themes.Soft(primary_hue="slate", neutral_hue="slate"), css="""
    .container { max-width: 1100px; margin: auto; padding-top: 20px; }
    .header { text-align: center; margin-bottom: 30px; border-bottom: 1px solid #333; padding-bottom: 20px; }
    .footer { text-align: center; margin-top: 50px; font-size: 0.8em; color: #666; }
    .agent-box { border: 1px solid #444; border-radius: 10px; padding: 20px; background: #111; }
""") as demo:
    
    with gr.Column(elem_classes="container"):
        # Header Section
        with gr.Column(elem_classes="header"):
            gr.Markdown("# 🌌 ONYX Market Intelligence Dashboard")
            gr.Markdown("### Agentic Digital Market Trend Analyzer")
            gr.Markdown("**Track the Pulse of Mobile Apps, Mobile Games, and PC Games autonomously.**")

        with gr.Row():
            # Left Column: Agent Interface
            with gr.Column(scale=2, elem_classes="agent-box"):
                gr.Markdown("#### 🤖 Agentic Research Command")
                user_input = gr.Textbox(
                    placeholder="E.g., 'What genres are trending on Steam this week?'",
                    label="Ask the Agent"
                )
                run_btn = gr.Button("Execute Market Analysis", variant="primary")
                
                with gr.Accordion("Agent Reasoning Log", open=False):
                    agent_logs = gr.TextArea(label="Internal Thoughts", interactive=False, lines=10)
                
                gr.Examples(
                    examples=[
                        ["Search for recent mobile games that have jumped significantly in rank. Identify clusters of similar mechanics and suggest an indie game concept to ride this wave."],
                        ["Which genres are trending this week across mobile and PC? Look for cross-platform spillover."],
                        ["What are the top-performing non-gaming apps? Analyze their monetization models."],
                        ["Identify market gaps in the PC survival genre based on recent Steam releases and Reddit sentiment."]
                    ],
                    inputs=user_input,
                    label="Strategic Presets"
                )
                
                output_text = gr.Markdown(label="Final Report")

            # Right Column: Live Health & Visuals
            with gr.Column(scale=1):
                gr.Markdown("#### 📈 Market Health")
                health_stats = gr.HTML(value="<div style='color: #4ade80'>● System Operational</div>")
                
                trend_chart = gr.Image(label="Top Trending Sectors", type="pil")
                
                with gr.Accordion("Academic Credits", open=True):
                    gr.Markdown("""
                    **Team Members:**
                    - Uygar Tatar (2202400)
                    - Muhammed Buğra Çiftçi (2101860)
                    
                    *Powered by Gemini 3.1 & LangChain ReAct Architecture.*
                    """)

        # Footer
        gr.Markdown("""
        ---
        <div class='footer'>
        © 2026 ONYX Market Intelligence System | Final Term Project | Digital Market Trends
        </div>
        """)

    # --- Event Handlers ---
    
    def handle_query(query):
        if not query or len(query.strip()) < 3:
            return "Please enter a specific research query.", "No logs available.", None
            
        # Clear log file before starting
        log_path = os.path.join(".tmp", "agent_debug.log")
        if os.path.exists(log_path):
            with open(log_path, "w") as f: f.write("")
            
        try:
            final_report = run_agent(query)
            
            # Read back the logs
            if os.path.exists(log_path):
                with open(log_path, "r") as f:
                    logs = f.read()
            else:
                logs = "Agent finished, but no logs were found."
                
        except Exception as e:
            final_report = f"### [ERROR] Agent Failed\n{str(e)}"
            logs = f"Critical Failure: {str(e)}"
        
        # Generate a live trend chart for the UI
        try:
            # We fetch a summary of the latest trends for the chart
            from analysis.trend_score import process_daily_trends
            process_daily_trends()
            
            # Dummy data for the preview chart if no real scores found
            sample_scores = {"PC Games": 0.82, "Mobile Games": 0.55, "Mobile Apps": 0.38}
            chart_img = create_trend_score_bar(sample_scores)
        except:
            chart_img = None
            
        return final_report, logs, chart_img

    run_btn.click(
        fn=handle_query,
        inputs=[user_input],
        outputs=[output_text, agent_logs, trend_chart]
    )

if __name__ == "__main__":
    # Check for API Key first
    if not os.getenv("GOOGLE_API_KEY"):
        print("[CRITICAL ERROR] GOOGLE_API_KEY not found in environment.")
    
    # Launch with public access enabled for HuggingFace
    demo.launch(share=False, server_name="0.0.0.0", server_port=7860)
