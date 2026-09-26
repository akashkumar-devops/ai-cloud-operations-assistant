"""
Filename: rag_engine.py

Purpose
-------
Core RAG engine for AI Cloud Operations Assistant.
"""

import os
import chromadb
import google.generativeai as genai
from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2
from dotenv import load_dotenv
from src.config import CHROMA_DB_DIR

COLLECTION_NAME = "cloud_operations_docs"
TOP_K = 3

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

_embedding_model = ONNXMiniLM_L6_V2(
    preferred_providers=["CPUExecutionProvider"],
)
_llm = genai.GenerativeModel("gemini-2.5-flash")
_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
_collection = _client.get_collection(COLLECTION_NAME)

def answer_question(question: str) -> dict:
    query_embedding = _embedding_model([question])[0].tolist()

    results = _collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K,
        include=["documents", "metadatas"],
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    context = "\n\n".join(documents)

    prompt = f"""
You are an AI Cloud Operations Assistant.

Instructions:
- Answer ONLY using the provided context.
- If the answer cannot be found in the context, clearly say so.
- Do not invent information.
- Be technically accurate.
- Answer in a clear and structured way.
- Put every runnable command in its own fenced code block. Keep explanatory text outside the code block, and do not combine unrelated commands in one block.
- Label command blocks with the appropriate shell when known (for example, bash or powershell).

Context
========
{context}

Question
========
{question}

Answer
========
"""

    response = _llm.generate_content(prompt)

    sources = []
    for metadata in metadatas:
        sources.append({
            "technology": metadata["technology"],
            "document": metadata["document"],
            "chunk_id": metadata["chunk_id"],
        })

    return {
        "question": question,
        "answer": response.text,
        "sources": sources,
        "retrieved_chunks": len(documents),
    }
