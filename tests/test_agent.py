import unittest
from agent.tools import collect_pc_game_data, collect_mobile_game_data, compute_category_trends

class TestAgentTools(unittest.TestCase):
    """
    Verify that Agent tools are correctly defined and have the expected structure.
    """
    
    def test_tool_names(self):
        self.assertEqual(collect_pc_game_data.name, "collect_pc_game_data")
        self.assertEqual(collect_mobile_game_data.name, "collect_mobile_game_data")
        self.assertEqual(compute_category_trends.name, "compute_category_trends")
        
    def test_tool_invocation_args(self):
        # Tools should have defined input schemas
        self.assertIsNotNone(collect_pc_game_data.args_schema)
        self.assertIn("query", collect_pc_game_data.args)
        self.assertIn("category", compute_category_trends.args)

    def test_sanitizers(self):
        from agent.tools import _sanitize_country, _sanitize_category
        # Test country sanitizers
        self.assertEqual(_sanitize_country("us"), "us")
        self.assertEqual(_sanitize_country("US"), "us")
        self.assertEqual(_sanitize_country("country='us'"), "us")
        self.assertEqual(_sanitize_country("country=\"us\""), "us")
        self.assertEqual(_sanitize_country("{'country': 'us'}"), "us")
        self.assertEqual(_sanitize_country("invalid"), "us") # default fallback
        
        # Test category sanitizers
        self.assertEqual(_sanitize_category("mobile_games"), "mobile_games")
        self.assertEqual(_sanitize_category("category='mobile_games'"), "mobile_games")
        self.assertEqual(_sanitize_category("category=\"mobile_games\""), "mobile_games")

if __name__ == "__main__":
    unittest.main()
