"""Kubernetes documentation source configuration."""

from src.config import RAW_DATA_DIR
from src.docs.kubernetes_urls import KUBERNETES_URLS
from src.extractors.kubernetes_extractor import KubernetesExtractor
from src.sources.base_source import BaseSource


class KubernetesSource(BaseSource):
    """Official Kubernetes documentation pages for ingestion."""

    def __init__(self):
        super().__init__(
            name="kubernetes",
            urls=KUBERNETES_URLS,
            extractor=KubernetesExtractor(),
            output_folder=RAW_DATA_DIR,
        )
