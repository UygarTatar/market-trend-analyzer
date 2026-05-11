import unittest
from analysis.trend_score import calculate_trend_score

class TestTrendScore(unittest.TestCase):
    """
    Test the Trend Score calculation logic and weights.
    """
    
    def test_rank_influence(self):
        # Rank 1 should be significantly higher than Rank 100 with same other stats
        high_rank = calculate_trend_score(rank=1, rating=4.0, sentiment_score=0.5, review_count=1000)
        low_rank = calculate_trend_score(rank=100, rating=4.0, sentiment_score=0.5, review_count=1000)
        self.assertGreater(high_rank, low_rank)
        
    def test_rating_influence(self):
        # 5.0 rating should be higher than 1.0 rating
        high_rating = calculate_trend_score(rank=10, rating=5.0, sentiment_score=0.5, review_count=1000)
        low_rating = calculate_trend_score(rank=10, rating=1.0, sentiment_score=0.5, review_count=1000)
        self.assertGreater(high_rating, low_rating)

    def test_review_count_log(self):
        # 1M reviews should be higher than 10 reviews
        high_reviews = calculate_trend_score(rank=10, rating=4.0, sentiment_score=0.5, review_count=1000000)
        low_reviews = calculate_trend_score(rank=10, rating=4.0, sentiment_score=0.5, review_count=10)
        self.assertGreater(high_reviews, low_reviews)

    def test_zero_rank_safety(self):
        # Rank 0 or None should return a score (likely based on 0.0 normalization)
        score = calculate_trend_score(rank=0, rating=4.0, sentiment_score=0.5, review_count=1000)
        self.assertGreaterEqual(score, 0)

if __name__ == "__main__":
    unittest.main()
