"""
Filename: search.py

Purpose
-------
Retrieves the most relevant chunks from ChromaDB
using semantic search.

Project
-------
AI Cloud Operations Assistant
"""

import chromadb
from sentence_transformers import SentenceTransformer

from src.config import CHROMA_DB_DIR

# =====================================================
# Configuration
# =====================================================

COLLECTION_NAME = "cloud_operations_docs"

# =====================================================
# Load Embedding Model
# =====================================================

print("Loading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# =====================================================
# Connect to ChromaDB
# =====================================================

client = chromadb.PersistentClient(
    path=CHROMA_DB_DIR,
)

collection = client.get_collection(
    COLLECTION_NAME,
)

print(f"Total Chunks : {collection.count()}")

# =====================================================
# Ask Question
# =====================================================

question = input("\nAsk a question: ")

query_embedding = model.encode(
    question
).tolist()

# =====================================================
# Retrieve
# =====================================================

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5,
    include=[
        "documents",
        "metadatas",
        "distances",
    ],
)

print("\n" + "=" * 60)
print("Top Matching Chunks")
print("=" * 60)

for i in range(len(results["documents"][0])):

    metadata = results["metadatas"][0][i]

    print(f"\nResult {i + 1}")
    print("-" * 60)

    print(f"Technology : {metadata['technology']}")
    print(f"Document   : {metadata['document']}")
    print(f"Chunk ID   : {metadata['chunk_id']}")
    print(f"Distance   : {results['distances'][0][i]:.4f}")

    print("\nContent:\n")

    print(results["documents"][0][i][:700])

print("\n" + "=" * 60)