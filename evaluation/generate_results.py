"""
Generate Results Summary — Creates formatted tables for the mémoire.
Reads the evaluation report and generates a summary.

Usage:
    python evaluation/generate_results.py
"""

import os
import sys
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def print_per_note_table(metrics_list: list):
    """Print per-note results table."""
    header = f"{'Note ID':<12} {'Pathology':<35} {'P':>6} {'R':>6} {'F1':>6} {'TP':>4} {'FP':>4} {'FN':>4}"
    print(header)
    print("-" * len(header))
    for m in metrics_list:
        print(f"{m['note_id']:<12} "
              f"{m.get('pathology', '')[:34]:<35} "
              f"{m['precision']:>6.3f} "
              f"{m['recall']:>6.3f} "
              f"{m['f1']:>6.3f} "
              f"{m['tp']:>4} "
              f"{m['fp']:>4} "
              f"{m['fn']:>4}")


def print_match_method_breakdown(output_dir: str):
    """Analyze matching methods across all notes."""
    methods = {"exact_label": 0, "exact_synonym": 0, "sapbert_similarity": 0, "no_match": 0}
    total = 0

    for fname in os.listdir(output_dir):
        if fname.endswith("_full_output.json"):
            path = os.path.join(output_dir, fname)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            step2 = data.get("step2", {})
            for cat in ["problem", "treatment", "test"]:
                for ent in step2.get(cat, []):
                    mt = ent.get("match_type", "no_match")
                    methods[mt] = methods.get(mt, 0) + 1
                    total += 1

    print(f"\n{'Method':<25} {'Count':>6} {'%':>8}")
    print("-" * 42)
    for method, count in sorted(methods.items(), key=lambda x: -x[1]):
        pct = (count / total * 100) if total > 0 else 0
        print(f"{method:<25} {count:>6} {pct:>7.1f}%")
    print(f"{'TOTAL':<25} {total:>6} {'100.0':>7}%")


def main():
    output_dir = os.path.join(PROJECT_ROOT, "output")
    report_path = os.path.join(output_dir, "evaluation_report.json")

    if not os.path.exists(report_path):
        print("ERROR: No evaluation report found. Run 'python run_all_notes.py' first.")
        return

    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    print("=" * 60)
    print(" RESULTS SUMMARY FOR MEMOIRE")
    print("=" * 60)
    print(f"\nGenerated: {report['timestamp']}")
    print(f"Pipeline init time: {report['init_time_seconds']}s")

    # Per-note table
    print(f"\n{'='*60}")
    print(" TABLE 1: Per-Note Evaluation Results")
    print(f"{'='*60}\n")
    print_per_note_table(report["per_note_metrics"])

    # Aggregate
    agg = report["aggregate"]
    print(f"\n{'='*60}")
    print(" TABLE 2: Aggregate Metrics")
    print(f"{'='*60}\n")
    print(f"  Micro-averaged Precision:  {agg['micro_precision']:.4f}")
    print(f"  Micro-averaged Recall:     {agg['micro_recall']:.4f}")
    print(f"  Micro-averaged F1-Score:   {agg['micro_f1']:.4f}")
    print(f"\n  Macro-averaged Precision:  {agg['macro_precision']:.4f}")
    print(f"  Macro-averaged Recall:     {agg['macro_recall']:.4f}")
    print(f"  Macro-averaged F1-Score:   {agg['macro_f1']:.4f}")

    # Match method breakdown
    print(f"\n{'='*60}")
    print(" TABLE 3: Normalization Method Breakdown")
    print(f"{'='*60}")
    print_match_method_breakdown(output_dir)

    print(f"\n{'='*60}")
    print(" Use these tables in Chapter 5 of the memoire.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
