import unittest
import pandas as pd
from collectors.pc_games import scrape_steam_top_sellers
from collectors.mobile_games import scrape_google_play_games

class TestCollectors(unittest.TestCase):
    """
    Basic connectivity and schema tests for the collectors.
    """
    
    def test_steam_scraper(self):
        print("\nTesting Steam Scraper...")
        df = scrape_steam_top_sellers(limit=5)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)
        self.assertIn('title', df.columns)
        self.assertIn('app_id', df.columns)

    def test_google_play_scraper(self):
        print("\nTesting Google Play Scraper...")
        # Only testing a small subset to avoid rate limits
        df = scrape_google_play_games(country='us', limit=5)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)
        self.assertIn('title', df.columns)
        self.assertIn('platform', df.columns)

if __name__ == "__main__":
    unittest.main()
