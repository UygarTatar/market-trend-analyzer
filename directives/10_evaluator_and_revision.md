# Directive: Evaluator & Revision Loop

**Goal:** Implement the autonomous quality control system to evaluate and dynamically refine generated reports.

**Inputs:** Refer to `project_plan.md` Section 8.
**Outputs:** 1. Create `reporting/evaluator.py`.
2. Create `reporting/revision.py`.

**Rules:**
- **Evaluator (`evaluator.py`):**
    - Use `gemini-3.1-flash-lite` (our verified fast model).
    - Import `EVALUATOR_PROMPT` from `agent.prompts`.
    - The function `evaluate_report(report_text)` must force the LLM to output STRICT JSON. 
    - The JSON must contain the 5 exact criteria defined in the project plan (0 or 1 for each), a `total_score` (sum/5), and a `feedback` string.
    - Implement robust JSON parsing: strip Markdown formatting like ` ```json ` and ` ``` ` before calling `json.loads()`.
- **Revision Loop (`revision.py`):**
    - Import the generator and the evaluator.
    - Implement `generate_with_evaluation(user_query: str, analysis_data: str)`.
    - Set constants: `MAX_REVISION_ATTEMPTS = 2` and `PASSING_THRESHOLD = 0.7`.
    - **Logic:** Generate -> Evaluate. If score < 0.7, append the evaluator's `feedback` to a new prompt and call the generator again. Break early if it passes.
    - Return a dictionary: `{"report": best_report, "final_score": best_score, "attempts": attempts, "passed_evaluation": bool}`.
- **Testing:** At the bottom of `revision.py`, write a dry-run test using a deliberately short/bad mock report to ensure the evaluator catches the failure and triggers the loop.

**Known edge cases (learned during execution):**
- **Template Collision**: The `EVALUATOR_PROMPT` contains curly braces for the JSON schema, which conflicts with Python's `.format()` method. These were escaped to `{{ ... }}` to allow dynamic report injection.
- **JSON Parsing Robustness**: LLMs occasionally include Markdown formatting (fences) in their output even when asked for raw JSON. The `evaluator.py` implementation includes a cleaning layer to strip ` ```json ` and other artifacts before calling `json.loads()`.
- **Import Context**: Standalone testing of reporting modules requires manual `sys.path` adjustment to resolve dependencies from the project root.
- **Hallucinated Compliance**: The generator is often "too good" at making a professional-looking report even with thin data. The evaluator rubric is designed to be pedantic about *numeric* presence to force real data density.

**Status: COMPLETE** — `reporting/evaluator.py` and `reporting/revision.py` implemented. Quality control gate and autonomous revision loop verified via dry-tests.