import sys
import os

# Add the project root to sys.path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.tools import tool
from collectors import mobile_apps, mobile_games, pc_games, reddit_sentiment
from analysis import snapshot, trend_score

@tool
def collect_mobile_app_data(country: str = "us") -> str:
    """
    Use this tool to collect current top mobile app rankings from Google Play and the Apple App Store.
    It scrapes live app data and saves the result to the database as snapshots.
    """
    # Sanitize input
    country = str(country).strip().strip("'").strip('"')
    gp_df = mobile_apps.fetch_google_play_top_apps(count=50, country=country)
    ios_df = mobile_apps.fetch_app_store_top_apps(count=50, country=country)
    
    snapshot.save_snapshot(gp_df, "mobile_apps_android")
    snapshot.save_snapshot(ios_df, "mobile_apps_ios")
    
    return f"Successfully collected {len(gp_df)} Android apps and {len(ios_df)} iOS apps for region '{country}'."

@tool
def collect_mobile_game_data(country: str = "us") -> str:
    """
    Use this tool to collect current top mobile game rankings across all major genres.
    It hits both Google Play and the App Store, and saves the data as a DB snapshot.
    """
    # Sanitize input
    country = str(country).strip().strip("'").strip('"')
    df = mobile_games.fetch_all_mobile_game_categories(count_per_cat=20, country=country)
    snapshot.save_snapshot(df, "mobile_games")
    return f"Successfully collected {len(df)} mobile games across genres and saved snapshot to DB."

@tool
def collect_pc_game_data(query: str = "top sellers") -> str:
    """
    Use this tool to fetch live rankings and detailed metadata for top-selling PC games from Steam.
    It gathers metadata like price, rating, and genres, then saves the snapshot to the DB.
    """
    df = pc_games.fetch_pc_games_with_details(count=50)
    snapshot.save_snapshot(df, "pc_games")
    return f"Successfully collected {len(df)} Steam PC games and saved snapshot to DB."

@tool
def compute_category_trends(category: str) -> str:
    """
    Use this tool to calculate and update trend scores for the data.
    Takes a category name and triggers the trend scoring engine to read snapshots 
    from the database and write out the computed trend scores.
    """
    # Sanitize input
    category = str(category).strip().strip("'").strip('"')
    df = snapshot.load_snapshot(category, days_ago=0)
    
    # Process all trends in DB
    trend_score.process_daily_trends()
    
    return f"Successfully computed trend scores for category '{category}'."

@tool
def collect_reddit_sentiment(query: str = "general"):
    """
    Collects live community sentiment and trending discussions from gaming subreddits via RSS.
    No API key required. Use this to find what gamers are talking about.
    """
    try:
        df = reddit_sentiment.collect_gaming_sentiment()
        if df.empty:
            return "No recent Reddit discussions found."
        
        # Summarize the top 10 trending topics for the agent
        summary = "\n".join([f"- {row['title']} (r/{row['subreddit']})" for _, row in df.head(10).iterrows()])
        return f"Recent Trending Discussions on Reddit:\n{summary}"
    except Exception as e:
        return f"Error collecting Reddit data: {e}"

# Registry of all available tools for the LangChain agent
ALL_TOOLS = [
    collect_mobile_app_data,
    collect_mobile_game_data,
    collect_pc_game_data,
    compute_category_trends,
    collect_reddit_sentiment
]
