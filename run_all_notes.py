"""
Run All Notes — Execute the full 4-module BILINGUAL pipeline
on all CHU Oran clinical reports and evaluate results.

Usage:
    python run_all_notes.py           # Run all 30 CHU reports
    python run_all_notes.py --limit 5 # Run first 5 reports only
"""

import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

import sys
import json
import time

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from clinical_notes.chu_reports import load_chu_reports
from pipeline import FullPipeline
from evaluation.metrics import evaluate_note, compute_aggregate_metrics


def run_chu_reports(pipeline_obj, reports, output_dir):
    """Run pipeline on all CHU reports."""
    all_metrics = []

    for i, report in enumerate(reports, start=1):
        note_id = report["note_id"]
        filename = report["filename"]
        text = report["text"]

        print(f"\n{'='*60}")
        print(f"  [{i}/{len(reports)}] {note_id} — {filename[:50]}")
        print(f"  Text length: {len(text)} chars")
        print(f"{'='*60}")

        start = time.time()
        try:
            result = pipeline_obj.process_and_save(
                clinical_text=text,
                note_id=note_id,
                output_dir=output_dir,
            )
        except Exception as e:
            print(f"  [ERROR] {e}")
            all_metrics.append({
                "note_id": note_id,
                "filename": filename,
                "error": str(e),
            })
            continue

        elapsed = round(time.time() - start, 2)
        print(f"  Processing time: {elapsed}s")

        # ── Module 2: Entities ────────────────────────────────────────
        m2 = result.get("module2", {}).get("entities", {})
        problems = m2.get("problem", [])
        treatments = m2.get("treatment", [])
        tests = m2.get("test", [])

        print(f"  Entities: {len(problems)} problems, "
              f"{len(treatments)} treatments, {len(tests)} tests")

        # ── Module 3: Validation ──────────────────────────────────────
        m3 = result.get("module3", {})
        warnings = m3.get("warnings", {})

        negated_count = sum(
            1 for cat in ["problem", "treatment", "test"]
            for e in m2.get(cat, [])
            if e.get("negated", False)
        )
        if negated_count:
            print(f"  Negated entities: {negated_count}")

        temporal = warnings.get("temporal", [])
        if temporal:
            for w in temporal:
                print(f"  TEMPORAL: {w.get('message', '')}")

        inconsistencies = warnings.get("inconsistencies", [])
        if inconsistencies:
            for w in inconsistencies:
                print(f"  INCONSISTENCY: {w.get('message', '')}")

        numeric = m3.get("numeric_phenotypes", [])
        if numeric:
            print(f"  Numeric phenotypes: {len(numeric)}")
            for np_item in numeric:
                print(f"      {np_item.get('hpo_name', '?')} ({np_item.get('source', '?')})")

        # ── Module 4: Normalization ───────────────────────────────────
        m4 = result.get("module4", {})
        stats = m4.get("stats", {})
        print(f"  HPO: {stats.get('matched', 0)}/{stats.get('total', 0)} matched")

        # ORDO candidates
        ordo = m4.get("ordo_candidates", [])
        if ordo:
            top = ordo[0]
            name_display = top.get("name_fr") or top.get("name", "?")
            print(f"  Top ORDO: {name_display} (score={top.get('score', 0):.3f})")

        # Collect all HPO IDs extracted
        extracted_hpo = set()
        for cat in ["problem", "treatment", "test"]:
            for e in m4.get(cat, []):
                hpo_id = e.get("hpo_id")
                if hpo_id:
                    extracted_hpo.add(hpo_id)

        all_metrics.append({
            "note_id": note_id,
            "filename": filename,
            "processing_time": elapsed,
            "language": result.get("module1", {}).get("language", "fr"),
            "total_entities": stats.get("total", 0),
            "matched_hpo": stats.get("matched", 0),
            "unmatched": stats.get("unmatched", 0),
            "negated": negated_count,
            "numeric_phenotypes": len(numeric),
            "ordo_top": ordo[0].get("name", "") if ordo else "",
            "ordo_score": ordo[0].get("score", 0) if ordo else 0,
            "extracted_hpo_ids": sorted(extracted_hpo),
        })

    return all_metrics


def main():
    # Parse limit
    limit = None
    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        if idx + 1 < len(sys.argv):
            limit = int(sys.argv[idx + 1])

    output_dir = os.path.join(PROJECT_ROOT, "output")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print(" CLINICAL PRE-ANALYSIS PIPELINE — CHU ORAN EVALUATION")
    print(" Pipeline: PHI -> NER (DeBERTa-v3) -> Validation -> HPO/ORDO")
    print("=" * 60)

    # Load reports
    reports = load_chu_reports()
    if limit:
        reports = reports[:limit]
        print(f"\n  Limited to first {limit} reports")

    print(f"\n  Total reports to process: {len(reports)}")

    # Initialize pipeline
    start_init = time.time()
    pipeline_obj = FullPipeline()
    init_time = round(time.time() - start_init, 1)
    print(f"  Initialization time: {init_time}s\n")

    # Process all reports
    start_total = time.time()
    all_metrics = run_chu_reports(pipeline_obj, reports, output_dir)
    total_time = round(time.time() - start_total, 1)

    # ── Summary ──────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(" SUMMARY — CHU ORAN CLINICAL REPORTS")
    print(f"{'='*60}")

    successful = [m for m in all_metrics if "error" not in m]
    failed = [m for m in all_metrics if "error" in m]

    print(f"\n  Reports processed:  {len(successful)}/{len(reports)}")
    if failed:
        print(f"  Failed:             {len(failed)}")
        for m in failed:
            print(f"    {m['note_id']}: {m['error'][:60]}")

    if successful:
        total_ents = sum(m.get("total_entities", 0) for m in successful)
        total_hpo = sum(m.get("matched_hpo", 0) for m in successful)
        total_neg = sum(m.get("negated", 0) for m in successful)
        total_numeric = sum(m.get("numeric_phenotypes", 0) for m in successful)
        avg_time = sum(m.get("processing_time", 0) for m in successful) / len(successful)

        ordo_count = sum(1 for m in successful if m.get("ordo_score", 0) > 0)

        print(f"\n  Total entities extracted:    {total_ents}")
        print(f"  Total HPO codes assigned:   {total_hpo}")
        print(f"  Total negated entities:     {total_neg}")
        print(f"  Total numeric phenotypes:   {total_numeric}")
        print(f"  Reports with ORDO match:    {ordo_count}/{len(successful)}")
        print(f"\n  Avg processing time:        {avg_time:.2f}s per report")
        print(f"  Total processing time:      {total_time}s")

        # Per-report table
        print(f"\n  {'Note ID':<12} {'Entities':>8} {'HPO':>5} {'Neg':>4} "
              f"{'ORDO Top Match':<30} {'Score':>6} {'Time':>5}")
        print(f"  {'-'*12} {'-'*8} {'-'*5} {'-'*4} {'-'*30} {'-'*6} {'-'*5}")
        for m in successful:
            ordo_name = (m.get("ordo_top", "") or "—")[:30]
            ordo_score = m.get("ordo_score", 0)
            print(f"  {m['note_id']:<12} {m.get('total_entities', 0):>8} "
                  f"{m.get('matched_hpo', 0):>5} {m.get('negated', 0):>4} "
                  f"{ordo_name:<30} {ordo_score:>5.1%} "
                  f"{m.get('processing_time', 0):>4.1f}s")

    # Save report
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "pipeline_version": "v4.0 (DeBERTa-v3 bilingual)",
        "dataset": "CHU Oran — Real clinical reports",
        "total_reports": len(reports),
        "successful": len(successful),
        "init_time_seconds": init_time,
        "total_time_seconds": total_time,
        "per_report_metrics": all_metrics,
    }
    report_path = os.path.join(output_dir, "evaluation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n  Report saved: {report_path}")
    print(f"  All outputs saved to: {output_dir}/")
    print("\n Done!\n")


if __name__ == "__main__":
    main()
