"""
Filename: chunker.py

Purpose
-------
Splits cleaned documentation into embedding-ready chunks.

Responsibilities
----------------
- Prepare logical text units
- Merge units into embedding-sized chunks
- Preserve context as much as possible

This component DOES NOT
-----------------------
- Clean text
- Generate metadata
- Create embeddings

Project
-------
AI Cloud Operations Assistant
"""

from config import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
)


class Chunker:
    """
    Splits cleaned documentation into chunks.
    """

    def chunk(self, text: str) -> list[str]:
        """
        Split cleaned documentation into chunks.

        Parameters
        ----------
        text : str
            Cleaned documentation.

        Returns
        -------
        list[str]
            Embedding-ready chunks.
        """

        if not text.strip():
            return []

        units = self._prepare_units(text)

        chunks = self._merge_units(units)

        return chunks

    def _prepare_units(
        self,
        text: str,
    ) -> list[str]:
        """
        Prepare logical text units.

        V1:
        Paragraphs

        Future:
        - Markdown headings
        - HTML sections
        - Semantic sections
        """

        return [
            unit.strip()
            for unit in text.split("\n\n")
            if unit.strip()
        ]

    def _merge_units(
        self,
        units: list[str],
    ) -> list[str]:
        """
        Merge logical units into embedding-sized chunks.
        """

        chunks = []

        current_chunk = ""

        for unit in units:

            projected_size = (
                len(current_chunk)
                + len(unit)
                + 2
            )

            if projected_size <= DEFAULT_CHUNK_SIZE:

                if current_chunk:
                    current_chunk += "\n\n"

                current_chunk += unit

            else:

                if current_chunk:
                    chunks.append(current_chunk)

                current_chunk = unit

        if current_chunk:
            chunks.append(current_chunk)

        return chunks