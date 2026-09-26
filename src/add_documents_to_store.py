"""Incrementally add one registered source's chunks to the shared Chroma index."""

import argparse
import json
import os
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2

from src.config import CHROMA_DB_DIR, CHUNK_DIR
from src.sources.registry import SOURCES


COLLECTION_NAME = "cloud_operations_docs"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, choices=[source.name for source in SOURCES])
    source_name = parser.parse_args().source
    source = next(source for source in SOURCES if source.name == source_name)
    chunk_folder = os.path.join(CHUNK_DIR, source.name)

    if not os.path.isdir(chunk_folder):
        raise SystemExit(f"No chunks found for source '{source.name}': {chunk_folder}")

    records = []
    for filename in sorted(os.listdir(chunk_folder)):
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(chunk_folder, filename), encoding="utf-8") as file:
            chunk = json.load(file)
        metadata = chunk["metadata"]
        document = metadata["document"]
        metadata["source_url"] = source.urls[document]
        records.append(
            (
                f"{metadata['technology']}_{document}_{metadata['chunk_id']}",
                chunk["content"],
                metadata,
            )
        )

    if not records:
        raise SystemExit(f"No chunk files found for source '{source.name}'.")

    print(f"Preparing {len(records)} {source.name} chunks for the existing index...")
    embedding_model = ONNXMiniLM_L6_V2(
        preferred_providers=["CPUExecutionProvider"],
    )
    embedding_model.DOWNLOAD_PATH = Path(
        os.getenv(
            "CHROMA_MODEL_CACHE",
            Path(__file__).resolve().parents[1] / ".build-cache" / "chroma",
        )
    ) / embedding_model.MODEL_NAME
    embeddings = [
        embedding.tolist()
        for embedding in embedding_model([record[1] for record in records])
    ]

    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    collection = client.get_collection(COLLECTION_NAME)
    new_ids = {record[0] for record in records}
    batch_size = 100
    for start in range(0, len(records), batch_size):
        batch = records[start : start + batch_size]
        collection.upsert(
            ids=[record[0] for record in batch],
            documents=[record[1] for record in batch],
            metadatas=[record[2] for record in batch],
            embeddings=embeddings[start : start + batch_size],
        )

    existing = collection.get(
        where={"technology": source.name},
        include=["metadatas"],
    )
    stale_ids = [chunk_id for chunk_id in existing["ids"] if chunk_id not in new_ids]
    if stale_ids:
        collection.delete(ids=stale_ids)

    print(f"Added/updated {len(records)} {source.name} chunks.")
    print(f"Collection total: {collection.count()} chunks.")


if __name__ == "__main__":
    main()
