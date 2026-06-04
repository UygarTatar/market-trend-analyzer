import sqlite3
import os
from datetime import datetime, timedelta

def get_intelligence_stats():
    """Calculates high-level metrics for the Intelligence Hub dashboard."""
    db_path = os.getenv("DB_PATH", "database/market_analyzer.db")
    
    # Check if DB exists
    if not os.path.exists(db_path):
        return {
            "total_points": 0,
            "growth_24h": 0,
            "unique_apps": 0,
            "top_trends": []
        }

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. Total Data Points (Density)
        cursor.execute("SELECT COUNT(*) FROM snapshots")
        total_points = cursor.fetchone()[0]

        # 2. Last 24h Scouted (Freshness)
        # Using simple date comparison since fetched_at is a timestamp
        cursor.execute("SELECT COUNT(*) FROM snapshots WHERE fetched_at > datetime('now', '-1 day')")
        growth_24h = cursor.fetchone()[0]

        # 3. Unique Entities (Coverage)
        cursor.execute("SELECT COUNT(DISTINCT app_id) FROM snapshots")
        unique_apps = cursor.fetchone()[0]

        # 4. Top Trends (Velocity)
        cursor.execute("""
            SELECT title, trend_score 
            FROM trend_scores 
            ORDER BY trend_score DESC, computed_at DESC 
            LIMIT 3
        """)
        top_trends = [{"title": row[0], "score": row[1]} for row in cursor.fetchall()]

        conn.close()
        
        return {
            "total_points": total_points,
            "growth_24h": growth_24h,
            "unique_apps": unique_apps,
            "top_trends": top_trends
        }

    except Exception as e:
        print(f"[STATS ERROR] {e}")
        return {
            "total_points": "Error",
            "growth_24h": "Error",
            "unique_apps": "Error",
            "top_trends": []
        }
