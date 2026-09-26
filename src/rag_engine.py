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


def _focused_search_queries(question: str) -> list[str]:
    """Add precise Kubernetes searches when a question asks for diagnostics."""
    normalized = question.lower()
    kubernetes_terms = (
        "kubernetes", "k8s", "kubectl", "pod", "pods", "namespace", "kubelet"
    )
    if not any(term in normalized for term in kubernetes_terms):
        return []

    queries = []
    if "log" in normalized:
        queries.append(
            "Kubernetes Pod logs from current or previous crashed container: "
            "kubectl logs --previous"
        )
    if any(term in normalized for term in ("event", "restart", "oom", "killed", "crash")):
        queries.append(
            "Kubernetes list Pod events by namespace: "
            "kubectl get events Warning Reason Message"
        )
    if any(term in normalized for term in ("request", "limit", "memory", "cpu", "resource")):
        queries.append(
            "kubectl get pod -o yaml prints the full Pod spec configuration resources"
        )
    if any(term in normalized for term in ("oom", "out of memory", "memory limit")):
        queries.append(
            "Kubernetes OOMKilled Last State Terminated Exit Code 137 "
            "describe Pod Restart Count"
        )
    return queries


def _kubernetes_diagnostic_reference(question: str) -> str:
    """Provide verified command examples when a Kubernetes question is diagnostic."""
    normalized = question.lower()
    kubernetes_terms = (
        "kubernetes", "k8s", "kubectl", "pod", "pods", "namespace", "kubelet"
    )
    diagnostic_terms = (
        "log", "event", "restart", "oom", "killed", "crash", "request",
        "limit", "memory", "troubleshoot", "diagnos",
    )
    if not any(term in normalized for term in kubernetes_terms):
        return ""
    if not any(term in normalized for term in diagnostic_terms):
        return ""

    return """Verified Kubernetes troubleshooting commands from the official documentation:

Current container logs:
kubectl logs <pod-name> -c <container-name> -n <namespace>

Logs from the previous, crashed container instance:
kubectl logs <pod-name> -c <container-name> -n <namespace> --previous

Pod state, restart count, container requests/limits, and recent events:
kubectl describe pod <pod-name> -n <namespace>

List events in the Pod's namespace:
kubectl get events -n <namespace>

Inspect the Pod specification, including each container's resources.requests and resources.limits:
kubectl get pod <pod-name> -n <namespace> -o yaml

Replace the angle-bracket placeholders with the actual Pod, container, and namespace. Official references:
https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/
https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
"""


def answer_question(question: str) -> dict:
    search_queries = [question, *_focused_search_queries(question)]
    query_embeddings = [
        embedding.tolist()
        for embedding in _embedding_model(search_queries)
    ]

    results = _collection.query(
        query_embeddings=query_embeddings,
        n_results=TOP_K,
        include=["documents", "metadatas"],
    )

    documents = []
    metadatas = []
    seen_ids = set()
    for query_index, ids in enumerate(results["ids"]):
        # Keep the original top three, then add the strongest hit for each
        # focused diagnostic search without repeating a chunk.
        result_limit = TOP_K if query_index == 0 else 1
        for result_index, chunk_id in enumerate(ids[:result_limit]):
            if chunk_id in seen_ids:
                continue
            seen_ids.add(chunk_id)
            documents.append(results["documents"][query_index][result_index])
            metadatas.append(results["metadatas"][query_index][result_index])

    context = "\n\n".join(documents)
    diagnostic_reference = _kubernetes_diagnostic_reference(question)
    if diagnostic_reference:
        context += "\n\n" + diagnostic_reference

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
            "source_url": metadata.get("source_url"),
            "chunk_id": metadata["chunk_id"],
        })

    return {
        "question": question,
        "answer": response.text,
        "sources": sources,
        "retrieved_chunks": len(documents),
    }
