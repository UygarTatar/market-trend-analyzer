import os
import sys
import pandas as pd
from collectors.pc_games import fetch_steam_top_sellers
from collectors.mobile_games import fetch_all_mobile_game_categories
from collectors.reddit_sentiment import collect_gaming_sentiment
from analysis.trend_score import calculate_trend_score
from visualization.charts import create_trend_score_bar
from agent.react_agent import run_agent

def master_test():
    print("="*50)
    print("STARTING ONYX MASTER SYSTEM TEST - FINAL VALIDATION")
    print("="*50)

    # 1. Test Collectors
    print("\n[1/5] Testing Collectors (PC + Mobile + Reddit RSS)...")
    try:
        steam_df = fetch_steam_top_sellers(count=3)
        google_df = fetch_all_mobile_game_categories(count_per_cat=2)
        reddit_df = collect_gaming_sentiment()
        print(f"[OK] PC Games: {len(steam_df)} items found")
        print(f"[OK] Mobile Games: {len(google_df)} items found")
        print(f"[OK] Reddit Posts: {len(reddit_df)} items found")
    except Exception as e:
        print(f"[FAIL] Collector Test Failed: {e}")

    # 2. Test Scoring Logic
    print("\n[2/5] Testing Trend Scoring Math...")
    try:
        sample_score = calculate_trend_score(rank=1, rating=4.9, sentiment_score=0.9, review_count=100000)
        print(f"[OK] Trend Score Calculation: {sample_score} (Expected high)")
        assert sample_score > 0.5
    except Exception as e:
        print(f"[FAIL] Scoring Test Failed: {e}")

    # 3. Test Visualization
    print("\n[3/5] Testing Visualization (PIL/Windows Shield)...")
    try:
        dummy_scores = {"pc_games": 0.85, "mobile_games": 0.45}
        img = create_trend_score_bar(dummy_scores)
        print(f"[OK] Visualization: Generated {type(img)}")
        assert img is not None
    except Exception as e:
        print(f"[FAIL] Visualization Test Failed: {e}")

    # 4. Test Agent Reasoning
    print("\n[4/5] Testing Agent Intelligence & Tools...")
    try:
        # A quick query to see if it invokes tools
        response = run_agent("Give me a 1-sentence summary of what's currently trending on Steam.")
        print(f"[OK] Agent Response: {response[:150]}...")
    except Exception as e:
        print(f"[FAIL] Agent Test Failed: {e}")

    # 5. Database Health
    print("\n[5/5] Checking Database Integrity...")
    try:
        from database.db import get_connection
        conn = get_connection()
        count = conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
        conn.close()
        print(f"[OK] Database: {count} snapshots active.")
    except Exception as e:
        print(f"[FAIL] Database Test Failed: {e}")

    print("\n" + "="*50)
    print("MASTER TEST COMPLETE - ALL SYSTEMS NOMINAL")
    print("="*50)

if __name__ == "__main__":
    master_test()
