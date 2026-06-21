"""
CHU Gold Standard v2 — Loader

Loads the self-contained gold standard dataset from chu_gold_dataset.json.
Each entry has: note_id, disease, orpha_id, text (clinical note), expected_hpo.

Usage:
    from clinical_notes.chu_gold_v2.loader import load_chu_gold_v2
    reports, gold_map = load_chu_gold_v2()
"""

import os
import json


DATASET_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "chu_gold_dataset.json"
)


def load_chu_gold_v2():
    """
    Load the CHU Gold Standard v2 dataset.

    Returns:
        reports: list of dicts with 'note_id', 'text', 'filename'
        gold_map: dict mapping note_id -> gold entry with 'expected_hpo', 'orpha_id', 'disease'
    """
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    reports = []
    gold_map = {}

    for entry in dataset:
        note_id = entry["note_id"]

        reports.append({
            "note_id": note_id,
            "text": entry["text"],
            "filename": entry["source_file"],
            "patient": note_id,  # Use note_id as patient key for consistency
        })

        gold_map[note_id] = {
            "disease": entry["disease"],
            "orpha_id": entry["orpha_id"],
            "expected_hpo": entry["expected_hpo"],
            "filename": entry["source_file"],
        }

    return reports, gold_map


# ── Quick test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    reports, gold = load_chu_gold_v2()
    print(f"Loaded {len(reports)} reports, {len(gold)} gold entries")
    print(f"Total expected HPO: {sum(len(g['expected_hpo']) for g in gold.values())}")
    print()
    for r in reports:
        g = gold[r["note_id"]]
        text_preview = r["text"][:60].replace("\n", " ")
        print(f"  {r['note_id']} | {g['disease'][:35]:<35} | {g['orpha_id']:<15} | {len(g['expected_hpo']):>2} HPO | {len(r['text']):>5} chars | {text_preview}...")
