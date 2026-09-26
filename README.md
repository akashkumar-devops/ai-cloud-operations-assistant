# ai-cloud-operations-assistant
AI Powered Cloud Operations Knowledge Assistant using RAG, Gemini and ChromaDB

## Install dependencies

- Runtime and Render deployment: `pip install -r requirements.txt`
- Local document ingestion and index rebuilding: `pip install -r requirements-build.txt`

The runtime uses ChromaDB's ONNX MiniLM embedding function to avoid loading PyTorch and SentenceTransformers in the web service process.
