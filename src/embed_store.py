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
    "sentence-transformers/all-MiniLM-L6-v2",
    backend="onnx",
    model_kwargs={"file_name": "onnx/model_quint8_avx2.onnx"},
)

# =====================================================
# ChromaDB Configuration
# =====================================================

COLLECTION_NAME = "cloud_operations_docs"
STAGING_DB_DIR = f"{CHROMA_DB_DIR}_staging"
PREVIOUS_DB_DIR = f"{CHROMA_DB_DIR}_previous"

# =====================================================
# Build a replacement database separately so a failed rebuild cannot
# destroy the currently usable index.
# =====================================================

if os.path.exists(STAGING_DB_DIR):

    print("Removing incomplete staging ChromaDB...")

    shutil.rmtree(STAGING_DB_DIR)

client = chromadb.PersistentClient(
    path=STAGING_DB_DIR,
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

# Swap the finished index into place. Keep the previous database as a
# rollback copy until the replacement has been confirmed.
if os.path.exists(PREVIOUS_DB_DIR):
    raise FileExistsError(
        f"Previous database already exists: {PREVIOUS_DB_DIR}. "
        "Move or remove it before rebuilding."
    )

if os.path.exists(CHROMA_DB_DIR):
    os.replace(CHROMA_DB_DIR, PREVIOUS_DB_DIR)

try:
    os.replace(STAGING_DB_DIR, CHROMA_DB_DIR)
except Exception:
    if os.path.exists(PREVIOUS_DB_DIR) and not os.path.exists(CHROMA_DB_DIR):
        os.replace(PREVIOUS_DB_DIR, CHROMA_DB_DIR)
    raise

print(f"Index swapped into : {CHROMA_DB_DIR}")
