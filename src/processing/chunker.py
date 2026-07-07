"""
Filename: chunker.py

Purpose
-------
Splits cleaned documentation into embedding-ready chunks.

Responsibilities
----------------
- Prepare logical text units
- Build embedding-sized chunks
- Preserve context

This component DOES NOT
-----------------------
- Clean text
- Generate metadata
- Create embeddings

Project
-------
AI Cloud Operations Assistant
"""

from config import DEFAULT_CHUNK_SIZE


class Chunker:
    """
    Splits cleaned documentation into chunks.
    """

    def chunk(self, text: str) -> list[str]:
        """
        Split cleaned documentation into chunks.
        """

        if not text.strip():
            return []

        units = self._prepare_units(text)

        return self._build_chunks(units)

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

        units = []
        current_unit = []

        for line in text.splitlines():

            line = line.strip()

            if not line:

                if current_unit:
                    units.append("\n".join(current_unit))
                    current_unit = []

                continue

            current_unit.append(line)

        if current_unit:
            units.append("\n".join(current_unit))

        return units

    def _build_chunks(
        self,
        units: list[str],
    ) -> list[str]:
        """
        Build embedding-sized chunks.
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

                continue

            self._finalize_chunk(
                chunks,
                current_chunk,
            )

            if len(unit) <= DEFAULT_CHUNK_SIZE:

                current_chunk = unit

                continue

            remaining = unit

            while len(remaining) > DEFAULT_CHUNK_SIZE:

                split_index = remaining.rfind(
                    " ",
                    0,
                    DEFAULT_CHUNK_SIZE,
                )

                if split_index == -1:
                    split_index = DEFAULT_CHUNK_SIZE

                chunk = remaining[:split_index].strip()

                self._finalize_chunk(
                    chunks,
                    chunk,
                )

                remaining = remaining[split_index:].strip()

            current_chunk = remaining

        self._finalize_chunk(
            chunks,
            current_chunk,
        )

        return chunks

    def _finalize_chunk(
        self,
        chunks: list[str],
        current_chunk: str,
    ) -> None:
        """
        Store a completed chunk.
        """

        if current_chunk:
            chunks.append(current_chunk)