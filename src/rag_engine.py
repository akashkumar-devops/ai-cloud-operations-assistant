"""
Filename: rag_engine.py

Purpose
-------
Core RAG engine for AI Cloud Operations Assistant.
"""

import math
import os
import re
import sqlite3
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv
from src.config import CHROMA_DB_DIR

COLLECTION_NAME = "cloud_operations_docs"
TOP_K = 3

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

_llm = genai.GenerativeModel("gemini-2.5-flash")
_chunks_cache: list[tuple[str, str, dict]] | None = None
_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "for",
    "from", "how", "i", "in", "is", "it", "me", "of", "on", "or", "the",
    "this", "to", "what", "when", "with", "you", "your",
}


def _load_chunks() -> list[tuple[str, str, dict]]:
    """Read indexed text and metadata from Chroma's SQLite store, without HNSW lookups."""
    global _chunks_cache
    if _chunks_cache is None:
        db_path = Path(CHROMA_DB_DIR).resolve() / "chroma.sqlite3"
        connection_uri = f"{db_path.as_uri()}?mode=ro"
        with sqlite3.connect(connection_uri, uri=True, timeout=5) as connection:
            rows = connection.execute(
                """
                SELECT
                    e.embedding_id,
                    MAX(CASE WHEN m.key = 'chroma:document'
                        THEN m.string_value END) AS document_text,
                    MAX(CASE WHEN m.key = 'technology'
                        THEN COALESCE(m.string_value, CAST(m.int_value AS TEXT)) END) AS technology,
                    MAX(CASE WHEN m.key = 'document'
                        THEN COALESCE(m.string_value, CAST(m.int_value AS TEXT)) END) AS document_name,
                    MAX(CASE WHEN m.key = 'source_url'
                        THEN m.string_value END) AS source_url,
                    MAX(CASE WHEN m.key = 'chunk_id'
                        THEN COALESCE(m.string_value, CAST(m.int_value AS TEXT)) END) AS chunk_id
                FROM embeddings AS e
                JOIN segments AS s ON s.id = e.segment_id
                JOIN collections AS c ON c.id = s.collection
                JOIN embedding_metadata AS m ON m.id = e.id
                WHERE c.name = ?
                GROUP BY e.id, e.embedding_id
                """,
                (COLLECTION_NAME,),
            ).fetchall()

        chunks = []
        for chunk_id, document_text, technology, document_name, source_url, source_chunk_id in rows:
            if not document_text:
                continue
            metadata = {
                "technology": technology or str(chunk_id).casefold().split("_", 1)[0],
                "document": document_name or "unknown",
                "source_url": source_url,
                "chunk_id": source_chunk_id or chunk_id,
            }
            chunks.append((str(chunk_id), document_text, metadata))
        _chunks_cache = chunks
    return _chunks_cache


def _tokens(text: str) -> list[str]:
    return [
        token for token in re.findall(r"[a-z0-9]+", text.casefold())
        if token not in _STOP_WORDS and len(token) > 1
    ]


def _retrieve_technology_chunks(
    query: str,
    technology: str | None,
    limit: int,
) -> list[tuple[str, str, dict]]:
    """Rank a small document set with BM25-style lexical scoring."""
    chunks = _load_chunks()
    if technology:
        chunks = [
            item for item in chunks
            if str(item[2].get("technology", "")).casefold() == technology.casefold()
        ]
    if not chunks or limit <= 0:
        return []

    query_tokens = _tokens(query)
    if not query_tokens:
        return []
    tokenized_docs = [_tokens(document) for _, document, _ in chunks]
    document_frequency = {
        token: sum(token in set(doc) for doc in tokenized_docs)
        for token in set(query_tokens)
    }
    average_length = sum(map(len, tokenized_docs)) / max(len(tokenized_docs), 1)

    scored = []
    for item, doc_tokens in zip(chunks, tokenized_docs):
        frequencies = {}
        for token in doc_tokens:
            frequencies[token] = frequencies.get(token, 0) + 1
        length = len(doc_tokens)
        score = 0.0
        for token in query_tokens:
            frequency = frequencies.get(token, 0)
            if not frequency:
                continue
            df = document_frequency[token]
            inverse_frequency = math.log(1 + (len(chunks) - df + 0.5) / (df + 0.5))
            denominator = frequency + 1.2 * (0.25 + 0.75 * length / max(average_length, 1))
            score += inverse_frequency * frequency * 2.2 / denominator
        normalized_text = " ".join(doc_tokens)
        normalized_query = " ".join(query_tokens)
        if normalized_query and normalized_query in normalized_text:
            score += 2.0
        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda entry: entry[0], reverse=True)
    return [item for _, item in scored[:limit]]


def _focused_search_queries(question: str) -> list[tuple[str, str, int]]:
    """Return a query, technology filter, and result limit for focused retrieval."""
    normalized = question.lower()
    asks_about_docker = "docker" in normalized
    asks_about_kubernetes = any(
        term in normalized
        for term in (
            "kubernetes", "k8s", "kubectl", "pod", "pods", "namespace",
            "kubelet", "deployment",
        )
    )

    docker_definition_terms = (
        "what is docker", "define docker", "explain docker", "what's docker",
        "what does docker",
    )
    is_docker_definition = any(term in normalized for term in docker_definition_terms)

    if asks_about_docker and asks_about_kubernetes:
        if any(term in normalized for term in ("health", "probe", "rollout")):
            docker_query = (
                "Dockerfile HEALTHCHECK container health status docker inspect "
                "logs events"
            )
            kubernetes_query = (
                "Kubernetes readinessProbe livenessProbe startupProbe Deployment "
                "rollout Pods Service traffic events logs"
            )
        elif "log" in normalized or "event" in normalized:
            docker_query = "Docker container logs docker logs inspect events"
            kubernetes_query = (
                "Kubernetes Pod logs events rollout Deployment Service endpoints"
            )
        else:
            docker_query = (
                "Docker Engine images containers builds and runs applications"
            )
            kubernetes_query = (
                "Kubernetes orchestrates containerized applications Pods "
                "Deployments Services scaling"
            )
        return [
            (docker_query, "docker", 2),
            (kubernetes_query, "kubernetes", 2),
        ]

    if asks_about_docker:
        if is_docker_definition:
            query = (
                "Docker Engine overview daemon dockerd REST API Docker CLI "
                "build and run containers"
            )
            limit = TOP_K
        elif "health" in normalized:
            query = (
                "Dockerfile HEALTHCHECK container health status docker inspect "
                "health logs events"
            )
            limit = 2
        elif "log" in normalized or "event" in normalized:
            query = "Docker container logs docker logs inspect events"
            limit = 2
        else:
            query = f"Docker documentation: {question}"
            limit = 2
        return [(query, "docker", limit)]

    if not asks_about_kubernetes:
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
    if not queries:
        queries.append(f"Kubernetes documentation: {question} Pods Deployments Services")
    return [(query, "kubernetes", 1) for query in queries]


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
    focused_searches = _focused_search_queries(question)
    documents = []
    metadatas = []
    seen_ids = set()
    search_plan = (
        [(query, technology, result_limit) for query, technology, result_limit in focused_searches]
        if focused_searches
        else [(question, None, TOP_K)]
    )

    for search_query, technology, result_limit in search_plan:
        query_results = _retrieve_technology_chunks(
            search_query,
            technology,
            result_limit,
        )
        for chunk_id, document, metadata in query_results:
            if chunk_id in seen_ids:
                continue
            seen_ids.add(chunk_id)
            documents.append(document)
            metadatas.append(metadata)

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

