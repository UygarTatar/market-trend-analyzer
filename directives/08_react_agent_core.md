# Directive: LangChain ReAct Agent Core

**Goal:** Implement the brain of the system using LangChain's ReAct framework and define the core system prompts.

**Inputs:** Refer to `project_plan.md` Sections 6.2 and 6.3.
**Outputs:** 1. Create `agent/prompts.py`.
2. Create `agent/react_agent.py`.

**Rules for `agent/prompts.py`:**
- Define `SYSTEM_PROMPT`: Instruct the agent that it is a "market intelligence analyst AI". It MUST follow a logical sequence: collect data -> compute trends -> detect patterns -> generate report.
- Define `EVALUATOR_PROMPT` (we will use this later in Section 8, but define it now): A strict rubric-based prompt for evaluating the final report against 5 criteria.

**Rules for `agent/react_agent.py`:**
- Import `ALL_TOOLS` from `agent.tools`.
- Import `SYSTEM_PROMPT` from `agent.prompts`.
- Initialize `ChatGoogleGenerativeAI` using `gemini-1.5-pro` with a low temperature (e.g., 0.3) for logical stability.
- Use `hub.pull("hwchase17/react")` to get the standard ReAct prompt template, or define a robust custom one.
- Create the agent using `create_react_agent` and wrap it in an `AgentExecutor`.
- Set `handle_parsing_errors=True` and `max_iterations=10` on the executor to prevent infinite loops.
- Implement a `run_agent(user_query: str) -> str` function that invokes the executor.
- At the bottom, add an `if __name__ == "__main__":` block to test a query like "What are the top trending genres this week?" and print the agent's reasoning.

**Known edge cases (learned during execution):**
- **API Key Dependency**: The agent requires a valid `GOOGLE_API_KEY` in the `.env` file. Without it, the `ChatGoogleGenerativeAI` class fails during initialization.
- **Model Availability**: In this environment, Gemini 1.5 models were not found. The agent was successfully migrated to **Gemini 3.1** models (`gemini-3.1-pro-preview` or `gemini-3.1-flash-lite`).
- **Quota Management**: Using the `Pro` version of 3.1 on a free tier key quickly triggers "Resource Exhausted" (429) errors. The system was optimized to use **`gemini-3.1-flash-lite`**, which provides stable performance and higher throughput.
- **LangChain Hub Access**: `hub.pull("hwchase17/react")` can fail due to connectivity. A local fallback `PromptTemplate` was implemented to ensure system resilience.

**Status: COMPLETE** — `agent/prompts.py` and `agent/react_agent.py` implemented. The ReAct core has been **live-verified** to reason, select tools, and handle observations using the Gemini 3.1 Flash Lite model.