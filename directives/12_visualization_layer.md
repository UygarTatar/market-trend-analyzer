# Directive: Visualization Layer

**Goal:** Create the charting modules to visualize trend scores, top movers, and genre distributions for the Gradio UI.

**Inputs:** Refer to `project_plan.md` Section 9.
**Outputs:** 1. Create `visualization/charts.py`.

**Rules:**
- Use `matplotlib` for static charts and `plotly` for interactive ones.
- **Trend Score Bar Chart:** Implement `create_trend_score_bar(category_scores: dict)`. It must generate a Matplotlib bar chart comparing the 3 categories. Return the image as a base64-encoded string (this ensures easy embedding in Gradio).
- **Top Movers Table:** Implement `create_top_movers_table(top_movers: list, category: str)`. Use `plotly.graph_objects.Table` to create a sleek, interactive table showing apps and their rank changes.
- **Genre Distribution Pie:** Implement `create_genre_distribution_pie(genre_counts: dict, title: str)`. Use `plotly.express.pie`.
- **Edge Case Handling:** If empty data (e.g., an empty dictionary or list) is passed to any of these functions, they must return a graceful empty figure or a placeholder, NOT throw an exception.
- At the bottom, add an `if __name__ == "__main__":` block to mock some dummy data (e.g., `{"mobile_apps": 0.8, "mobile_games": -0.2, "pc_games": 0.5}`) and test the generation of the base64 string and Plotly objects.

**Known edge cases (learned during execution):**
- **Memory Management**: In a server environment like Gradio, failing to call `plt.close()` leads to cumulative memory usage and potential chart overlap. Explicit closing was added to all Matplotlib functions.
- **Empty State UI**: Passing empty lists or dicts to Plotly can result in confusing blank grids. The implementation uses `fig.add_annotation` to provide "No data available" feedback to the user.
- **Base64 Portability**: Encoding static charts to base64 strings avoids local file I/O overhead and permissions issues during deployment, which is critical for Gradio stability.
- **Dynamic Sizing**: Fixed heights were added to Plotly figures to prevent the Gradio UI from "jumping" or resizing awkwardly when data loads.

**Status: COMPLETE** — `visualization/charts.py` implemented. Matplotlib base64 encoding and Plotly interactive chart generation verified via dry-test.