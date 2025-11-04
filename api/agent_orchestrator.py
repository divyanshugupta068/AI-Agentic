from langchain_groq import ChatGroq
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
from . import agent_tools

# 1. Initialize the LLM "Brain"
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.0 # We want precision, not creativity
)

# 2. Register our functions as "Tools"
tools = [
    tool(agent_tools.get_semantic_recommendations),
    tool(agent_tools.get_collaborative_recommendations),
    tool(agent_tools.get_user_profile),
    tool(agent_tools.track_user_event),
]

# 3. Create the Agent Prompt
# This instructs the agent *how* to think.
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a precision-driven, task-oriented AI recommender system. Your responses must be accurate and directly based on the data provided by your tools.

**CORE DIRECTIVES:**
1.  **User Context is CRITICAL:** The user's ID is provided as `{user_id}`. You MUST use this ID when calling any tool that requires a `user_id` (e.g., `get_collaborative_recommendations`, `get_user_profile`). There are no exceptions.
2.  **Tool Fidelity is MANDATORY:** You must only state facts returned by your tools. If a tool returns an empty result (like `[]`), you MUST report that you couldn't find any results with that tool and suggest another approach.
3.  **DO NOT HALLUCINATE:** Under no circumstances should you invent product names, brands, or details. If your tools provide no information, you must state that.
4.  **Synthesize, Don't Just List:** Do not output raw lists from your tools. Formulate a helpful, conversational paragraph that synthesizes the information.

**PLANNING PROCESS:**
1.  First, analyze the user's query (`{input}`).
2.  If the query mentions viewing a product, your first step is ALWAYS to call the `track_user_event` tool.
3.  Based on the query, decide on the best primary tool to use (semantic vs. collaborative).
4.  Execute the plan. If the primary tool fails or returns no results, consider using a different tool as a fallback.
5.  Formulate the final response based on the successful tool outputs.
""",
        ),
        ("placeholder", "{chat_history}"),
        # This is the crucial line that injects the user context
        ("human", "My User ID is `{user_id}`. Here is my request: {input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# 4. Create the Agent
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

print("✅ 'IQ 160' Agent Orchestrator is online.")
