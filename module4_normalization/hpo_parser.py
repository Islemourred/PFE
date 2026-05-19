"""
HPO Parser — Parses the hp.owl (OWL/XML) file to extract all HPO terms.
Extracts: HPO ID, label (official name), exact synonyms, related synonyms,
           UMLS cross-references, and definitions.
Uses iterative XML parsing (iterparse) to handle the large 73MB file efficiently.
"""

import xml.etree.ElementTree as ET
import json
import os
import time

# OWL/XML namespaces used in hp.owl
NS = {
    "owl":      "http://www.w3.org/2002/07/owl#",
    "rdf":      "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs":     "http://www.w3.org/2000/01/rdf-schema#",
    "obo":      "http://purl.obolibrary.org/obo/",
    "oboInOwl": "http://www.geneontology.org/formats/oboInOwl#",
}

HPO_URI_PREFIX = "http://purl.obolibrary.org/obo/HP_"


def parse_hpo_owl(owl_path: str) -> list[dict]:
    """
    Parse hp.owl and extract all HPO terms with their metadata.

    Args:
        owl_path: path to hp.owl file

    Returns:
        List of dicts, each containing:
        {
            "id":               "HP:0001382",
            "name":             "Joint hypermobility",
            "definition":       "The capability that a joint...",
            "exact_synonyms":   ["Flexible joints", "Lax joints", ...],
            "related_synonyms": ["Joint instability", ...],
            "xrefs":            ["UMLS:C1844820", "SNOMEDCT_US:298181000"]
        }
    """
    print(f"Parsing HPO ontology from: {owl_path}")
    start = time.time()

    terms = []

    # --- Iterative parsing for memory efficiency ---
    # We look for <owl:Class> elements whose rdf:about starts with the HP_ prefix
    context = ET.iterparse(owl_path, events=("end",))

    for event, elem in context:
        # We only care about owl:Class elements
        if elem.tag != f"{{{NS['owl']}}}Class":
            continue

        # Check if this is an HP term
        about = elem.get(f"{{{NS['rdf']}}}about", "")
        if not about.startswith(HPO_URI_PREFIX):
            # Free memory for non-HP elements
            elem.clear()
            continue

        # --- Extract HPO ID ---
        hpo_id_elem = elem.find(f"{{{NS['oboInOwl']}}}id")
        if hpo_id_elem is None or hpo_id_elem.text is None:
            elem.clear()
            continue
        hpo_id = hpo_id_elem.text.strip()

        # --- Extract label (official name) ---
        label_elem = elem.find(f"{{{NS['rdfs']}}}label")
        name = label_elem.text.strip() if label_elem is not None and label_elem.text else ""

        # Skip obsolete terms (they have "obsolete" in the name)
        if name.lower().startswith("obsolete"):
            elem.clear()
            continue

        # --- Extract definition ---
        def_elem = elem.find(f"{{{NS['obo']}}}IAO_0000115")
        definition = def_elem.text.strip() if def_elem is not None and def_elem.text else ""

        # --- Extract exact synonyms ---
        exact_synonyms = []
        for syn in elem.findall(f"{{{NS['oboInOwl']}}}hasExactSynonym"):
            if syn.text:
                exact_synonyms.append(syn.text.strip())

        # --- Extract related synonyms ---
        related_synonyms = []
        for syn in elem.findall(f"{{{NS['oboInOwl']}}}hasRelatedSynonym"):
            if syn.text:
                related_synonyms.append(syn.text.strip())

        # --- Extract cross-references (UMLS, SNOMED, etc.) ---
        xrefs = []
        for xref in elem.findall(f"{{{NS['oboInOwl']}}}hasDbXref"):
            if xref.text:
                xrefs.append(xref.text.strip())

        terms.append({
            "id": hpo_id,
            "name": name,
            "definition": definition,
            "exact_synonyms": exact_synonyms,
            "related_synonyms": related_synonyms,
            "xrefs": xrefs,
        })

        # Free memory
        elem.clear()

    elapsed = round(time.time() - start, 1)
    print(f"Parsed {len(terms)} HPO terms in {elapsed}s")
    return terms


def save_hpo_json(terms: list[dict], output_path: str):
    """Save parsed HPO terms to a JSON file for fast future loading."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(terms, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(terms)} terms to {output_path}")


def load_hpo_json(json_path: str) -> list[dict]:
    """Load previously parsed HPO terms from JSON."""
    with open(json_path, "r", encoding="utf-8") as f:
        terms = json.load(f)
    print(f"Loaded {len(terms)} HPO terms from {json_path}")
    return terms


def get_hpo_terms(owl_path: str, cache_path: str = None) -> list[dict]:
    """
    Get HPO terms — loads from cache JSON if available,
    otherwise parses the OWL file and caches the result.

    Args:
        owl_path:   path to hp.owl
        cache_path: path to cached JSON (default: same dir as owl, named hpo_terms.json)

    Returns:
        List of HPO term dicts
    """
    if cache_path is None:
        cache_path = os.path.join(os.path.dirname(owl_path), "hpo_terms.json")

    if os.path.exists(cache_path):
        return load_hpo_json(cache_path)

    terms = parse_hpo_owl(owl_path)
    save_hpo_json(terms, cache_path)
    return terms


# ── Quick test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    owl_file = sys.argv[1] if len(sys.argv) > 1 else "hp.owl"
    terms = get_hpo_terms(owl_file)

    # Show a few examples
    for t in terms[:5]:
        print(f"\n{t['id']} — {t['name']}")
        if t["exact_synonyms"]:
            print(f"  Synonyms: {t['exact_synonyms'][:5]}")
        if t["xrefs"]:
            print(f"  Xrefs:    {t['xrefs'][:3]}")
