"""
RareArena Clinical Case Loader

Loads 30 curated clinical case reports from the RareArena dataset
(Chen et al., Lancet Digital Health, 2026).

Source: https://github.com/zhao-zy15/RareArena
"""

import json
import os

_CASES_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "rarearena_cases", "rarearena_cases.json"
)


def load_rarearena_cases() -> list:
    """Load the 30 curated RareArena clinical case reports."""
    if not os.path.exists(_CASES_PATH):
        print(f"[!] RareArena cases not found at {_CASES_PATH}")
        return []
    with open(_CASES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    cases = load_rarearena_cases()
    print(f"Loaded {len(cases)} RareArena cases")
    for c in cases:
        print(f"  {c['note_id']}: {c['disease'][:50]} ({c['word_count']} words)")
