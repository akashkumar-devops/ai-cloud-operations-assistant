"""
Filename: base_source.py

Purpose
-------
Represents a generic documentation source.

A source combines:
- Technology name
- Documentation URLs
- Extractor
- Output folder

Every documentation source (Docker, Kubernetes,
OpenShift, etc.) will inherit from this class.

Project
-------
AI Cloud Operations Assistant
"""

from extractors.base_extractor import BaseExtractor


class BaseSource:
    """
    Base class for every documentation source.
    """

    def __init__(
        self,
        name: str,
        urls: dict,
        extractor: BaseExtractor,
        output_folder: str,
    ):
        """
        Initialize a documentation source.

        Parameters
        ----------
        name : str
            Technology name.

        urls : dict
            Dictionary of documentation URLs.

        extractor : BaseExtractor
            Extractor responsible for parsing pages.

        output_folder : str
            Folder where raw documents are saved.
        """

        self.name = name
        self.urls = urls
        self.extractor = extractor
        self.output_folder = output_folder