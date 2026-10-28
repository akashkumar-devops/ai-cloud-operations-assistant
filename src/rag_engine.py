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
    search_queries = [question, *(query for query, _, _ in focused_searches)]
    query_embeddings = [
        embedding.tolist()
        for embedding in _embedding_model(search_queries)
    ]

    documents = []
    metadatas = []
    seen_ids = set()
    if focused_searches:
        search_plan = [
            (index, technology, result_limit)
            for index, (_, technology, result_limit) in enumerate(focused_searches, start=1)
        ]
    else:
        search_plan = [(0, None, TOP_K)]

    collection_size = None
    for query_index, technology, result_limit in search_plan:
        query_args = {
            "query_embeddings": [query_embeddings[query_index]],
            "n_results": result_limit,
            "include": ["documents", "metadatas"],
        }
        if technology:
            # Avoid Chroma's filtered query/get path, which can fail with
            # "Error finding id" when metadata and HNSW state are out of sync.
            if collection_size is None:
                collection_size = _collection.count()
            if collection_size == 0:
                continue
            query_args["n_results"] = collection_size

        results = _collection.query(**query_args)
        query_results = []
        for result_index, chunk_id in enumerate(results["ids"][0]):
            metadata = results["metadatas"][0][result_index]
            if technology and metadata.get("technology") != technology:
                continue
            query_results.append((chunk_id, results["documents"][0][result_index], metadata))
            if len(query_results) >= result_limit:
                break

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

