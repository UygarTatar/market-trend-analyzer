import os
import sys
import math
import pandas as pd
from datetime import datetime

# Add the parent directory to the path so we can import from database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection

def calculate_trend_score(rank: int, rating: float, sentiment_score: float, review_count: int) -> float:
    """
    Calculate the unified Trend Score for an entity.
    Formula: TrendScore = (W1 * NormalizedRank) + (W2 * Rating) + (W3 * SentimentScore) + (W4 * log(ReviewCount))
    """
    W1, W2, W3, W4 = 0.4, 0.2, 0.3, 0.1
    
    # Handle missing/mock sentiment
    if sentiment_score == 0:
        sentiment_score = 0.5
        
    # Normalize Rank: 1.0 / rank (prevents division by zero, rank 1 gets highest score)
    normalized_rank = 1.0 / rank if rank and rank > 0 else 0.0
    
    # Ensure rating is treated safely
    safe_rating = float(rating) if pd.notnull(rating) else 0.0
    
    # Calculate log of review count
    safe_reviews = int(review_count) if pd.notnull(review_count) and review_count > 0 else 1
    log_reviews = math.log10(safe_reviews) if safe_reviews > 1 else 0.0
    
    # Calculate score
    score = (W1 * normalized_rank) + (W2 * safe_rating) + (W3 * sentiment_score) + (W4 * log_reviews)
    
    return round(score, 4)

def process_daily_trends():
    """
    Reads data from the snapshots table, calculates scores for each app/game,
    and writes the results into the trend_scores table.
    """
    conn = get_connection()
    
    # Drop and recreate trend_scores to apply any schema updates
    try:
        conn.execute("DROP TABLE IF EXISTS trend_scores")
        # Initialize schema to recreate the table with the new app_id and title columns
        from database.db import _initialize_schema
        _initialize_schema(conn)
    except Exception as e:
        print(f"Schema update notice: {e}")
        
    query = "SELECT * FROM snapshots"
    df = pd.read_sql(query, conn)
    
    if df.empty:
        print("No data in snapshots to process.")
        conn.close()
        return

    # Calculate scores
    scores_list = []
    now = datetime.now()
    
    for _, row in df.iterrows():
        # Sentiment is not available per app in snapshots, default to 0
        score = calculate_trend_score(
            rank=row.get('rank', 0),
            rating=row.get('rating', 0.0),
            sentiment_score=0.0, 
            review_count=row.get('reviews', 0)
        )
        
        scores_list.append({
            'app_id': row.get('app_id'),
            'title': row.get('title'),
            'category': row.get('category', 'unknown'),
            'trend_score': score,
            'rank_change_avg': 0.0,
            'review_delta': 0.0,
            'sentiment_shift': 0.0,
            'computed_at': now
        })
        
    scores_df = pd.DataFrame(scores_list)
    
    # Write to database
    scores_df.to_sql('trend_scores', conn, if_exists='append', index=False)
    conn.close()
    
    print(f"Successfully processed {len(scores_df)} daily trend scores.")

if __name__ == "__main__":
    # Dry-test with 5 dummy records
    print("--- Running Dry-Test for Trend Scoring Engine ---")
    dummy_data = [
        {"app_id": "app.1", "title": "Game A", "rank": 1, "rating": 4.5, "sentiment_score": 0.8, "review_count": 10000},
        {"app_id": "app.2", "title": "App B", "rank": 10, "rating": 4.0, "sentiment_score": 0.0, "review_count": 500},
        {"app_id": "app.3", "title": "Game C", "rank": 50, "rating": 3.2, "sentiment_score": -0.2, "review_count": 50},
        {"app_id": "app.4", "title": "App D", "rank": 5, "rating": 4.8, "sentiment_score": 0.9, "review_count": 1000000},
        {"app_id": "app.5", "title": "Game E", "rank": 100, "rating": 2.5, "sentiment_score": 0.0, "review_count": 10},
    ]
    
    for item in dummy_data:
        score = calculate_trend_score(
            rank=item["rank"],
            rating=item["rating"],
            sentiment_score=item["sentiment_score"],
            review_count=item["review_count"]
        )
        print(f"[{item['title']}] Rank: {item['rank']}, Rating: {item['rating']}, Reviews: {item['review_count']}, Sentiment: {item['sentiment_score']} -> Trend Score: {score}")
    
    # Optionally, we can also test the full pipeline if we want
    # process_daily_trends()
