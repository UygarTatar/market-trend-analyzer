import unittest
from reporting.evaluator import evaluate_report

class TestEvaluator(unittest.TestCase):
    """
    Test the report evaluation logic and error handling.
    """
    
    def test_default_failure_state(self):
        # If we pass something that is completely nonsensical, it should still return a valid dict
        # with a 0.0 total_score rather than crashing.
        result = evaluate_report("")
        self.assertIn("total_score", result)
        self.assertIn("feedback", result)
        self.assertLessEqual(result["total_score"], 10.0) # Should be low for empty report

    def test_required_keys_presence(self):
        # The result must ALWAYS contain the 5 rubric keys even if parsing fails
        result = evaluate_report("Invalid Report")
        required_keys = [
            "all_3_categories_covered", 
            "three_numeric_datapoints", 
            "cross_market_comparison", 
            "visualization_reference", 
            "clear_conclusion"
        ]
        for key in required_keys:
            self.assertIn(key, result)

if __name__ == "__main__":
    unittest.main()
