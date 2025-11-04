import sqlite3
import pandas as pd
from neo4j import GraphDatabase
import json

print("Initializing graph database seeding...")

# 1. Neo4j Connection
uri = "bolt://localhost:7687"
try:
    # Use the password you set in docker-compose.yml
    driver = GraphDatabase.driver(uri, auth=("neo4j", "password123"))
    driver.verify_connectivity()
    print("Successfully connected to Neo4j.")
except Exception as e:
    print(f"Error connecting to Neo4j: {e}")
    print("Please ensure your Docker containers are running with 'docker-compose up -d'.")
    exit()

# 2. Load Data
try:
    # Load Products from CSV
    product_df = pd.read_csv('data/products.csv')
    
    # --- CORRECTED COLUMN NAMES ---
    original_id_col = 'uniq_id'
    original_name_col = 'product_name'
    original_cat_col = 'product_category_tree'

    required_cols = [original_id_col, original_name_col, original_cat_col]
    product_df = product_df.dropna(subset=required_cols)
    product_df = product_df.drop_duplicates(subset=[original_id_col])

    # --- Clean and Standardize Data ---
    def clean_category(raw_cat):
        try:
            first_item = json.loads(raw_cat)[0]
            return first_item.split('>>')[0].strip()
        except:
            return "Uncategorized"

    product_df['category'] = product_df[original_cat_col].apply(clean_category)
    
    # Rename columns to a standard format for the database
    product_df.rename(columns={
        original_id_col: 'product_id',
        original_name_col: 'name'
    }, inplace=True)

    products = product_df[['product_id', 'name', 'category']].to_dict('records')

    # Load Interactions from SQLite
    conn = sqlite3.connect('data/db.sqlite3')
    interactions_df = pd.read_sql_query("SELECT user_id, product_id FROM user_interactions", conn)
    conn.close()
    interactions = interactions_df.to_dict('records')

except FileNotFoundError:
    print("Error: 'data/products.csv' not found.")
    exit()
except Exception as e:
    print(f"An error occurred during data loading: {e}")
    exit()


# 3. Seeding Queries
def run_query(tx, query, data):
    tx.run(query, data=data)

with driver.session() as session:
    # Clear out old data to ensure a fresh start
    print("Deleting old graph data...")
    session.run("MATCH (n) DETACH DELETE n")

    # Set constraints for faster queries and data integrity
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Product) REQUIRE p.id IS UNIQUE")
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE")

    print(f"Seeding {len(products)} products into Neo4j...")
    # Cypher query to load products
    product_query = """
    UNWIND $data AS row
    MERGE (p:Product {id: row.product_id})
    SET p.name = row.name, p.category = row.category
    """
    session.execute_write(run_query, product_query, products)
    
    print(f"Seeding {len(interactions)} interactions into Neo4j...")
    # Cypher query to load interactions and create relationships
    interaction_query = """
    UNWIND $data AS row
    MERGE (u:User {id: row.user_id})
    MERGE (p:Product {id: row.product_id})
    MERGE (u)-[:VIEWED]->(p)
    """
    session.execute_write(run_query, interaction_query, interactions)

driver.close()
print("Graph database seeding complete.")