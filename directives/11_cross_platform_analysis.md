# Directive: Cross-Platform Analysis

**Goal:** Implement the logic to detect overlapping titles and shared genre trends across Mobile and PC markets.

**Inputs:** Refer to `project_plan.md` Section 5.3.
**Outputs:** 1. Create `analysis/cross_platform.py`.

**Rules:**
- Implement `detect_overlap(category_results: dict) -> dict`.
- The input `category_results` will contain DataFrames for 'mobile_apps', 'mobile_games', and 'pc_games'.
- **Title Overlap:** Convert titles to lowercase and use set intersection (`&`) to find games that exist on both mobile and PC.
- **Genre Trends:** Find the most frequent genre in each category using `value_counts().idxmax()`.
- **Shared Genre:** Determine the overall most common genre across all platforms using `collections.Counter`.
- **Edge Case Handling:** If any DataFrame is empty, handle it gracefully without throwing a `KeyError` or `ValueError`.
- At the bottom, add an `if __name__ == "__main__":` block to mock 3 dummy DataFrames (with at least one overlapping title like "Minecraft" or "Roblox") and print the resulting overlap dictionary to verify the logic.

**Known edge cases (learned during execution):**
- **Title Normalization**: Direct set intersection (`&`) requires exact string matches. Converting all titles to lowercase is a mandatory first step to prevent missing matches like "Roblox" vs "roblox".
- **Null Value Handling**: DataFrames from scrapers may contain `NaN` titles or genres. Using `.dropna()` before set conversion and `value_counts()` is critical to prevent `AttributeError`.
- **Schema Variance**: If a category has no snapshots, the genre column may be missing entirely. The implementation includes a "Unknown" fallback to prevent `KeyError`.
- **Tie-Breaking in Trends**: If two genres have the same frequency across platforms, `Counter.most_common(1)` will deterministically select the first one encountered.

**Status: COMPLETE** — `analysis/cross_platform.py` implemented. Title overlap and shared genre detection verified via dry-test.