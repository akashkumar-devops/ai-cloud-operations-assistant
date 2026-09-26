"""
Filename: clean_text.py

Purpose:
---------
Cleans raw documentation scraped from Docker Docs.

Responsibilities:
-----------------
1. Read all raw text files.
2. Remove navigation/UI elements.
3. Normalize whitespace.
4. Save cleaned text.

Input:
------
data/raw/

Output:
-------
data/cleaned/

Project:
--------
AI Cloud Operations Assistant
"""

import os
import re
import argparse

from src.config import RAW_DATA_DIR, CLEAN_DATA_DIR
from src.sources.registry import SOURCES

# =====================================================
# Create output directory
# =====================================================

os.makedirs(CLEAN_DATA_DIR, exist_ok=True)

# =====================================================
# Text that should never appear in RAG
# =====================================================

NOISE_LINES = {

    # Navigation
    "Home",
    "Back",
    "Manuals",
    "Guides",
    "Reference",

    # UI Buttons
    "Ask Gordon",
    "Copy Markdown",
    "View Markdown",

    # Footer
    "Edit this page",
    "Request changes",

    # Website Links
    "Product offerings",
    "Pricing",
    "About us",
    "Cookies Settings",
    "Terms of Use",
    "Status",
    "Legal",
}

# =====================================================
# Clean a single document
# =====================================================

def clean_document(text):
    """
    Removes website UI and normalizes whitespace.
    """

    cleaned_lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if line in NOISE_LINES:
            continue

        cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines)

    # Remove repeated blank lines
    cleaned_text = re.sub(r"\n{2,}", "\n", cleaned_text)

    # Remove repeated spaces
    cleaned_text = re.sub(r"[ ]{2,}", " ", cleaned_text)

    return cleaned_text.strip()


# =====================================================
# Main pipeline
# =====================================================

def main():

    processed = 0

    print("=" * 60)
    print("Cleaning Documentation")
    print("=" * 60)

    parser = argparse.ArgumentParser(description="Clean ingested documentation.")
    parser.add_argument("--source", choices=[source.name for source in SOURCES])
    selected_source = parser.parse_args().source
    selected_documents = None
    if selected_source:
        selected_documents = next(
            source for source in SOURCES if source.name == selected_source
        ).urls

    for filename in sorted(os.listdir(RAW_DATA_DIR)):

        if not filename.endswith(".txt"):
            continue

        if selected_documents is not None and filename.removesuffix(".txt") not in selected_documents:
            continue

        input_path = os.path.join(RAW_DATA_DIR, filename)

        output_path = os.path.join(CLEAN_DATA_DIR, filename)

        with open(input_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        cleaned_text = clean_document(raw_text)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        print(f"✔ {filename}")

        print(f"   Raw chars   : {len(raw_text):,}")
        print(f"   Clean chars : {len(cleaned_text):,}")

        processed += 1

    print("\n" + "=" * 60)
    print(f"Files Processed : {processed}")
    print("=" * 60)


# =====================================================
# Entry Point
# =====================================================

if __name__ == "__main__":
    main()
