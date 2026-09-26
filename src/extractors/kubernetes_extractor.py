"""Extract the main article text from Kubernetes documentation pages."""

from bs4 import BeautifulSoup

from src.extractors.base_extractor import BaseExtractor


class KubernetesExtractor(BaseExtractor):
    """Remove Kubernetes site chrome and return the documentation article."""

    def extract(self, soup: BeautifulSoup) -> str:
        article = soup.select_one(".td-content") or soup.find("main")
        if article is None:
            return ""

        for element in article.select(
            "nav, script, style, button, .edit-page, .feedback, .td-page-meta"
        ):
            element.decompose()

        return article.get_text(separator="\n", strip=True)
