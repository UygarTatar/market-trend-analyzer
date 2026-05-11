import os
import sys
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors import mobile_apps, mobile_games, pc_games, reddit_sentiment
from analysis import snapshot, trend_score

def run_daily_collection():
    print(f"--- Starting Daily Collection: {datetime.now()} ---")
    
    # 1. PC Games
    try:
        print("[1/4] Collecting PC Games...")
        df_pc = pc_games.fetch_pc_games_with_details(count=50)
        snapshot.save_snapshot(df_pc, "pc_games")
    except Exception as e:
        print(f"Error collecting PC games: {e}")

    # 2. Mobile Apps
    try:
        print("[2/4] Collecting Mobile Apps...")
        gp_apps = mobile_apps.fetch_google_play_top_apps(count=50)
        ios_apps = mobile_apps.fetch_app_store_top_apps(count=50)
        snapshot.save_snapshot(gp_apps, "mobile_apps_android")
        snapshot.save_snapshot(ios_apps, "mobile_apps_ios")
    except Exception as e:
        print(f"Error collecting mobile apps: {e}")

    # 3. Mobile Games
    try:
        print("[3/4] Collecting Mobile Games...")
        df_games = mobile_games.fetch_all_mobile_game_categories(count_per_cat=20)
        snapshot.save_snapshot(df_games, "mobile_games")
    except Exception as e:
        print(f"Error collecting mobile games: {e}")

    # 4. Reddit Sentiment (RSS)
    try:
        print("[4/4] Collecting Reddit Sentiment...")
        # Note: We save reddit posts to a different table or logic if needed, 
        # but for now we just trigger the collection to verify health.
        df_reddit = reddit_sentiment.collect_gaming_sentiment()
        print(f"Collected {len(df_reddit)} Reddit posts.")
    except Exception as e:
        print(f"Error collecting Reddit: {e}")

    # 5. Process Trends
    try:
        print("[TRENDS] Computing daily trend scores...")
        trend_score.process_daily_trends()
    except Exception as e:
        print(f"Error processing trends: {e}")

    print(f"--- Collection Complete: {datetime.now()} ---")

if __name__ == "__main__":
    run_daily_collection()
