"""
Filename: config.py

Purpose:
---------
Stores all project-wide configuration values.

Changing paths, models, or settings only requires updating this file.

Used By:
--------
- scraper.py
- clean_text.py
- chunk_text.py
- embed_store.py
- search.py
- rag_chat.py

Project:
--------
AI Cloud Operations Assistant
"""


# =====================================================
# ChromaDB Configuration
# =====================================================

COLLECTION_NAME = "docker_docs"

# =====================================================
# Embedding Model
# =====================================================

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# =====================================================
# HTTP Request Configuration
# =====================================================

REQUEST_TIMEOUT = 15

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0 Safari/537.36"
    )
}

# =====================================================
# Data folders
# =====================================================

RAW_DATA_DIR = "data/raw"
CLEAN_DATA_DIR = "data/cleaned"
CHUNK_DIR = "data/chunks"
CHROMA_DB_DIR = "chroma_db_complete"

# =====================================================
# Processing Configuration
# =====================================================

DEFAULT_CHUNK_SIZE = 800

DEFAULT_CHUNK_OVERLAP = 100
