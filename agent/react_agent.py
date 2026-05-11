import os
import sys
from dotenv import load_dotenv

# Add the project root to sys.path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from langchain.prompts import PromptTemplate
from agent.tools import ALL_TOOLS
from agent.prompts import SYSTEM_PROMPT

# Load environment variables (API keys)
load_dotenv()

def build_agent() -> AgentExecutor:
    """
    Initialize the Google Gemini LLM and wrap it in a ReAct AgentExecutor.
    """
    # 1. Initialize the LLM (Gemini 1.5 Pro)
    # Note: Ensure GOOGLE_API_KEY is set in your .env file
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3,  # Low temperature for more deterministic/stable reasoning
        max_output_tokens=2048,
    )

    # 2. Define the ReAct Prompt Template
    # We attempt to pull the standard one from LangChain Hub, 
    # but provide a fallback if there are connection issues.
    try:
        base_prompt = hub.pull("hwchase17/react")
    except Exception:
        # Fallback ReAct prompt template
        template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Context: {system_prompt}

Question: {input}
Thought: {agent_scratchpad}"""
        base_prompt = PromptTemplate.from_template(template)

    # Inject our SYSTEM_PROMPT context into the template
    prompt = base_prompt.partial(system_prompt=SYSTEM_PROMPT)

    # 3. Create the ReAct Agent
    agent = create_react_agent(llm=llm, tools=ALL_TOOLS, prompt=prompt)

    # 4. Initialize the Executor
    return AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        verbose=True,
        handle_parsing_errors=True,  # Crucial for LLM stability
        max_iterations=10,            # Prevent infinite loops
        return_intermediate_steps=True
    )

import logging

# Configure deep logging
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".tmp", "agent_debug.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)

def run_agent(user_query: str) -> str:
    """
    Execute the agent with a user query and return the final response.
    Includes deep logging for debugging.
    """
    logging.info(f"--- NEW SESSION: {user_query} ---")
    try:
        executor = build_agent()
        logging.info("Agent built successfully. Starting invocation...")
        
        # We use invoke which is synchronous
        response = executor.invoke({"input": user_query})
        
        # Log the intermediate steps (tools called)
        if "intermediate_steps" in response:
            for i, (action, observation) in enumerate(response["intermediate_steps"]):
                logging.info(f"Step {i+1}: Action={action.tool}, Input={action.tool_input}")
                logging.info(f"Step {i+1}: Observation={str(observation)[:200]}...")

        logging.info("Invocation successful.")
        return response["output"]
    except Exception as e:
        logging.error(f"Error during agent execution: {str(e)}", exc_info=True)
        raise e

if __name__ == "__main__":
    # Dry-run test
    print(f"Logging to: {LOG_FILE}")
    print(run_agent("What are the top trending genres this week in mobile games?"))
