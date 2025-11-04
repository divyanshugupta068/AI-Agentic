import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
import json

print("Initializing vector database seeding...")

# 1. Load Data
try:
    df = pd.read_csv('data/products.csv')
except FileNotFoundError:
    print("Error: 'data/products.csv' not found. Please make sure the file is in the 'data' folder.")
    exit()

# --- CORRECTED COLUMN NAMES ---
# Use the original column names from your CSV
original_id_col = 'uniq_id'
original_name_col = 'product_name'
original_cat_col = 'product_category_tree'
original_desc_col = 'description'

required_cols = [original_id_col, original_name_col, original_cat_col, original_desc_col]
for col in required_cols:
    if col not in df.columns:
        print(f"Error: Required column '{col}' not found in 'products.csv'.")
        exit()

df = df.dropna(subset=required_cols)
df = df.drop_duplicates(subset=[original_id_col])

# 2. Initialize Model
print("Loading sentence transformer model (all-MiniLM-L6-v2)...")
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Error loading SentenceTransformer model: {e}")
    print("Please ensure you are connected to the internet or the model is cached.")
    exit()

# 3. Initialize ChromaDB
print("Connecting to ChromaDB...")
client = chromadb.PersistentClient(path="./chroma_db")
collection_name = "products"

try:
    if client.get_collection(name=collection_name):
        print(f"Collection '{collection_name}' already exists. Deleting it.")
        client.delete_collection(name=collection_name)
except Exception as e:
    # This is normal if the collection doesn't exist yet
    pass

collection = client.create_collection(
    name=collection_name,
    metadata={"hnsw:space": "cosine"} # Use cosine similarity
)

# 4. Prepare Data for Embedding
print("Preparing data for embedding...")

def clean_category(raw_cat):
    try:
        first_item = json.loads(raw_cat)[0]
        return first_item.split('>>')[0].strip()
    except:
        return "Uncategorized"

df['category_clean'] = df[original_cat_col].apply(clean_category)

# Create the 'soup' (the text we will embed)
df['soup'] = df[original_name_col] + ' ' + df['category_clean'] + ' ' + df[original_desc_col]
documents = df['soup'].tolist()

# --- CORRECTED METADATA ---
# Create the metadata that will be stored alongside the vectors
metadatas = df[[original_id_col, original_name_col, 'category_clean']].copy()
metadatas.rename(columns={
    original_id_col: 'product_id', # Standardize to 'product_id' in the metadata
    original_name_col: 'name',
    'category_clean': 'category'
}, inplace=True)
metadatas_list = metadatas.to_dict('records')

# Use the original uniq_id for the ChromaDB 'id'
ids = df[original_id_col].tolist()

# 5. Generate and Add Embeddings
print(f"Generating and adding embeddings for {len(df)} products (in batches)...")
batch_size = 500
for i in range(0, len(documents), batch_size):
    batch_num = (i // batch_size) + 1
    print(f"Processing batch {batch_num}...")
    
    batch_docs = documents[i:i+batch_size]
    batch_metadatas = metadatas_list[i:i+batch_size]
    batch_ids = ids[i:i+batch_size]
    
    try:
        batch_embeddings = model.encode(batch_docs).tolist()
    except Exception as e:
        print(f"Error encoding batch {batch_num}: {e}")
        continue
    
    try:
        collection.add(
            embeddings=batch_embeddings,
            documents=batch_docs,
            metadatas=batch_metadatas,
            ids=batch_ids
        )
    except Exception as e:
        print(f"Error adding batch {batch_num} to ChromaDB: {e}")

print("Vector database seeding complete.")