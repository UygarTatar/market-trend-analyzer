import pandas as pd
from collections import Counter

def detect_overlap(category_results: dict) -> dict:
    """
    Identify apps/games appearing across platforms and detect shared genre trends.

    Parameters
    ----------
    category_results : dict — Keys are 'mobile_apps', 'mobile_games', 'pc_games'.
                       Each value is a DataFrame of top items for that category.
    
    Returns
    -------
    dict with title overlaps and genre trends.
    """
    # 1. Edge Case: Handle empty or missing DataFrames
    for cat in ["mobile_apps", "mobile_games", "pc_games"]:
        if cat not in category_results or category_results[cat] is None:
            category_results[cat] = pd.DataFrame(columns=["title", "genre"])
        if category_results[cat].empty:
            # Ensure columns exist even if empty
            if "title" not in category_results[cat].columns:
                category_results[cat]["title"] = []
            if "genre" not in category_results[cat].columns:
                category_results[cat]["genre"] = []

    # 2. Title-based overlap (same game on mobile + PC)
    # Note: Using .str.lower() to ensure case-insensitive matching
    mobile_titles = set(category_results["mobile_games"]["title"].dropna().str.lower())
    pc_titles = set(category_results["pc_games"]["title"].dropna().str.lower())
    cross_platform_titles = mobile_titles & pc_titles

    # 3. Genre trend overlap
    genre_trends = {}
    for category, df in category_results.items():
        if "genre" in df.columns and not df["genre"].dropna().empty:
            top_genre = df["genre"].value_counts().idxmax()
            genre_trends[category] = top_genre
        else:
            genre_trends[category] = "Unknown"

    # 4. Overall shared genre trend
    shared_genre = _find_shared_genre(genre_trends)

    return {
        "cross_platform_titles": sorted(list(cross_platform_titles)),
        "dominant_genre_per_category": genre_trends,
        "shared_genre_trend": shared_genre,
        "overlap_count": len(cross_platform_titles)
    }

def _find_shared_genre(genre_trends: dict) -> str:
    """
    Find the most common genre across the different category trends.
    """
    all_genres = [g for g in genre_trends.values() if g != "Unknown"]
    if not all_genres:
        return "N/A"
    
    counts = Counter(all_genres)
    return counts.most_common(1)[0][0]

if __name__ == "__main__":
    # Dry-test with mock data
    print("--- Starting Cross-Platform Analysis Dry-Test ---")
    
    mock_data = {
        "mobile_apps": pd.DataFrame({
            "title": ["Instagram", "TikTok", "Discord"],
            "genre": ["Social", "Social", "Communication"]
        }),
        "mobile_games": pd.DataFrame({
            "title": ["Minecraft", "Roblox", "Genshin Impact", "PUBG Mobile"],
            "genre": ["Sandbox", "Sandbox", "RPG", "Action"]
        }),
        "pc_games": pd.DataFrame({
            "title": ["Minecraft", "Elden Ring", "Roblox", "Cyberpunk 2077"],
            "genre": ["Sandbox", "RPG", "Sandbox", "RPG"]
        })
    }
    
    result = detect_overlap(mock_data)
    
    print("\n--- Overlap Results ---")
    print(f"Cross-Platform Titles: {result['cross_platform_titles']}")
    print(f"Dominant Genre per Category: {result['dominant_genre_per_category']}")
    print(f"Overall Shared Genre Trend: {result['shared_genre_trend']}")
    print(f"Total Overlap Count: {result['overlap_count']}")
    
    # Test with empty data
    print("\n--- Empty Data Test ---")
    empty_result = detect_overlap({"mobile_apps": pd.DataFrame()})
    print(f"Empty results handled: {empty_result['shared_genre_trend'] == 'N/A'}")
