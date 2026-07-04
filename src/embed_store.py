"""
embed_store.py

Purpose:
---------
Reads all chunk files from data/chunks,
generates embeddings using Sentence Transformers,
and stores them in ChromaDB.

Run Order:
----------
1. scraper.py
2. chunk_documents.py
3. embed_store.py
4. rag_chat.py
"""

import os
import shutil
import chromadb
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------
# Load embedding model
# This converts text into vector embeddings.
# ---------------------------------------------------
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# ---------------------------------------------------
# ChromaDB Configuration
# ---------------------------------------------------
DB_PATH = "chroma_db"
COLLECTION_NAME = "docker_docs"

# ---------------------------------------------------
# Delete old database
# This prevents stale vectors from previous runs.
# ---------------------------------------------------
if os.path.exists(DB_PATH):
    print("Removing old ChromaDB...")
    shutil.rmtree(DB_PATH)

# Create a fresh persistent database
client = chromadb.PersistentClient(path=DB_PATH)

# Create a new collection
collection = client.create_collection(
    name=COLLECTION_NAME
)

# ---------------------------------------------------
# Read all chunk files
# ---------------------------------------------------
CHUNK_DIR = "data/chunks"

chunk_files = sorted([
    f for f in os.listdir(CHUNK_DIR)
    if f.endswith(".txt")
])

print(f"Found {len(chunk_files)} chunk files.")

# ---------------------------------------------------
# Generate embeddings and store them
# ---------------------------------------------------
for file in chunk_files:

    filepath = os.path.join(CHUNK_DIR, file)

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # Convert text into embedding vector
    embedding = model.encode(text).tolist()

    # Store in ChromaDB
    collection.add(
        ids=[file],                     # Unique ID
        documents=[text],               # Original text
        embeddings=[embedding],         # Vector embedding
        metadatas=[{
            "source": file              # Used for citations
        }]
    )

print("=" * 50)
print(f"Successfully stored {len(chunk_files)} chunks.")
print("Vector database is ready!")
print("=" * 50)