# Directive: Trend Scoring Engine

**Goal:** Create the core logic to calculate a unified "Trend Score" for all tracked entities.

**Inputs:** Refer to `project_plan.md` Section 5.1 (Trend Calculation Logic).
**Outputs:** 
1. Create `analysis/trend_score.py`.

**Rules:**
- Implement a function `calculate_trend_score(rank, rating, sentiment_score, review_count)` based on the project formula.
- **The Formula:** $TrendScore = (W1 \times NormalizedRank) + (W2 \times Rating) + (W3 \times SentimentScore) + (W4 \times \log(ReviewCount))$
- Use weights: $W1=0.4, W2=0.2, W3=0.3, W4=0.1$.
- Handle edge cases: If `sentiment_score` is 0 (mock/missing), use a neutral baseline of 0.5.
- Create a `process_daily_trends()` function that reads data from the `snapshots` table in SQLite, calculates scores for each app/game, and writes the results into the `trend_scores` table.
- Use `pandas` for all data transformations.
- At the bottom, add an `if __name__ == "__main__":` block to run a dry-test with 5 dummy records and print the calculated Trend Scores.

**Known edge cases (learned during execution):**
- `NormalizedRank` Division-by-Zero: Since rank 1 is best, the raw rank needs inverse normalization. Handled by enforcing `1.0 / rank` only when `rank > 0`, and defaulting to `0.0` otherwise.
- `review_count` Math Errors: Since $\log(0)$ is undefined, safely handling reviews $\le 1$ by treating them as resulting in a log score of `0.0`.
- Missing `rating` Values: Handled missing or `NaN` ratings by defaulting them to `0.0` before computing the formula.
- Schema Extensibility: The `trend_scores` table originally only tracked category-level trends. Added `app_id` and `title` columns to `schema.sql` so the engine can save individual app/game scores.

**Status: COMPLETE** — `analysis/trend_score.py` created and verified. Trend Score calculation formula and database ingestion successfully deployed and tested.