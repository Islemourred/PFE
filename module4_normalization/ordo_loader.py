"""
ORDO Full Loader — Downloads and parses the official HPO disease annotations.
Replaces the 19 hardcoded disease profiles with 4,000+ from Orphanet/HPO.

Source: HPO Consortium (phenotype.hpoa)
URL: https://github.com/obophenotype/human-phenotype-ontology
Format: TSV with columns: database_id, disease_name, qualifier, hpo_id, ...

Usage:
    from module4_normalization.ordo_loader import load_ordo_profiles
    profiles = load_ordo_profiles()  # downloads once, caches as JSON
"""

import os
import json
import time
import urllib.request
from log_config import get_logger

logger = get_logger(__name__)

# Official HPO annotations file (maintained by HPO Consortium)
HPOA_URL = "https://github.com/obophenotype/human-phenotype-ontology/releases/latest/download/phenotype.hpoa"

# Cache paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HPOA_RAW_PATH = os.path.join(PROJECT_ROOT, "phenotype.hpoa")
ORDO_CACHE_PATH = os.path.join(PROJECT_ROOT, "data", "ordo_profiles.json")


def download_hpoa(url: str = HPOA_URL, output_path: str = HPOA_RAW_PATH) -> str:
    """
    Download the phenotype.hpoa file from the HPO GitHub releases.

    Args:
        url: URL to the phenotype.hpoa file
        output_path: where to save the downloaded file

    Returns:
        Path to the downloaded file
    """
    if os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        logger.info("phenotype.hpoa already exists (%.1f MB)", size_mb)
        return output_path

    logger.info("Downloading phenotype.hpoa from HPO Consortium...")
    logger.info("  URL: %s", url)

    start = time.time()
    try:
        urllib.request.urlretrieve(url, output_path)
        elapsed = round(time.time() - start, 1)
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        logger.info("  Downloaded %.1f MB in %ss", size_mb, elapsed)
        return output_path
    except Exception as e:
        logger.error("  Failed to download: %s", e)
        logger.warning("  Will use hardcoded profiles as fallback")
        return None


def parse_hpoa(hpoa_path: str) -> dict:
    """
    Parse the phenotype.hpoa file to extract ORPHA disease → HPO mappings.

    Only extracts ORPHA-prefixed diseases (Orphanet rare diseases).
    Filters out NOT-qualified annotations (negated phenotypes).

    Args:
        hpoa_path: path to the phenotype.hpoa TSV file

    Returns:
        Dict of {orpha_id: {"name": str, "hpo": set of HPO IDs}}
    """
    logger.info("Parsing phenotype.hpoa for ORPHA diseases...")
    start = time.time()

    profiles = {}
    total_lines = 0
    orpha_annotations = 0

    with open(hpoa_path, "r", encoding="utf-8") as f:
        for line in f:
            # Skip comments and header
            if line.startswith("#") or line.startswith("database_id"):
                continue

            total_lines += 1
            parts = line.strip().split("\t")
            if len(parts) < 4:
                continue

            db_id = parts[0].strip()        # e.g., "ORPHA:558"
            disease_name = parts[1].strip()  # e.g., "Marfan syndrome"
            qualifier = parts[2].strip()     # "NOT" or empty
            hpo_id = parts[3].strip()        # e.g., "HP:0001166"

            # Only ORPHA diseases
            if not db_id.startswith("ORPHA:"):
                continue

            # Skip negated phenotypes (qualifier = "NOT")
            if qualifier.upper() == "NOT":
                continue

            # Validate HPO ID format
            if not hpo_id.startswith("HP:"):
                continue

            orpha_annotations += 1

            if db_id not in profiles:
                profiles[db_id] = {
                    "name": disease_name,
                    "hpo": set(),
                }
            profiles[db_id]["hpo"].add(hpo_id)

    elapsed = round(time.time() - start, 1)
    logger.info("  Parsed %d lines, %d ORPHA annotations", total_lines, orpha_annotations)
    logger.info("  Found %d unique ORPHA diseases in %ss", len(profiles), elapsed)

    # Stats
    hpo_counts = [len(p["hpo"]) for p in profiles.values()]
    if hpo_counts:
        avg_hpo = sum(hpo_counts) / len(hpo_counts)
        logger.info("  Avg HPO terms per disease: %.1f (min=%d, max=%d)",
                     avg_hpo, min(hpo_counts), max(hpo_counts))

    return profiles


def save_ordo_cache(profiles: dict, cache_path: str = ORDO_CACHE_PATH):
    """Save parsed ORDO profiles to JSON cache for fast loading."""
    # Convert sets to lists for JSON serialization
    serializable = {}
    for orpha_id, data in profiles.items():
        serializable[orpha_id] = {
            "name": data["name"],
            "hpo": sorted(data["hpo"]),
        }

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=1, ensure_ascii=False)

    size_mb = os.path.getsize(cache_path) / (1024 * 1024)
    logger.info("  ORDO cache saved: %s (%.1f MB, %d diseases)",
                cache_path, size_mb, len(serializable))


def load_ordo_cache(cache_path: str = ORDO_CACHE_PATH) -> dict:
    """Load ORDO profiles from JSON cache."""
    with open(cache_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert lists back to sets
    profiles = {}
    for orpha_id, info in data.items():
        profiles[orpha_id] = {
            "name": info["name"],
            "hpo": set(info["hpo"]),
        }

    logger.info("  Loaded %d ORPHA disease profiles from cache", len(profiles))
    return profiles


def load_ordo_profiles(force_download: bool = False) -> dict:
    """
    Load ORDO disease profiles — from cache, or download + parse if needed.

    Args:
        force_download: if True, re-download even if cache exists

    Returns:
        Dict of {orpha_id: {"name": str, "hpo": set of HPO IDs}}
    """
    # 1. Try loading from cache
    if os.path.exists(ORDO_CACHE_PATH) and not force_download:
        return load_ordo_cache()

    # 2. Try downloading and parsing
    hpoa_path = download_hpoa()
    if hpoa_path and os.path.exists(hpoa_path):
        profiles = parse_hpoa(hpoa_path)
        save_ordo_cache(profiles)
        return profiles

    # 3. Fallback: return empty (will use hardcoded profiles)
    logger.warning("No ORDO data available — using hardcoded profiles only")
    return {}


# ── Quick test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    profiles = load_ordo_profiles()
    print(f"\nTotal ORPHA diseases: {len(profiles)}")

    # Show some examples
    examples = ["ORPHA:586", "ORPHA:558", "ORPHA:183660", "ORPHA:906", "ORPHA:47"]
    for oid in examples:
        if oid in profiles:
            p = profiles[oid]
            print(f"\n{oid}: {p['name']} ({len(p['hpo'])} HPO terms)")
            print(f"  Sample HPO: {sorted(p['hpo'])[:5]}")
