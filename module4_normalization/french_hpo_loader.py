"""
French HPO Loader — Downloads official HPO French translations from Orphanet/INSERM.
Replaces the hardcoded 100-entry dictionary with 25,000+ official French labels.

Source: HPO International Consortium (Babelon format)
  - Labels: http://purl.obolibrary.org/obo/hp/translations/hp-fr.babelon.tsv
  - Synonyms: http://purl.obolibrary.org/obo/hp/translations/hp-fr.synonyms.tsv

The downloaded data is cached as JSON for instant loading on subsequent runs.
"""

import os
import json
import urllib.request
from log_config import get_logger

logger = get_logger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FR_HPO_CACHE = os.path.join(PROJECT_ROOT, "data", "hpo_french_labels.json")
FR_EN_CACHE = os.path.join(PROJECT_ROOT, "data", "hpo_fr_en_translations.json")

# Official HPO French translation URLs (Orphanet/INSERM maintained)
HPO_FR_LABELS_URL = "http://purl.obolibrary.org/obo/hp/translations/hp-fr.babelon.tsv"
HPO_FR_SYNONYMS_URL = "http://purl.obolibrary.org/obo/hp/translations/hp-fr.synonyms.tsv"


def download_french_hpo() -> tuple[dict, dict]:
    """
    Download official French HPO translations from Orphanet/INSERM.

    Returns:
        (fr_hpo_mapping, fr_en_translations)
        - fr_hpo_mapping: {french_term_lower: (hpo_id, english_name)}
        - fr_en_translations: {french_term_lower: english_term}
    """
    fr_hpo = {}
    fr_en = {}

    # ── Download main labels ──
    try:
        logger.info("  Downloading official HPO French labels from Orphanet/INSERM...")
        response = urllib.request.urlopen(HPO_FR_LABELS_URL, timeout=60)
        content = response.read().decode("utf-8")
        lines = content.strip().split("\n")

        for line in lines[1:]:  # Skip header
            parts = line.strip().split("\t")
            if len(parts) >= 8:
                hpo_id = parts[0].strip()
                en_name = parts[5].strip()
                fr_name = parts[7].strip()

                if hpo_id.startswith("HP:") and fr_name and en_name:
                    fr_lower = fr_name.lower()
                    fr_hpo[fr_lower] = (hpo_id, en_name)
                    fr_en[fr_lower] = en_name

        logger.info("  Loaded %d French HPO labels", len(fr_hpo))

    except Exception as e:
        logger.warning("  Failed to download HPO French labels: %s", e)

    # ── Download synonyms ──
    try:
        logger.info("  Downloading HPO French synonyms...")
        response = urllib.request.urlopen(HPO_FR_SYNONYMS_URL, timeout=60)
        content = response.read().decode("utf-8")
        lines = content.strip().split("\n")

        syn_count = 0
        for line in lines[1:]:
            parts = line.strip().split("\t")
            if len(parts) >= 8:
                hpo_id = parts[0].strip()
                en_name = parts[5].strip()
                fr_syn = parts[7].strip()

                if hpo_id.startswith("HP:") and fr_syn:
                    fr_lower = fr_syn.lower()
                    if fr_lower not in fr_hpo:
                        fr_hpo[fr_lower] = (hpo_id, en_name)
                        fr_en[fr_lower] = en_name
                        syn_count += 1

        logger.info("  Loaded %d additional French synonyms", syn_count)

    except Exception as e:
        logger.warning("  French synonyms not available: %s", e)

    return fr_hpo, fr_en


def save_cache(fr_hpo: dict, fr_en: dict):
    """Save French HPO data to JSON cache."""
    # Convert tuples to lists for JSON serialization
    serializable = {k: list(v) for k, v in fr_hpo.items()}
    with open(FR_HPO_CACHE, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=1, ensure_ascii=False)

    with open(FR_EN_CACHE, "w", encoding="utf-8") as f:
        json.dump(fr_en, f, indent=1, ensure_ascii=False)

    logger.info("  French HPO cache saved: %d labels, %d translations",
                len(fr_hpo), len(fr_en))


def load_french_hpo(force_download: bool = False) -> tuple[dict, dict]:
    """
    Load French HPO mappings — from cache or download.

    Returns:
        (fr_hpo_mapping, fr_en_translations)
    """
    if os.path.exists(FR_HPO_CACHE) and not force_download:
        with open(FR_HPO_CACHE, "r", encoding="utf-8") as f:
            raw = json.load(f)
            fr_hpo = {k: tuple(v) for k, v in raw.items()}
        with open(FR_EN_CACHE, "r", encoding="utf-8") as f:
            fr_en = json.load(f)
        logger.info("  Loaded %d French HPO labels from cache", len(fr_hpo))
        return fr_hpo, fr_en

    fr_hpo, fr_en = download_french_hpo()
    if fr_hpo:
        save_cache(fr_hpo, fr_en)
    return fr_hpo, fr_en


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    fr_hpo, fr_en = load_french_hpo(force_download=True)
    print(f"\nTotal French HPO labels: {len(fr_hpo)}")
    print(f"Total FR→EN translations: {len(fr_en)}")

    # Test common terms
    test_terms = ["fièvre", "anémie", "dyspnée", "eczéma", "ataxie",
                  "thrombopénie", "hépatite", "céphalée", "asthénie"]
    print("\nSample lookups:")
    for term in test_terms:
        if term in fr_hpo:
            print(f"  {term} → {fr_hpo[term][0]} ({fr_hpo[term][1]})")
        else:
            print(f"  {term} → NOT FOUND")
