"""
Filename: base_extractor.py

Purpose:
---------
Defines the common interface for all documentation extractors.

Every technology (Docker, Kubernetes, OpenShift, Helm, etc.)
must implement this interface.

Benefits:
---------
- Keeps scraper.py generic
- Makes adding new technologies easy
- Follows the Open/Closed Principle

Project:
--------
AI Cloud Operations Assistant
"""

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup


class BaseExtractor(ABC):
    """
    Abstract base class for documentation extractors.
    """

    @abstractmethod
    def extract(self, soup: BeautifulSoup) -> str:
        """
        Extract the main documentation content.

        Parameters
        ----------
        soup : BeautifulSoup
            Parsed HTML page.

        Returns
        -------
        str
            Extracted documentation text.
        """
        pass