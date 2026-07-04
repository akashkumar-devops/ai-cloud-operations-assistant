"""
Filename: section.py

Purpose
-------
Represents a logical documentation section.

A section contains:
- Heading
- Paragraphs

Project
-------
AI Cloud Operations Assistant
"""

from dataclasses import dataclass


@dataclass
class Section:
    """
    Represents one logical documentation section.
    """

    heading: str

    paragraphs: list[str]