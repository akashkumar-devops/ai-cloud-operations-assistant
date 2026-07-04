"""
Filename: docker_source.py

Purpose
-------
Represents Docker as a documentation source.

This class combines:
- Docker URLs
- Docker extractor
- Output folder

Project
-------
AI Cloud Operations Assistant
"""

from sources.base_source import BaseSource

from docs.docker_urls import DOCKER_URLS
from extractors.docker_extractor import DockerExtractor

from config import RAW_DATA_DIR


class DockerSource(BaseSource):
    """
    Docker documentation source.
    """

    def __init__(self):
        """
        Initialize the Docker documentation source.
        """

        super().__init__(
            name="docker",
            urls=DOCKER_URLS,
            extractor=DockerExtractor(),
            output_folder=RAW_DATA_DIR,
        )