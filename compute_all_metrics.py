"""Compute P/R/F1 for all 30 CHU Oran reports using ORDO profiles as gold standard."""
import os, sys, json
sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from module4_normalization.ordo_matcher import RARE_DISEASE_PROFILES

# Map pathology names to ORPHA IDs
PATHOLOGY_TO_ORPHA = {
    "Mucoviscidose": "ORPHA:586",
    "Wiskott-Aldrich": "ORPHA:906",
    "Agammaglobulinémie (Bruton)": "ORPHA:47",
    "SCID": "ORPHA:183660",
    "SCID-like": "ORPHA:183660",
    "Déficit HLA-DR": "ORPHA:572",
    "Ataxie-Télangiectasie": "ORPHA:100",
}

report_path = os.path.join(PROJECT_ROOT, "output", "all_reports", "full_corpus_report.json")
with open(report_path, encoding="utf-8") as f:
    data = json.load(f)

results = []
for r in data["per_report"]:
    note_id = r["note_id"]
    pathology = r["pathology"]
    orpha = PATHOLOGY_TO_ORPHA.get(pathology)
    
    # Load full output to get HPO IDs
    full_path = os.path.join(PROJECT_ROOT, "output", "all_reports", f"{note_id}_full_output.json")
    if not os.path.exists(full_path):
        continue
    with open(full_path, encoding="utf-8") as f2:
        full = json.load(f2)
    
    # Collect predicted HPO (non-negated problem entities + numerics)
    predicted = set()
    step2 = full.get("step2", full.get("module4", {}))
    for cat in ["problem"]:
        for e in step2.get(cat, []):
            if e.get("matched") and e.get("hpo_id") and not e.get("negated", False):
                predicted.add(e["hpo_id"])
    for n in step2.get("numeric_phenotypes", []):
        if n.get("hpo_id"):
            predicted.add(n["hpo_id"])
    
    # Gold standard from ORDO profile
    if orpha and orpha in RARE_DISEASE_PROFILES:
        gold = RARE_DISEASE_PROFILES[orpha]["hpo"]
        tp = len(predicted & gold)
        fp = len(predicted - gold)
        fn = len(gold - predicted)
        p = tp / (tp + fp) if (tp + fp) > 0 else 0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * p * rec / (p + rec) if (p + rec) > 0 else 0
        evaluable = True
    else:
        tp = fp = fn = 0
        p = rec = f1 = 0
        gold = set()
        evaluable = False
    
    results.append({
        "note_id": note_id,
        "patient": r["patient"][:30],
        "pathology": pathology[:25],
        "entities": r["total_entities"],
        "hpo_matched": r["matched_hpo"],
        "predicted": len(predicted),
        "gold": len(gold),
        "tp": tp, "fp": fp, "fn": fn,
        "precision": round(p, 3),
        "recall": round(rec, 3),
        "f1": round(f1, 3),
        "evaluable": evaluable,
        "ordo_correct": r.get("ordo_correct", False),
    })

# Print table
print(f"{'Note':<8} {'Patient':<25} {'Pathologie':<22} {'Ent':>4} {'HPO':>4} {'TP':>3} {'FP':>3} {'FN':>3} {'Prec':>6} {'Rec':>6} {'F1':>6} {'ORDO':>5}")
print("-" * 120)

eval_results = []
for r in results:
    if r["evaluable"]:
        ordo = "OK" if r["ordo_correct"] else "NO"
        print(f"{r['note_id']:<8} {r['patient']:<25} {r['pathology']:<22} {r['entities']:>4} {r['hpo_matched']:>4} {r['tp']:>3} {r['fp']:>3} {r['fn']:>3} {r['precision']:>6.3f} {r['recall']:>6.3f} {r['f1']:>6.3f} {ordo:>5}")
        eval_results.append(r)
    else:
        print(f"{r['note_id']:<8} {r['patient']:<25} {r['pathology']:<22} {r['entities']:>4} {r['hpo_matched']:>4}   -   -   -      -      -      -     -")

# Aggregates
if eval_results:
    total_tp = sum(r["tp"] for r in eval_results)
    total_fp = sum(r["fp"] for r in eval_results)
    total_fn = sum(r["fn"] for r in eval_results)
    micro_p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    micro_r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    micro_f1 = 2 * micro_p * micro_r / (micro_p + micro_r) if (micro_p + micro_r) > 0 else 0
    macro_p = sum(r["precision"] for r in eval_results) / len(eval_results)
    macro_r = sum(r["recall"] for r in eval_results) / len(eval_results)
    macro_f1 = sum(r["f1"] for r in eval_results) / len(eval_results)
    ordo_ok = sum(1 for r in eval_results if r["ordo_correct"])
    
    print(f"\n{'='*120}")
    print(f"AGGREGATE ({len(eval_results)} evaluable reports)")
    print(f"{'='*120}")
    print(f"  Micro  Precision: {micro_p:.4f}   Recall: {micro_r:.4f}   F1: {micro_f1:.4f}")
    print(f"  Macro  Precision: {macro_p:.4f}   Recall: {macro_r:.4f}   F1: {macro_f1:.4f}")
    print(f"  Total  TP={total_tp}  FP={total_fp}  FN={total_fn}")
    print(f"  ORDO Top-1 Accuracy: {ordo_ok}/{len(eval_results)} ({ordo_ok/len(eval_results)*100:.1f}%)")
