"""
Filename: cleaner.py

Purpose
-------
Normalizes extracted documentation text before chunking.

Responsibilities
----------------
- Normalize line endings
- Remove duplicate blank lines
- Remove leading/trailing spaces
- Preserve technical content

This component DOES NOT
-----------------------
- Remove knowledge
- Create chunks
- Generate metadata

Project
-------
AI Cloud Operations Assistant
"""

import re


class Cleaner:
    """
    Cleans extracted documentation text.
    """

    def clean(self, text: str) -> str:
        """
        Clean extracted documentation.

        Parameters
        ----------
        text : str
            Raw extracted documentation.

        Returns
        -------
        str
            Cleaned documentation.
        """

        text = self._normalize_line_endings(text)

        text = self._remove_extra_blank_lines(text)

        text = self._remove_trailing_spaces(text)

        return text

    def _normalize_line_endings(self, text: str) -> str:
        """
        Normalize all line endings to Unix style.
        """

        return text.replace("\r\n", "\n").replace("\r", "\n")

    def _remove_extra_blank_lines(self, text: str) -> str:
        """
        Reduce multiple blank lines to a single blank line.
        """

        return re.sub(r"\n{3,}", "\n\n", text)

    def _remove_trailing_spaces(self, text: str) -> str:
        """
        Remove leading and trailing spaces
        from every line.
        """

        lines = text.split("\n")

        cleaned_lines = []

        for line in lines:
            cleaned_lines.append(line.strip())

        return "\n".join(cleaned_lines)