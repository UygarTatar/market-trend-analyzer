import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import google.generativeai as genai
from dotenv import load_dotenv
from agent.prompts import EVALUATOR_PROMPT

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Use our verified fast model
EVALUATOR_MODEL_NAME = "gemini-3.1-flash-lite"

def evaluate_report(report_text: str) -> dict:
    """
    Evaluates a generated report against a 5-criteria rubric using Gemini.
    
    Returns a dictionary with scores for each criterion, a total score, and feedback.
    """
    model = genai.GenerativeModel(model_name=EVALUATOR_MODEL_NAME)
    
    # Format the prompt with the actual report text
    prompt = EVALUATOR_PROMPT.format(report=report_text)
    
    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # Robust JSON parsing: remove Markdown code fences if present
        clean_json = raw_text.replace("```json", "").replace("```", "").strip()
        
        evaluation = json.loads(clean_json)
        
        # Ensure all required keys exist to prevent downstream errors
        required_keys = [
            "all_3_categories_covered", 
            "three_numeric_datapoints", 
            "cross_market_comparison", 
            "visualization_reference", 
            "clear_conclusion",
            "total_score",
            "feedback"
        ]
        
        for key in required_keys:
            if key not in evaluation:
                if "score" in key:
                    evaluation[key] = 0.0
                else:
                    evaluation[key] = 0
        
        return evaluation
        
    except Exception as e:
        print(f"[ERROR] Evaluator failed: {e}")
        # Default failure state
        return {
            "all_3_categories_covered": 0,
            "three_numeric_datapoints": 0,
            "cross_market_comparison": 0,
            "visualization_reference": 0,
            "clear_conclusion": 0,
            "total_score": 0.0,
            "feedback": "Evaluation engine failed to parse response. Assuming high revision priority."
        }

if __name__ == "__main__":
    # Smoke test with a deliberately bad report
    print("--- Starting Evaluator Smoke Test ---")
    bad_report = "This is a very short report. It only talks about Mobile Apps. It has no numbers."
    result = evaluate_report(bad_report)
    print(f"Evaluation Score: {result['total_score']}")
    print(f"Feedback: {result['feedback']}")
