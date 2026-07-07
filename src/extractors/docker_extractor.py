"""
Filename: docker_extractor.py

Purpose
-------
Extracts documentation content from Docker documentation pages.

Responsibilities
----------------
1. Find the documentation article.
2. Remove navigation elements.
3. Return clean documentation text.

Project
-------
AI Cloud Operations Assistant
"""

from bs4 import BeautifulSoup

from src.extractors.base_extractor import BaseExtractor


class DockerExtractor(BaseExtractor):
    """
    Docker documentation extractor.
    """

    def extract(self, soup: BeautifulSoup) -> str:
        """
        Extract clean documentation from a Docker Docs page.
        """

        # ------------------------------------------
        # Find the main documentation article
        # ------------------------------------------

        article = soup.find("article")

        if article is None:
            return ""

        # ------------------------------------------
        # Remove breadcrumbs
        # Example:
        #
        # Home / Manuals / Docker Compose
        # ------------------------------------------

        breadcrumbs = article.find("nav", id="breadcrumbs")

        if breadcrumbs:
            breadcrumbs.decompose()

        # ------------------------------------------
        # Remove common UI elements
        # ------------------------------------------

        ui_text = [

            "Ask Gordon",
            "Copy Markdown",
            "View Markdown",
            "Edit this page",
            "Request changes",

        ]

        for element in article.find_all():

            if element.get_text(strip=True) in ui_text:
                element.decompose()

        # ------------------------------------------
        # Return cleaned article text
        # ------------------------------------------

        return article.get_text(
            separator="\n",
            strip=True
        )