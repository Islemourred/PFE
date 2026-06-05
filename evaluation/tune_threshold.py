"""
SapBERT Threshold Auto-Tuner
Finds the optimal similarity threshold by grid search on gold standard data.

Instead of hardcoding threshold=0.70, this script evaluates all thresholds
from 0.50 to 0.95 and selects the one that maximizes F1-score.

Usage:
    python evaluation/tune_threshold.py
    
Output:
    Prints a table of threshold → F1 scores and the optimal value.
"""

import os
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

sys.stdout.reconfigure(encoding="utf-8")


def tune_threshold():
    """Grid search over SapBERT thresholds to find optimal F1."""
    from evaluation.metrics import evaluate_note, aggregate_metrics
    from evaluation.gold_standard import GOLD_STANDARD
    from evaluation.gold_standard_fr import GOLD_STANDARD_FR
    from clinical_notes.mock_data import CLINICAL_NOTES
    from clinical_notes.mock_data_fr import CLINICAL_NOTES_FR

    # Delayed import to avoid loading models at import time
    from pipeline import FullPipeline

    thresholds = [round(0.50 + i * 0.05, 2) for i in range(10)]
    # 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95

    results = []

    for threshold in thresholds:
        print(f"\n{'='*60}")
        print(f"  Testing threshold: {threshold}")
        print(f"{'='*60}")

        start = time.time()

        # Create pipeline with this threshold
        pipe = FullPipeline(similarity_threshold=threshold)

        all_metrics = []

        # English notes
        for note_id, note_data in CLINICAL_NOTES.items():
            gold = GOLD_STANDARD.get(note_id, {})
            if not gold or not gold.get("expected_hpo"):
                continue
            result = pipe.process(note_data["text"], note_id=note_id, lang="en")
            m = evaluate_note(result["module4"], gold)
            all_metrics.append(m)

        # French notes
        for note_id, note_data in CLINICAL_NOTES_FR.items():
            gold = GOLD_STANDARD_FR.get(note_id, {})
            if not gold or not gold.get("expected_hpo"):
                continue
            result = pipe.process(note_data["text"], note_id=note_id, lang="fr")
            m = evaluate_note(result["module4"], gold)
            all_metrics.append(m)

        agg = aggregate_metrics(all_metrics)
        elapsed = round(time.time() - start, 1)

        results.append({
            "threshold": threshold,
            "micro_p": agg["micro_precision"],
            "micro_r": agg["micro_recall"],
            "micro_f1": agg["micro_f1"],
            "macro_f1": agg["macro_f1"],
            "time": elapsed,
        })

        print(f"  Micro F1: {agg['micro_f1']:.4f} | "
              f"Macro F1: {agg['macro_f1']:.4f} | "
              f"Time: {elapsed}s")

        # Clean up to free GPU memory
        del pipe

    # Summary table
    print(f"\n{'='*70}")
    print(f"  THRESHOLD TUNING RESULTS")
    print(f"{'='*70}")
    print(f"  {'Threshold':<12} {'Micro P':<10} {'Micro R':<10} {'Micro F1':<10} {'Macro F1':<10}")
    print(f"  {'-'*52}")

    best = max(results, key=lambda x: x["micro_f1"])
    for r in results:
        marker = " ← BEST" if r["threshold"] == best["threshold"] else ""
        print(f"  {r['threshold']:<12} {r['micro_p']:<10.4f} {r['micro_r']:<10.4f} "
              f"{r['micro_f1']:<10.4f} {r['macro_f1']:<10.4f}{marker}")

    print(f"\n  Optimal threshold: {best['threshold']}")
    print(f"  Best Micro F1:     {best['micro_f1']:.4f}")
    print(f"  Best Macro F1:     {best['macro_f1']:.4f}")
    print(f"\n  To apply: Update pipeline.py line 38:")
    print(f"    def __init__(self, similarity_threshold: float = {best['threshold']}):")
    print(f"{'='*70}\n")

    return best


if __name__ == "__main__":
    tune_threshold()
