"""Read GSC cases and print summaries for gold standard creation."""
import json, sys, os
sys.stdout.reconfigure(encoding="utf-8")

cases = json.load(open(
    os.path.join(os.path.dirname(__file__), "clinical_notes", "gsc_cases", "gsc_cases.json"),
    "r", encoding="utf-8"
))

for c in cases:
    print(f"\n{'='*70}")
    print(f"  {c['note_id']} — {c['disease']} ({c['word_count']}w)")
    print(f"  PMID: {c['pmid']}")
    print(f"{'='*70}")
    # Print first 600 chars of the text
    print(c["text"][:600])
    print("...")
