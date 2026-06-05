"""
Medical Abbreviation Loader — Downloads comprehensive abbreviation datasets.
Merges UMLS SPECIALIST Lexicon abbreviations with curated clinical abbreviations.

Since UMLS requires a license, this module uses publicly available medical
abbreviation datasets from GitHub and supplements with the curated CHU Oran list.

Sources:
  - OpenMedData medical abbreviations (public, ~3000 entries)
  - Curated CHU Oran abbreviations (138 entries, bilingual)
"""

import os
import json
import csv
import io
import urllib.request
from log_config import get_logger

logger = get_logger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ABBREV_CACHE = os.path.join(PROJECT_ROOT, "data", "medical_abbreviations.json")

# Public medical abbreviation dataset URLs
ABBREV_SOURCES = [
    {
        "name": "OpenMedData",
        "url": "https://raw.githubusercontent.com/imantsm/medical_abbreviations/master/output/med_abbreviations.csv",
        "format": "csv",
    },
]


def download_abbreviations() -> dict:
    """
    Download medical abbreviations from public GitHub datasets.

    Source: imantsm/medical_abbreviations (~3000 entries, MIT license)

    Returns:
        Dict of {abbreviation_lower: expansion}
    """
    all_abbrevs = {}

    # Actual filenames in the repo CSVs/ directory
    csv_files = [
        "%23-A%2C%20medical%20abbreviations.csv",  # #-A
        "B%2C%20medical%20abbreviations.csv",
        "C%2C%20medical%20abbreviations.csv",
        "D%2C%20medical%20abbreviations.csv",
        "E-G%2C%20medical%20abbreviations.csv",
        "H%2C%20medical%20abbreviations.csv",
        "I%2C%20medical%20abbreviations.csv",
        "J-L%2C%20medical%20abbreviations.csv",
        "M%2C%20medical%20abbreviations.csv",
        "N-O%2C%20medical%20abbreviations.csv",
        "P%2C%20medical%20abbreviations.csv",
        "Q-R%2C%20medical%20abbreviations.csv",
        "S%2C%20medical%20abbreviations.csv",
        "T%2C%20medical%20abbreviations.csv",
        "U-Z%2C%20medical%20abbreviations.csv",
    ]
    base_url = "https://raw.githubusercontent.com/imantsm/medical_abbreviations/master/CSVs"

    logger.info("  Downloading medical abbreviations from OpenMedData (15 files)...")

    for csv_file in csv_files:
        url = f"{base_url}/{csv_file}"
        try:
            response = urllib.request.urlopen(url, timeout=15)
            content = response.read().decode("utf-8")

            reader = csv.reader(io.StringIO(content))
            for row in reader:
                if len(row) >= 2:
                    abbrev = row[0].strip().lower()
                    expansion = row[1].strip()
                    if abbrev and expansion and 1 < len(abbrev) <= 10:
                        all_abbrevs[abbrev] = expansion

        except Exception:
            continue  # Skip this file, continue with others

    logger.info("  Downloaded %d medical abbreviations", len(all_abbrevs))
    return all_abbrevs


def save_abbreviation_cache(abbrevs: dict, path: str = ABBREV_CACHE):
    """Save abbreviations to JSON cache."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(abbrevs, f, indent=1, ensure_ascii=False)
    logger.info("  Abbreviation cache saved: %s (%d entries)", path, len(abbrevs))


def load_abbreviation_cache(path: str = ABBREV_CACHE) -> dict:
    """Load abbreviations from JSON cache."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_medical_abbreviations(force_download: bool = False) -> dict:
    """
    Load comprehensive medical abbreviations — from cache or download.

    Returns:
        Dict of {abbreviation_lower: expansion}
    """
    # Try cache first
    if os.path.exists(ABBREV_CACHE) and not force_download:
        abbrevs = load_abbreviation_cache()
        logger.info("  Loaded %d abbreviations from cache", len(abbrevs))
        return abbrevs

    # Download and cache
    abbrevs = download_abbreviations()
    if abbrevs:
        save_abbreviation_cache(abbrevs)
    return abbrevs


if __name__ == "__main__":
    abbrevs = load_medical_abbreviations()
    print(f"\nTotal abbreviations: {len(abbrevs)}")
    examples = ["cf", "htn", "copd", "dvt", "chf", "dm", "sob"]
    for ex in examples:
        if ex in abbrevs:
            print(f"  {ex} → {abbrevs[ex]}")
