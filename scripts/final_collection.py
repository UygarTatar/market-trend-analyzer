import sys
import os
from agent.tools import collect_mobile_app_data, collect_mobile_game_data, collect_pc_game_data, compute_category_trends

def main():
    print("--- STARTING MASTER COLLECTION ---")
    
    print("\n[1/4] Scraping Mobile Apps (Global)...")
    res1 = collect_mobile_app_data.invoke({"country": "us"})
    print(f"Result: {res1}")
    
    print("\n[2/4] Scraping Mobile Games (All Genres)...")
    res2 = collect_mobile_game_data.invoke({"country": "us"})
    print(f"Result: {res2}")
    
    print("\n[3/4] Scraping PC Games (Steam Top Sellers)...")
    res3 = collect_pc_game_data.invoke({"query": "top sellers"})
    print(f"Result: {res3}")
    
    print("\n[4/4] Computing Global Trend Scores...")
    res4 = compute_category_trends.invoke({"category": "mobile_games"})
    res5 = compute_category_trends.invoke({"category": "pc_games"})
    res6 = compute_category_trends.invoke({"category": "mobile_apps"})
    print("Trend scores successfully updated in database.")
    
    print("\n--- MASTER COLLECTION COMPLETE ---")

if __name__ == "__main__":
    main()
