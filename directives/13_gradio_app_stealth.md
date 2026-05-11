# Directive: Gradio Web Interface & Premium UI Design

**Goal:** Create `app.py`, the final entry point that integrates the ReAct agent, visualizations, and a premium UI.

**Inputs:** - `project_plan.md` Section 11
- `SKILLS/frontend-design.md`

**Outputs:** 1. Create `app.py`.

**Rules:**
- **Integration:** Import your main backend runner and the charting functions from `visualization.charts`.
- **Frontend Design (via Skill):** Read and completely internalize `SKILLS/frontend-design.md`. You must choose a bold, production-grade aesthetic suitable for a "Market Intelligence Dashboard". 
    - Implement your chosen aesthetic direction using Gradio's custom CSS feature (`gr.Blocks(css=custom_css)`).
    - Strictly avoid generic AI aesthetics. Make intentional choices for typography, spatial composition, and colors based on the skill's guidelines.
- **Gradio Structure:** - Provide a `gr.Textbox` for the query, and `gr.Examples`.
    - The output section must display the Markdown report (`gr.Markdown`) and the charts (`gr.Image` for base64 Matplotlib, `gr.Plot` for Plotly).
- **Execution:** Create the `analyze_market(query)` wrapper function to connect the UI inputs to the backend engine.
- **Launch:** At the bottom, use `demo.launch(share=False)`.

## Known edge cases (Learned during execution)
- **Windows Path-Length Limit:** Passing large Base64 strings to `gr.Image` can trigger a `ValueError: stat: path too long` on Windows. **Solution:** Use `PIL.Image` objects directly; Gradio handles them natively without path-resolution crashes.
- **Generator StopIteration:** In Gradio 6.x, `StopIteration` raised inside a generator function (like `analyze_market`) is converted to a `RuntimeError`. **Solution:** Wrap the backend call in a broad `(Exception, BaseException)` block and catch `StopIteration` early.
- **Concurrent DB Access:** If a scraper is writing while the UI is reading, SQLite can occasionally throw a "Database is locked." **Solution:** Use `check_same_thread=False` or wrap the connection in a short retry loop.

## Completion Status
- **Status:** ✅ COMPLETED
- **Last Verified:** 2026-05-09
- **Notes:** Full ONYX Dark aesthetic implemented; handles high-throughput Steam and App Store data without UI lag.