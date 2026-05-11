-- Market Trend Analyzer — SQLite Schema
-- Initialized automatically by database/db.py on first connection

CREATE TABLE IF NOT EXISTS snapshots (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id        TEXT NOT NULL,
    title         TEXT,
    category      TEXT NOT NULL,       -- 'mobile_apps', 'mobile_games', 'pc_games'
    platform      TEXT,                -- 'android', 'ios', 'pc_steam'
    genre         TEXT,
    rank          INTEGER,
    rating        REAL,
    reviews       INTEGER,
    installs      TEXT,
    snapshot_date DATE NOT NULL,
    fetched_at    TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS trend_scores (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id          TEXT,
    title           TEXT,
    category        TEXT NOT NULL,
    trend_score     REAL,
    rank_change_avg REAL,
    review_delta    REAL,
    sentiment_shift REAL,
    computed_at     TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS reports (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    query       TEXT,
    report_text TEXT,
    eval_score  REAL,
    attempts    INTEGER,
    created_at  TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_snapshots_category_date
    ON snapshots(category, snapshot_date);
