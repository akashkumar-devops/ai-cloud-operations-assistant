"""
Filename: chunk_text.py

Purpose
-------
Reads cleaned documentation, creates Chunk objects,
adds metadata, and saves them as JSON files.

Project
-------
AI Cloud Operations Assistant
"""

import json
import os
import argparse

from src.config import (
    CLEAN_DATA_DIR,
    CHUNK_DIR,
)

from src.processing.chunker import Chunker
from src.processing.metadata import Metadata
from src.sources.registry import SOURCES, get_source


def save_chunk(
    chunk,
    output_folder,
    filename,
):
    """
    Save a Chunk as JSON.
    """

    os.makedirs(
        output_folder,
        exist_ok=True,
    )

    filepath = os.path.join(
        output_folder,
        filename,
    )

    with open(
        filepath,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            chunk.to_dict(),
            file,
            indent=4,
            ensure_ascii=False,
        )


def main():
    """
    Execute the chunking pipeline.
    """

    chunker = Chunker()
    metadata = Metadata()

    total_documents = 0
    total_chunks = 0

    print("=" * 60)
    print("Chunk Generation Pipeline")
    print("=" * 60)

    parser = argparse.ArgumentParser(description="Chunk cleaned documentation.")
    parser.add_argument("--source", choices=[source.name for source in SOURCES])
    selected_source = parser.parse_args().source
    selected_documents = None
    if selected_source:
        selected_documents = next(
            source for source in SOURCES if source.name == selected_source
        ).urls

    for filename in sorted(os.listdir(CLEAN_DATA_DIR)):

        if not filename.endswith(".txt"):
            continue

        if selected_documents is not None and filename.removesuffix(".txt") not in selected_documents:
            continue

        document = filename.removesuffix(".txt")

        source = get_source(document)

        input_path = os.path.join(
            CLEAN_DATA_DIR,
            filename,
        )

        with open(
            input_path,
            "r",
            encoding="utf-8",
        ) as file:

            text = file.read()

        chunks = chunker.chunk(text)

        output_folder = os.path.join(
            CHUNK_DIR,
            source.name,
        )

        print(f"\nDocument : {document}")
        print(f"Technology : {source.name}")

        for chunk in chunks:

            metadata.create(
                chunk=chunk,
                source=source,
                document=document,
            )

            output_filename = (
                f"{document}_chunk_{chunk.chunk_id}.json"
            )

            save_chunk(
                chunk=chunk,
                output_folder=output_folder,
                filename=output_filename,
            )

        print(f"Chunks Created : {len(chunks)}")

        total_documents += 1
        total_chunks += len(chunks)

    print("\n" + "=" * 60)
    print("Pipeline Summary")
    print("=" * 60)
    print(f"Documents Processed : {total_documents}")
    print(f"Chunks Created      : {total_chunks}")
    print("=" * 60)


if __name__ == "__main__":
    main()
