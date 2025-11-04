# Full-Stack AI Agent Recommender System 🧠🛍️

This project is an advanced, full-stack application demonstrating an AI-powered e-commerce assistant. It features an interactive Streamlit chat interface, a FastAPI backend, and an autonomous LangChain agent that leverages multiple databases (Vector, Graph, Cache) to provide intelligent, contextual product recommendations.

---

## 🚀 Demo

*(**Action Required:** Embed a GIF or link to a short Loom/YouTube video showing the Streamlit chat interface interacting with the agent)*



---

## Key Features

* **Conversational Interface:** A Streamlit chat application for natural language interaction.
* **Autonomous AI Agent:** Uses LangChain and Llama 3.1 (via Groq) to understand user queries, form plans, and utilize specialized tools.
* **Multi-Modal Data Foundation:** Integrates three databases for comprehensive understanding:
    * **ChromaDB (Vector):** Enables semantic search based on product meaning.
    * **Neo4j (Graph):** Models user-product relationships for collaborative filtering.
    * **Redis (Cache):** Provides real-time user session memory (interaction history).
* **Agentic Tool Use:** The AI agent dynamically chooses the best tool (semantic search, collaborative filtering, user profile lookup) based on the user's query.
* **Grounded & Synthesized Responses:** The agent retrieves factual data from its tools and synthesizes it into helpful, conversational answers, avoiding hallucination.
* **Decoupled Architecture:** FastAPI backend cleanly separated from the Streamlit frontend.

---

## Technology Stack

| Component            | Technology/Library                                 | Purpose                                   |
| :------------------- | :------------------------------------------------- | :---------------------------------------- |
| **Frontend** | Streamlit                                          | Interactive Chat UI                       |
| **Backend API** | Python, FastAPI, Uvicorn                           | API Server, Orchestration                 |
| **AI Agent** | LangChain, Langchain-Groq (Llama 3.1)              | Core Logic, Planning, Tool Use, Synthesis |
| **Semantic Search** | ChromaDB, Sentence-Transformers                    | Understanding Product Meaning             |
| **Collaborative** | Neo4j                                              | Understanding User Relationships          |
| **User Memory** | Redis                                              | Real-time Interaction History             |
| **Databases Setup** | Docker, Docker Compose                             | Running Neo4j & Redis                     |
| **Data Handling** | Pandas                                             | Initial Data Loading & Processing         |

---

## Setup & Run

**Prerequisites:**
* Python 3.10+
* Docker & Docker Compose


**1. Clone the repository:**
```bash
git clone <your-repository-url>
cd your-project-folder-name # Navigate into the cloned folder
```
**2. Create and activate a virtual environment:**
```bash
python -m venv .venv
# On Windows
.\.venv\Scripts\Activate.ps1
# On macOS/Linux
source .venv/bin/activate
```
**3. Install Python dependencies:**
```bash
pip install -r requirements.txt
```
### 4. Add Groq API Key:
```bash
Get a free API key from Groq.
Paste the key into the --GROQ_API_KEY-- variable inside the --api/agent_orchestrator.py -- file.
```
## 4.1 In case backend gives invalid Api key error , Do this immediately: 
```bash
# Use this name if you are using Groq
$env:GROQ_API_KEY = "YOUR_API_KEY"

# Or use whatever name you found in your code (e.g., OPENAI_API_KEY)
! BUT REMEMBER ITS ONLY ACTIVE UNTIL YOUR CURRENT POWERSHELL SESSION
```
**5. Start Databases (Docker):**
```bash
docker-compose up -d
```
### 6. Seed Databases:
```bash
(Vector DB): Run python seed_vector_db.py (This takes several minutes).
(Graph DB): Run python seed_graph_db.py.
```
### 7. Run the Application:
**Terminal 1 (Backend API):**
```bash
python -m uvicorn api.main:app --reload
```
**Terminal 2 (Frontend app):**
```bash
streamlit run app.py
```
_Navigate to the local URL provided by Streamlit (usually http://localhost:8501) to use the AI Assistant._

