"""
Run All Notes - Execute the full 4-module BILINGUAL pipeline
on all test notes (English + French) and evaluate results.

Usage:
    python run_all_notes.py           # Run both EN + FR
    python run_all_notes.py --fr      # Run French notes only
    python run_all_notes.py --en      # Run English notes only
"""

import os
import sys
import json
import time

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mock_data import raw_notes
from mock_data_fr import get_french_notes
from pipeline import FullPipeline
from evaluation.gold_standard import GOLD_STANDARD, get_all_note_ids
from evaluation.gold_standard_fr import GOLD_STANDARD_FR
from evaluation.metrics import evaluate_note, compute_aggregate_metrics

CLINICAL_NOTES_EN = {note["id"]: note for note in raw_notes}
CLINICAL_NOTES_FR = get_french_notes()


def run_notes(pipeline_obj, notes_dict, lang, output_dir, gold_standard=None):
    """Run pipeline on a set of notes and return metrics."""
    all_metrics = []

    for note_id, note_data in notes_dict.items():
        print(f"\n{'='*40}")
        print(f" {note_id} ({lang.upper()})")
        print(f"{'='*40}")

        clinical_text = note_data.get("text", "")
        if not clinical_text:
            print(f"  WARNING: No text found for {note_id}, skipping.")
            continue

        start = time.time()
        result = pipeline_obj.process_and_save(
            clinical_text=clinical_text,
            note_id=note_id,
            output_dir=output_dir,
            lang=lang,
        )
        elapsed = round(time.time() - start, 2)
        print(f"  Processing time: {elapsed}s")

        # Show Module 3 results
        warnings = result["module3"]["warnings"]
        if warnings["temporal"]:
            for w in warnings["temporal"]:
                print(f"  TEMPORAL: {w['message']}")
        if warnings["inconsistencies"]:
            for w in warnings["inconsistencies"]:
                print(f"  INCONSISTENCY: {w['message']}")

        numeric = result["module3"]["numeric_phenotypes"]
        if numeric:
            print(f"  Numeric phenotypes: {len(numeric)}")
            for np_item in numeric:
                print(f"      {np_item['hpo_name']} ({np_item['source']})")

        # Count negated
        negated_count = sum(
            1 for cat in ["problem", "treatment", "test"]
            for e in result["module2"]["entities"].get(cat, [])
            if e.get("negated", False)
        )
        if negated_count:
            print(f"  Negated entities: {negated_count}")

        # ORDO candidates
        ordo = result["module4"].get("ordo_candidates", [])
        if ordo:
            top = ordo[0]
            name_display = top.get("name_fr") or top["name"]
            print(f"  Top ORDO: {name_display} (score={top['score']:.3f})")

        # Stats
        stats = result["module4"].get("stats", {})
        print(f"  Entities: {stats.get('total', 0)} total, "
              f"{stats.get('matched', 0)} matched HPO, "
              f"{stats.get('unmatched', 0)} unmatched")

        # Evaluate against gold standard if available
        gold = (gold_standard or {}).get(note_id, {})
        if gold and gold.get("expected_hpo"):
            metrics = evaluate_note(result["step2"], gold)
            metrics["note_id"] = note_id
            metrics["pathology"] = gold.get("pathology", note_data.get("pathology", "Unknown"))
            metrics["processing_time"] = elapsed
            metrics["language"] = lang
            all_metrics.append(metrics)
            print(f"  P={metrics['precision']:.3f} R={metrics['recall']:.3f} F1={metrics['f1']:.3f}")
            if metrics["missed"]:
                print(f"  Missed HPO: {metrics['missed']}")
        else:
            # No gold standard — just report what was found
            pathology = note_data.get("pathology", "Unknown")
            print(f"  Pathology: {pathology}")
            all_metrics.append({
                "note_id": note_id,
                "pathology": pathology,
                "processing_time": elapsed,
                "language": lang,
                "tp": 0, "fp": 0, "fn": 0,
                "precision": 0, "recall": 0, "f1": 0,
            })

    return all_metrics


def main():
    mode = "both"
    if "--fr" in sys.argv:
        mode = "fr"
    elif "--en" in sys.argv:
        mode = "en"

    output_dir = os.path.join(PROJECT_ROOT, "output")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print(" CLINICAL PRE-ANALYSIS PIPELINE - BILINGUAL EVALUATION")
    print(f" Mode: {mode.upper()}")
    print(" Modules: PHI -> NER -> NegEx/Temporal/Numeric -> HPO/UMLS/ORDO")
    print("=" * 60)

    start_init = time.time()
    pipeline_obj = FullPipeline()
    init_time = round(time.time() - start_init, 1)
    print(f"\nInitialization time: {init_time}s\n")

    all_metrics = []

    # ── English notes ────────────────────────────────────────────────────
    if mode in ("en", "both"):
        print("\n" + "=" * 60)
        print(" ENGLISH NOTES (i2b2-style)")
        print("=" * 60)
        en_notes = {nid: CLINICAL_NOTES_EN[nid] for nid in get_all_note_ids()
                    if nid in CLINICAL_NOTES_EN}
        en_metrics = run_notes(pipeline_obj, en_notes, "en", output_dir, GOLD_STANDARD)
        all_metrics.extend(en_metrics)

    # ── French notes ─────────────────────────────────────────────────────
    if mode in ("fr", "both"):
        print("\n" + "=" * 60)
        print(" FRENCH NOTES (CHU Oran)")
        print("=" * 60)
        fr_metrics = run_notes(pipeline_obj, CLINICAL_NOTES_FR, "fr", output_dir, GOLD_STANDARD_FR)
        all_metrics.extend(fr_metrics)

    # ── Aggregate ────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(" AGGREGATE RESULTS")
    print(f"{'='*60}")

    # Filter metrics with actual gold standard
    evaluated = [m for m in all_metrics if m.get("tp", 0) + m.get("fn", 0) > 0]
    if evaluated:
        agg = compute_aggregate_metrics(evaluated)
        print(f"\n  Evaluated notes:    {len(evaluated)}")
        print(f"  Total TP:           {agg['total_tp']}")
        print(f"  Total FP:           {agg['total_fp']}")
        print(f"  Total FN:           {agg['total_fn']}")
        print(f"\n  Micro Precision:    {agg['micro_precision']:.4f}")
        print(f"  Micro Recall:       {agg['micro_recall']:.4f}")
        print(f"  Micro F1:           {agg['micro_f1']:.4f}")
        print(f"\n  Macro Precision:    {agg['macro_precision']:.4f}")
        print(f"  Macro Recall:       {agg['macro_recall']:.4f}")
        print(f"  Macro F1:           {agg['macro_f1']:.4f}")
    else:
        agg = {}

    # French-only summary
    fr_notes_processed = [m for m in all_metrics if m.get("language") == "fr"]
    if fr_notes_processed:
        print(f"\n  French notes processed: {len(fr_notes_processed)}")
        for m in fr_notes_processed:
            print(f"    {m['note_id']}: {m.get('pathology', '?')} "
                  f"({m['processing_time']}s)")

    # Save report
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "pipeline_version": "v3 (bilingual FR+EN)",
        "mode": mode,
        "init_time_seconds": init_time,
        "per_note_metrics": all_metrics,
        "aggregate": agg,
    }
    report_path = os.path.join(output_dir, "evaluation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n  Report saved: {report_path}")
    print(f"  All outputs saved to: {output_dir}/")
    print("\n Done!\n")


if __name__ == "__main__":
    main()
