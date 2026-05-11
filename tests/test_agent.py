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

if __name__ == "__main__":
    unittest.main()
