import chromadb
import redis
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer

# --- Initialize Clients ---
# We initialize them here to be reused by the tools

# Pillar 1: Vector DB Client
print("Loading embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Connecting to ChromaDB...")
chroma_client = chromadb.PersistentClient(path="./chroma_db")
product_collection = chroma_client.get_collection("products")

# Pillar 2: Redis Client
print("Connecting to Redis...")
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Pillar 3: Graph DB Client
print("Connecting to Neo4j...")
neo4j_uri = "bolt://localhost:7687"
neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=("neo4j", "password123"))

# --- Define Tools ---

def get_semantic_recommendations(query: str, n_results: int = 5) -> dict:
    """
    Tool 1: Semantic Search.
    Finds products that are conceptually similar to a text query.
    Use this to find similar-looking items.
    """
    print(f"[Tool Call] Semantic Search for: '{query}'")
    query_embedding = embedding_model.encode(query).tolist()
    results = product_collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results['metadatas'][0]

def get_collaborative_recommendations(user_id: str, n_results: int = 5) -> list:
    """
    Tool 2: Collaborative Filtering (Graph).
    Finds products that similar users have viewed.
    Use this when the user asks "what do other people like?" or "recommend something for me".
    """
    print(f"[Tool Call] Collaborative Search for User: '{user_id}'")
    query = """
    MATCH (u:User {id: $user_id})-[:VIEWED]->(p:Product)<-[:VIEWED]-(other:User)
    WITH other, u
    MATCH (other)-[:VIEWED]->(rec:Product)
    WHERE NOT (u)-[:VIEWED]->(rec)
    RETURN rec.name AS name, rec.category AS category, COUNT(other) AS recommendation_strength
    ORDER BY recommendation_strength DESC
    LIMIT $n_results
    """
    with neo4j_driver.session() as session:
        result = session.run(query, user_id=user_id, n_results=n_results)
        return [record.data() for record in result]

def get_user_profile(user_id: str) -> dict:
    """
    Tool 3: User Profile Retrieval (Cache).
    Gets the user's most recent interaction history.
    """
    print(f"[Tool Call] Profile Retrieval for User: '{user_id}'")
    history = redis_client.lrange(f"user:{user_id}:history", 0, 9) # Get last 10 items
    return {"user_id": user_id, "recent_views": history}

def track_user_event(user_id: str, product_name: str) -> str:
    """
    Tool 4: User Event Tracking (Cache).
    Records a new product view event for a user.
    """
    print(f"[Tool Call] Event Tracking for User: '{user_id}'")
    key = f"user:{user_id}:history"
    redis_client.lpush(key, product_name)
    redis_client.ltrim(key, 0, 49) # Keep only the 50 most recent items
    return "Event tracked successfully."