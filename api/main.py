from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .agent_orchestrator import agent_executor # Import our new agent
from . import agent_tools # Import to ensure clients are initialized on startup

# --- FastAPI App Initialization ---
app = FastAPI(
    title="AI-Powered Agentic Recommender API",
    description="An API that uses an LLM agent to provide intelligent recommendations.",
    version="2.0.0"
)

# --- Request Models ---
class AgentQuery(BaseModel):
    user_id: str
    query: str
    chat_history: list = [] # To make it conversational

# --- API Endpoint ---
@app.post("/agent_recommend")
async def get_agent_recommendation(request: AgentQuery):
    """
    Receives a user query and orchestrates an agentic response.
    """
    try:
        response = await agent_executor.ainvoke({
            "input": request.query,
            "user_id": request.user_id,
            "chat_history": request.chat_history
        })
        
        return {"response": response['output']}
        
    except Exception as e:
        print(f"Error in agent invocation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
def on_startup():
    # This just ensures our database clients are warm
    print("FastAPI server starting... initializing clients.")
    _ = agent_tools.neo4j_driver
    _ = agent_tools.redis_client
    _ = agent_tools.chroma_client
    print("All clients initialized.")