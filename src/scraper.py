"""
Filename: scraper.py

Purpose
-------
Downloads documentation pages from one or more sources,
extracts their content, and stores the raw text.

Responsibilities
----------------
- Iterate through documentation sources
- Download webpages
- Delegate HTML extraction to the appropriate extractor
- Save raw text

Project
-------
AI Cloud Operations Assistant
"""

import os

import requests
from bs4 import BeautifulSoup

from src.config import (
    HEADERS,
    REQUEST_TIMEOUT,
)

from src.sources.registry import SOURCES


def fetch_page(url):
    """
    Download a webpage and return a BeautifulSoup object.
    """

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        return BeautifulSoup(
            response.text,
            "html.parser",
        )

    except requests.RequestException as e:

        print(f"❌ Failed to download:\n{url}")
        print(e)

        return None


def save_document(
    output_folder,
    filename,
    text,
):
    """
    Save extracted text.
    """

    os.makedirs(output_folder, exist_ok=True)

    filepath = os.path.join(
        output_folder,
        f"{filename}.txt",
    )

    with open(
        filepath,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(text)

    return filepath


def main():
    """
    Run the scraping pipeline.
    """

    total_saved = 0
    total_skipped = 0

    print("=" * 60)
    print("Knowledge Ingestion Engine")
    print("=" * 60)

    for source in SOURCES:

        print(f"\nProcessing Source: {source.name}")

        saved = 0
        skipped = 0

        for name, url in source.urls.items():

            print(f"\nScraping: {name}")

            soup = fetch_page(url)

            if soup is None:

                skipped += 1
                continue

            text = source.extractor.extract(soup)

            if not text:

                print("⚠ No content extracted.")

                skipped += 1
                continue

            filepath = save_document(
                output_folder=source.output_folder,
                filename=name,
                text=text,
            )

            print(f"✔ Saved: {filepath}")
            print(f"Characters: {len(text):,}")

            saved += 1

        print(f"\nCompleted {source.name}")
        print(f"Saved: {saved}")
        print(f"Skipped: {skipped}")

        total_saved += saved
        total_skipped += skipped

    print("\n" + "=" * 60)
    print("Overall Summary")
    print("=" * 60)
    print(f"Saved   : {total_saved}")
    print(f"Skipped : {total_skipped}")
    print("=" * 60)


if __name__ == "__main__":
    main()