"""
Filename: chunk.py

Purpose
-------
Represents a single chunk of knowledge.

A Chunk is the core unit that flows through the
AI Cloud Operations Assistant pipeline.

Project
-------
AI Cloud Operations Assistant
"""

from dataclasses import dataclass, field


@dataclass
class Chunk:
    """
    Represents a single knowledge chunk.
    """

    chunk_id: int

    content: str

    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """
        Convert the Chunk into a dictionary.

        Returns
        -------
        dict
            Dictionary representation of the chunk.
        """

        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "metadata": self.metadata,
        }