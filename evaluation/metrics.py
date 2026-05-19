"""
Evaluation Metrics — Precision, Recall, F1-Score computation.
Compares pipeline output against gold standard annotations.

Metrics follow standard NER/NEN evaluation methodology:
  - Precision = TP / (TP + FP)
  - Recall    = TP / (TP + FN)
  - F1        = 2 * P * R / (P + R)
"""


def compute_metrics(predicted_hpo_ids: set, gold_hpo_ids: set) -> dict:
    """
    Compute Precision, Recall, F1 for a single note.

    Args:
        predicted_hpo_ids: set of HPO IDs predicted by pipeline
        gold_hpo_ids:      set of HPO IDs from gold standard

    Returns:
        {"tp": int, "fp": int, "fn": int,
         "precision": float, "recall": float, "f1": float}
    """
    tp = len(predicted_hpo_ids & gold_hpo_ids)
    fp = len(predicted_hpo_ids - gold_hpo_ids)
    fn = len(gold_hpo_ids - predicted_hpo_ids)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)
          if (precision + recall) > 0 else 0.0)

    return {
        "tp": tp, "fp": fp, "fn": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def compute_aggregate_metrics(all_results: list[dict]) -> dict:
    """
    Compute micro-averaged metrics across all notes.

    Args:
        all_results: list of per-note metric dicts from compute_metrics()

    Returns:
        {"micro_precision": float, "micro_recall": float, "micro_f1": float,
         "macro_precision": float, "macro_recall": float, "macro_f1": float,
         "total_tp": int, "total_fp": int, "total_fn": int}
    """
    total_tp = sum(r["tp"] for r in all_results)
    total_fp = sum(r["fp"] for r in all_results)
    total_fn = sum(r["fn"] for r in all_results)

    # Micro-averaged
    micro_p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    micro_r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    micro_f1 = (2 * micro_p * micro_r / (micro_p + micro_r)
                if (micro_p + micro_r) > 0 else 0.0)

    # Macro-averaged
    n = len(all_results) if all_results else 1
    macro_p = sum(r["precision"] for r in all_results) / n
    macro_r = sum(r["recall"] for r in all_results) / n
    macro_f1 = sum(r["f1"] for r in all_results) / n

    return {
        "total_tp": total_tp, "total_fp": total_fp, "total_fn": total_fn,
        "micro_precision": round(micro_p, 4),
        "micro_recall": round(micro_r, 4),
        "micro_f1": round(micro_f1, 4),
        "macro_precision": round(macro_p, 4),
        "macro_recall": round(macro_r, 4),
        "macro_f1": round(macro_f1, 4),
    }


def evaluate_note(step2_result: dict, gold: dict) -> dict:
    """
    Evaluate a single note's pipeline output against gold standard.

    Args:
        step2_result: normalized output from Module 4 pipeline
        gold:         gold standard dict with "expected_hpo" key

    Returns:
        metrics dict with per-note P, R, F1

    Note:
        - Only 'problem' entities are counted (HPO = phenotypes, not treatments/tests)
        - NegEx-negated entities are excluded from positive predictions
        - Numeric phenotypes are included as additional positive predictions
    """
    # Extract predicted HPO IDs — ONLY from 'problem' category
    # and ONLY non-negated entities (NegEx-filtered)
    predicted = set()
    for category in ["problem"]:
        if category not in step2_result:
            continue
        for entity in step2_result[category]:
            if entity.get("matched") and entity.get("hpo_id"):
                # Exclude negated entities (NegEx says this is absent)
                if entity.get("negated", False):
                    continue
                predicted.add(entity["hpo_id"])

    # Include numeric phenotypes (lab values → HPO, always affirmed)
    for np_item in step2_result.get("numeric_phenotypes", []):
        if np_item.get("hpo_id"):
            predicted.add(np_item["hpo_id"])

    # Gold standard HPO IDs
    gold_ids = set(gold.get("expected_hpo", {}).keys())

    metrics = compute_metrics(predicted, gold_ids)
    metrics["predicted_ids"] = sorted(predicted)
    metrics["gold_ids"] = sorted(gold_ids)
    metrics["correct"] = sorted(predicted & gold_ids)
    metrics["missed"] = sorted(gold_ids - predicted)
    metrics["extra"] = sorted(predicted - gold_ids)

    return metrics
