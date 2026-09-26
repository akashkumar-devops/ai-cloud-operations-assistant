# ai-cloud-operations-assistant
AI Powered Cloud Operations Knowledge Assistant using RAG, Gemini and ChromaDB

## Install dependencies

- Runtime and Render deployment: `pip install -r requirements.txt`
- Local document ingestion and index rebuilding: `pip install -r requirements-build.txt`

The runtime uses ChromaDB's ONNX MiniLM embedding function to avoid loading PyTorch and SentenceTransformers in the web service process.

## Add or refresh Kubernetes knowledge

Kubernetes pages are pulled from the official Kubernetes documentation and indexed into the same Chroma collection used for Docker. This reuses the existing runtime embedding model; it does not add a second model or a new service.

Run these commands from the repository root after installing the build dependencies:

```powershell
python -m src.scraper --source kubernetes
```

```powershell
python -m src.clean_text --source kubernetes
```

```powershell
python -m src.chunk_text --source kubernetes
```

```powershell
python -m src.add_documents_to_store --source kubernetes
```

The `--source kubernetes` option limits each ingestion step to Kubernetes documents, so the existing Docker raw files and chunks are left alone. The final step incrementally upserts Kubernetes chunks into the existing index instead of rebuilding the Docker index. The indexed records retain their official page URL, which appears as a clickable source in the chat UI.
