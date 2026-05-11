import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reporting.generator import generate_report
from reporting.evaluator import evaluate_report

MAX_REVISION_ATTEMPTS = 2
PASSING_THRESHOLD = 0.7

def generate_with_evaluation(user_query: str, analysis_data: str) -> dict:
    """
    Autonomous loop that generates a report and evaluates it.
    If the score is below the threshold, it requests a revision using the feedback.
    
    Returns:
        dict: {
            "report": str,
            "final_score": float,
            "attempts": int,
            "passed_evaluation": bool
        }
    """
    attempts = 0
    current_report = ""
    current_evaluation = {}
    current_feedback = ""
    
    while attempts < MAX_REVISION_ATTEMPTS:
        attempts += 1
        print(f"  [Revision Loop] Attempt {attempts}...")
        
        # 1. Prepare data (if it's a revision, we append the feedback)
        if attempts > 1:
            revision_context = f"{analysis_data}\n\nPREVIOUS EVALUATOR FEEDBACK: {current_feedback}\nPLEASE FIX THESE ISSUES."
        else:
            revision_context = analysis_data
            
        # 2. Generate
        current_report = generate_report(user_query, revision_context)
        
        # 3. Evaluate
        current_evaluation = evaluate_report(current_report)
        current_score = current_evaluation.get("total_score", 0.0)
        current_feedback = current_evaluation.get("feedback", "")
        
        print(f"  [Revision Loop] Score: {current_score}")
        
        # 4. Check if we passed
        if current_score >= PASSING_THRESHOLD:
            print("  [Revision Loop] Passing threshold met.")
            return {
                "report": current_report,
                "final_score": current_score,
                "attempts": attempts,
                "passed_evaluation": True
            }
            
        print(f"  [Revision Loop] Score below threshold ({PASSING_THRESHOLD}). Refining...")

    # If we run out of attempts, return the best we have
    return {
        "report": current_report,
        "final_score": current_evaluation.get("total_score", 0.0),
        "attempts": attempts,
        "passed_evaluation": False
    }

if __name__ == "__main__":
    # Dry-run test with a deliberately hard query/data combo to test the loop
    print("--- Starting Revision Loop Dry-Run ---")
    
    # We provide data that is missing some components to see if the evaluator catches it
    mock_query = "Detailed analysis of everything."
    mock_data = "Only found some data about PC games: Steam sellers are up. No mobile data found."
    
    result = generate_with_evaluation(mock_query, mock_data)
    
    print("\n--- Final Results ---")
    print(f"Attempts Made: {result['attempts']}")
    print(f"Final Score: {result['final_score']}")
    print(f"Passed: {result['passed_evaluation']}")
    print("\n--- Final Report (Excerpt) ---")
    print(result['report'][:300] + "...")
