"""
RareArena Gold Standard — HPO annotations for 30 RareArena clinical case reports

Source: RareArena (Chen et al., Lancet Digital Health, 2026)
        https://github.com/zhao-zy15/RareArena

Each entry contains:
  - note_id: matches the RareArena case report ID (RA_EN_001 ... RA_EN_030)
  - disease: the target rare disease
  - orpha_id: expected ORPHA code (from RareArena ground truth)
  - expected_hpo: list of HPO terms expected to be found in the text
                  (manually annotated based on phenotypes in the clinical text)
"""

import json
import os

_GS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "clinical_notes", "rarearena_cases", "rarearena_gold_standard.json"
)


def _load_gs():
    with open(_GS_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
    gs = {}
    for entry in raw:
        nid = entry["note_id"]
        gs[nid] = {
            "disease": entry["disease"],
            "orpha_id": entry["orpha_id"],
            "expected_hpo": [h["hpo_id"] for h in entry["expected_hpo"]],
        }
    return gs


GOLD_STANDARD_RA = _load_gs()
