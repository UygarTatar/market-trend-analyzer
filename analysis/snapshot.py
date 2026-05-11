import pandas as pd
from database.db import get_connection

def save_snapshot(df: pd.DataFrame, category: str):
    """Save a market snapshot to the database, ensuring only valid columns are saved."""
    if df.empty:
        return
    
    # Work on a copy to prevent mutation issues
    df_copy = df.copy()
    
    conn = get_connection()
    df_copy["category"] = category
    df_copy["snapshot_date"] = pd.Timestamp.now().date()
    
    # --- SCHEMA SHIELD 2.0 ---
    cursor = conn.execute("PRAGMA table_info(snapshots);")
    db_cols = [row[1] for row in cursor.fetchall()]
    
    # Intersection of what we have and what DB wants
    cols_to_save = [c for c in df_copy.columns if c in db_cols]
    
    print(f"[DB DEBUG] Table snapshots columns: {db_cols}")
    print(f"[DB DEBUG] Saving columns: {cols_to_save}")
    
    df_final = df_copy[cols_to_save]
    df_final.to_sql("snapshots", conn, if_exists="append", index=False)
    conn.close()

def load_snapshot(category: str, days_ago: int = 7) -> pd.DataFrame:
    """Load a snapshot from N days ago."""
    conn = get_connection()
    target_date = (pd.Timestamp.now() - pd.Timedelta(days=days_ago)).date()
    query = "SELECT * FROM snapshots WHERE category = ? AND snapshot_date = ?"
    df = pd.read_sql(query, conn, params=[category, target_date])
    conn.close()
    return df
