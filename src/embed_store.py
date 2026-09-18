"""
Filename: embed_store.py

Purpose
-------
Reads JSON chunks, generates embeddings,
and stores them in ChromaDB.

Pipeline
--------
1. scraper.py
2. clean_text.py
3. chunk_text.py
4. embed_store.py

Project
-------
AI Cloud Operations Assistant
"""

import json
import os
import shutil

import chromadb
from sentence_transformers import SentenceTransformer

from src.config import (
    CHUNK_DIR,
    CHROMA_DB_DIR,
)

# =====================================================
# Load Embedding Model
# =====================================================

print("Loading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# =====================================================
# ChromaDB Configuration
# =====================================================

COLLECTION_NAME = "cloud_operations_docs"

# =====================================================
# Create Fresh Database
# =====================================================

if os.path.exists(CHROMA_DB_DIR):

    print("Removing old ChromaDB...")

    shutil.rmtree(CHROMA_DB_DIR)

client = chromadb.PersistentClient(
    path=CHROMA_DB_DIR,
)

collection = client.create_collection(
    name=COLLECTION_NAME,
)

# =====================================================
# Store Embeddings
# =====================================================

total_chunks = 0

print("=" * 60)
print("Embedding Pipeline")
print("=" * 60)

for technology in sorted(os.listdir(CHUNK_DIR)):

    technology_folder = os.path.join(
        CHUNK_DIR,
        technology,
    )

    if not os.path.isdir(technology_folder):
        continue

    print(f"\nTechnology : {technology}")

    for filename in sorted(os.listdir(technology_folder)):

        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(
            technology_folder,
            filename,
        )

        with open(
            filepath,
            "r",
            encoding="utf-8",
        ) as file:

            chunk = json.load(file)

        content = chunk["content"]

        metadata = chunk["metadata"]

        embedding = model.encode(
            content
        ).tolist()

        chunk_id = (
            f"{metadata['technology']}_"
            f"{metadata['document']}_"
            f"{metadata['chunk_id']}"
        )

        collection.add(
            ids=[chunk_id],
            documents=[content],
            embeddings=[embedding],
            metadatas=[metadata],
        )

        total_chunks += 1

print("\n" + "=" * 60)
print("Embedding Summary")
print("=" * 60)
print(f"Chunks Stored : {total_chunks}")
print(f"Collection    : {COLLECTION_NAME}")
print("=" * 60)