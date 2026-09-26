"""
Filename: registry.py

Purpose
-------
Central registry of all supported documentation sources.

Every pipeline imports the source list from here.

Project
-------
AI Cloud Operations Assistant
"""

from src.sources.docker_source import DockerSource
from src.sources.kubernetes_source import KubernetesSource


SOURCES = [
    DockerSource(),
    KubernetesSource(),
]


def get_source(document: str):
    """
    Return the source that owns a document.

    Parameters
    ----------
    document : str
        Document name without extension.

    Returns
    -------
    BaseSource
        Matching source.

    Raises
    ------
    ValueError
        If no source owns the document.
    """

    for source in SOURCES:

        if document in source.urls:

            return source

    raise ValueError(
        f"No source registered for document: {document}"
    )
