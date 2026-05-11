# Directive: AI Report Generator

**Goal:** Create the core reporting engine that turns raw market data into a professional analyst report using the Gemini API.

**Inputs:** Refer to `project_plan.md` Section 7.
**Outputs:** 1. Create `reporting/generator.py`.

**Rules:**
- Use the `google-generativeai` library. Load `GOOGLE_API_KEY` from the `.env` file.
- Implement the `generate_report(user_query: str, analysis_data: str) -> str` function.
- **Model:** Use `gemini-3.1-flash-lite` (since we verified it works well and fast in our environment).
- **The Prompt Structure:** It MUST follow the exact structure defined in Section 7 of the project plan:
    - Executive Summary
    - Mobile Apps Trends
    - Mobile Games Trends
    - PC Games Trends
    - Cross-Platform Analysis
    - Key Data Points (must extract at least 3 numeric values)
    - Conclusion & Recommendations
- **Tone:** Senior Market Intelligence Analyst (Professional, data-driven, actionable).
- **Error Handling:** If the API fails, return a pre-defined Markdown template with a "Data currently unavailable" message instead of crashing.
- At the bottom, add an `if __name__ == "__main__":` block to dry-test the function with some dummy string data to verify the markdown structure.

**Known edge cases (learned during execution):**
- **Numeric Extraction**: If the `analysis_data` is very sparse, the LLM may hallucinate numbers to meet the "at least 3 numeric values" requirement. The prompt was reinforced to prioritize extraction over generation.
- **Safety Filter Triggers**: Certain competitive analysis keywords can occasionally trigger safety filters. The implementation includes a `try-except` block that returns a professional fallback report rather than crashing the system.
- **Markdown Consistency**: The Evaluator module (Section 8) is very strict about headers. The `generator.py` implementation uses hardcoded Markdown strings to ensure 100% compatibility with the rubric checks.

**Status: COMPLETE** — `reporting/generator.py` implemented using Gemini 3.1 Flash Lite. Professional reporting structure verified via dry-test.