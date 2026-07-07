"""
Filename: test_chunker.py

Purpose
-------
Test the Chunker using a real cleaned
documentation file.

Project
-------
AI Cloud Operations Assistant
"""

from pathlib import Path

import sys

project_root = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(project_root))

from processing.chunker import Chunker


def main():

    project_root = Path(__file__).resolve().parents[2]

    file_path = (
        project_root
        / "data"
        / "cleaned"
        / "docker_engine.txt"
    )

    text = file_path.read_text(
        encoding="utf-8"
    )

    chunker = Chunker()

    units = chunker._prepare_units(text)

    print(f"Units : {len(units)}")
    
    chunks = chunker.chunk(text)

    print("=" * 60)
    print("Chunker Test")
    print("=" * 60)

    print(f"\nFile: {file_path.name}")
    print(f"Characters : {len(text)}")
    print(f"Chunks     : {len(chunks)}")

    print("\nChunk Sizes")

    for index, chunk in enumerate(chunks, start=1):

        print(
            f"Chunk {index}: "
            f"{len(chunk)} characters"
        )

    print("\nFirst Chunk Preview")
    print("-" * 60)

    print(chunks[0][:800])

if __name__ == "__main__":
    main()

