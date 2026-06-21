"""
CHU Gold Standard v2 — English Translated Loader

Loads the translated CHU dataset from chu_reports_en.json.
Uses the SAME gold standard (expected_hpo, orpha_id) as the French version.

Usage:
    from clinical_notes.chu_gold_v2.loader_en import load_chu_gold_v2_en
    reports, gold_map = load_chu_gold_v2_en()
"""

import os
import json


DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "chu_translated",
    "chu_reports_en.json"
)


def load_chu_gold_v2_en():
    """
    Load the CHU Gold Standard v2 English (translated) dataset.

    Returns:
        reports: list of dicts with 'note_id', 'text' (English), 'filename'
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
            "text": entry["text"],  # English text
            "filename": f"translated_{note_id}",
            "patient": note_id,
        })

        gold_map[note_id] = {
            "disease": entry["disease"],
            "orpha_id": entry["orpha_id"],
            "expected_hpo": entry["expected_hpo"],
            "filename": f"translated_{note_id}",
        }

    return reports, gold_map


# ── Quick test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    reports, gold = load_chu_gold_v2_en()
    print(f"Loaded {len(reports)} EN reports, {len(gold)} gold entries")
    print(f"Total expected HPO: {sum(len(g['expected_hpo']) for g in gold.values())}")
    print()
    for r in reports:
        g = gold[r["note_id"]]
        text_preview = r["text"][:60].replace("\n", " ")
        print(f"  {r['note_id']} | {g['disease'][:35]:<35} | {g['orpha_id']:<15} | {len(g['expected_hpo']):>2} HPO | {len(r['text']):>5} chars | {text_preview}...")
