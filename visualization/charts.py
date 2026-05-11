import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
from visualization.templates import COLORS, MPL_STYLE, PLOTLY_DARK_LAYOUT

def create_trend_score_bar(category_scores: dict):
    """
    Generate a static Matplotlib bar chart comparing trend scores.
    Returns a PIL Image object.
    """
    if not category_scores:
        return None

    # Apply ONYX Style
    plt.rcParams.update(MPL_STYLE)
    
    # Clean up names for display
    display_names = {
        "mobile_apps_android": "Mobile Apps (Android)",
        "mobile_apps_ios": "Mobile Apps (iOS)",
        "pc_games": "PC Games (Steam)",
        "mobile_games": "Mobile Games"
    }
    
    categories = [display_names.get(k, k) for k in category_scores.keys()]
    scores = list(category_scores.values())
    
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(categories, scores, color=COLORS["success"], alpha=0.8)
    
    # Add neon glow effect
    for bar in bars:
        bar.set_edgecolor(COLORS["accent_primary"])
        bar.set_linewidth(1.5)
    
    ax.axhline(y=0, color="white", linewidth=0.8, linestyle="--")
    
    ax.set_title("7-Day Trend Scores by Category", fontsize=14, fontweight="bold", pad=20)
    ax.set_ylabel("Normalized Trend Score (-1.0 to 1.0)")
    ax.set_ylim(-1.1, 1.1)
    
    # Grid lines for better readability
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Save to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    plt.close()
    buf.seek(0)
    
    # Return as PIL Image object
    return Image.open(buf)

def create_top_movers_table(top_movers: list, category: str) -> go.Figure:
    """
    Generate an interactive Plotly table of top-moving items.
    """
    if not top_movers:
        # Return an empty figure with a notice
        fig = go.Figure()
        fig.add_annotation(text="No significant movers detected in this period.", 
                           showarrow=False, font=dict(size=16))
        return fig

    df = pd.DataFrame(top_movers)
    
    # Format the rank change as a readable string
    if "rank_change" in df.columns:
        # Check if it's already a string or numeric
        if pd.api.types.is_numeric_dtype(df["rank_change"]):
            df["rank_change"] = (df["rank_change"] * 100).round(1).astype(str) + "%"

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["<b>Title</b>", "<b>Rank Shift</b>"],
            fill_color="#1E3A5F",
            align="left",
            font=dict(color="white", size=13)
        ),
        cells=dict(
            values=[df["title"], df["rank_change"]],
            fill_color="#F5F5F5",
            align="left",
            font=dict(size=12)
        )
    )])
    
    fig.update_layout(
        **PLOTLY_DARK_LAYOUT,
        title=f"Market Velocity - {category}",
        margin=dict(l=10, r=10, t=40, b=10),
        height=300
    )
    return fig

def create_genre_distribution_pie(genre_counts: dict, title: str) -> go.Figure:
    """
    Generate an interactive Plotly pie chart for genre distribution.
    """
    if not genre_counts:
        # Return empty figure
        fig = go.Figure()
        fig.add_annotation(text="Insufficient data for genre distribution.", 
                           showarrow=False, font=dict(size=14))
        return fig

    labels = list(genre_counts.keys())
    values = list(genre_counts.values())
    
    fig = px.pie(
        names=labels, 
        values=values, 
        title=title, 
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    
    return fig

if __name__ == "__main__":
    # Dry-test with dummy data
    print("--- Starting Visualization Layer Dry-Test ---")
    
    # 1. Test Trend Bar
    dummy_scores = {"mobile_apps": 0.82, "mobile_games": -0.15, "pc_games": 0.45}
    b64_img = create_trend_score_bar(dummy_scores)
    print(f"Trend Bar Chart (Base64 Prefix): {b64_img[:50]}...")
    
    # 2. Test Top Movers Table
    dummy_movers = [
        {"title": "Genshin Impact", "rank_change": 0.25},
        {"title": "Minecraft", "rank_change": 0.12},
        {"title": "Roblox", "rank_change": -0.05}
    ]
    table_fig = create_top_movers_table(dummy_movers, "mobile_games")
    print(f"Top Movers Table Generated: {type(table_fig)}")
    
    # 3. Test Genre Pie
    dummy_genres = {"RPG": 45, "Action": 30, "Sandbox": 25}
    pie_fig = create_genre_distribution_pie(dummy_genres, "Mobile Game Genres")
    print(f"Genre Pie Chart Generated: {type(pie_fig)}")
    
    # 4. Test Empty Data
    empty_b64 = create_trend_score_bar({})
    print(f"Empty Bar handled (len): {len(empty_b64)}")
