"""
Filename: metadata.py

Purpose
-------
Creates metadata for every chunk.

Responsibilities
----------------
- Build metadata
- Preserve document context
- Prepare data for embeddings

This component DOES NOT
-----------------------
- Clean text
- Chunk text
- Generate embeddings

Project
-------
AI Cloud Operations Assistant
"""

from src.models.chunk import Chunk


class Metadata:
    """
    Creates metadata for every chunk.
    """

    def create(
        self,
        chunk: Chunk,
        source,
        document: str,
    ) -> Chunk:
        """
        Populate metadata for a Chunk.

        Parameters
        ----------
        chunk : Chunk
            Chunk object.

        source
            Documentation source.

        document : str
            Document name.

        Returns
        -------
        Chunk
            Chunk enriched with metadata.
        """

        chunk.metadata.update(
            {
                "technology": source.name,
                "document": document,
                "source_url": source.urls[document],
                "chunk_id": chunk.chunk_id,
            }
        )

        return chunk
