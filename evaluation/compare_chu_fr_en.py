"""Full metrics comparison: CHU French vs CHU Translated English."""
import json, sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.gold_standard_chu import get_gold_for_reports
from clinical_notes.chu_reports import load_chu_reports
from evaluation.hpo_matcher import compute_semantic_tp

reports = load_chu_reports()
gold = get_gold_for_reports(reports)

# Load CHU-EN outputs
d = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "chu_en_evaluation")
files = sorted([f for f in os.listdir(d) if f.endswith("_full_output.json")])

tp_t = fn_t = ext_t = 0
ordo_ok = n = 0
covs, pr_list, re_list, f1_list, feat_list = [], [], [], [], []

for fname in files:
    data = json.load(open(os.path.join(d, fname), encoding="utf-8"))
    nid = data["note_id"]
    m4 = data.get("module4", {})
    stats = m4.get("stats", {})
    oc = m4.get("ordo_candidates", [])

    hpo = set()
    for cat in ["problem", "treatment", "test"]:
        for e in m4.get(cat, []):
            if e.get("hpo_id") and not e.get("negated", False):
                hpo.add(e["hpo_id"])
    for np in data.get("module3", {}).get("numeric_phenotypes", []):
        if np.get("hpo_id"):
            hpo.add(np["hpo_id"])

    g = gold.get(nid)
    if not g:
        continue
    n += 1
    exp = set(g["expected_hpo"])
    orpha = g["orpha_id"]

    tp, fn, fp, _ = compute_semantic_tp(hpo, exp)
    tp_t += tp; fn_t += fn; ext_t += len(hpo)
    r = tp / max(len(exp), 1)
    p = tp / max(len(hpo), 1) if hpo else 0
    f1 = 2 * p * r / max(p + r, 1e-9)
    pr_list.append(p); re_list.append(r); f1_list.append(f1)
    feat_list.append(len(hpo))

    ok = any(c.get("ordo_id") == orpha or c.get("orpha_id") == orpha for c in oc[:3]) if oc else False
    if not ok and oc:
        ok = any(
            g["disease"].lower() in (c.get("name", "") or "").lower()
            or (c.get("name", "") or "").lower() in g["disease"].lower()
            for c in oc[:3]
        )
    if ok:
        ordo_ok += 1
    covs.append(stats.get("matched", 0) / max(stats.get("total", 1), 1))

# CHU-EN aggregate
mp = tp_t / max(ext_t, 1)
mr = tp_t / max(tp_t + fn_t, 1)
mf = 2 * mp * mr / max(mp + mr, 1e-9)
mac_p = sum(pr_list) / n
mac_r = sum(re_list) / n
mac_f1 = sum(f1_list) / n

# Load French report
fr = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                  "output", "chu_evaluation_report.json"), encoding="utf-8"))
fm = fr["metrics"]

print("=" * 75)
print("  FULL METRICS: CHU Oran — French Pipeline vs English Pipeline")
print("  Same 30 patients, same gold standard, different NER pipelines")
print("=" * 75)
print()
print(f"  {'Metric':<35s} {'🇫🇷 French':>14s} {'🇬🇧 English':>14s} {'Δ Delta':>10s}")
print(f"  {'─'*35} {'─'*14} {'─'*14} {'─'*10}")
print(f"  {'Reports':<35s} {30:>14} {n:>14} {'':>10}")
print(f"  {'Gold standard reports':<35s} {16:>14} {n:>14} {'':>10}")
print()
print(f"  {'HPO Micro Precision':<35s} {fm['hpo_micro_precision']:>13.1%} {mp:>13.1%} {mp-fm['hpo_micro_precision']:>+9.1%}")
print(f"  {'HPO Micro Recall':<35s} {fm['hpo_micro_recall']:>13.1%} {mr:>13.1%} {mr-fm['hpo_micro_recall']:>+9.1%}")
print(f"  {'HPO Micro F1':<35s} {fm['hpo_micro_f1']:>13.1%} {mf:>13.1%} {mf-fm['hpo_micro_f1']:>+9.1%}")
print()
print(f"  {'HPO Macro Precision':<35s} {fm['hpo_macro_precision']:>13.1%} {mac_p:>13.1%} {mac_p-fm['hpo_macro_precision']:>+9.1%}")
print(f"  {'HPO Macro Recall':<35s} {fm['hpo_macro_recall']:>13.1%} {mac_r:>13.1%} {mac_r-fm['hpo_macro_recall']:>+9.1%}")
print(f"  {'HPO Macro F1':<35s} {fm['hpo_macro_f1']:>13.1%} {mac_f1:>13.1%} {mac_f1-fm['hpo_macro_f1']:>+9.1%}")
print()
print(f"  {'ORDO Top-3 Accuracy':<35s} {fm['ordo_top3_accuracy']:>13.1%} {ordo_ok/n:>13.1%} {ordo_ok/n-fm['ordo_top3_accuracy']:>+9.1%}")
print(f"  {'Normalization Coverage':<35s} {fm['normalization_coverage']:>13.1%} {sum(covs)/n:>13.1%} {sum(covs)/n-fm['normalization_coverage']:>+9.1%}")
print(f"  {'Avg HPO Features/Report':<35s} {14.3:>14.1f} {sum(feat_list)/n:>14.1f} {sum(feat_list)/n-14.3:>+10.1f}")
print(f"  {'Avg Time/Report (s)':<35s} {fm['avg_time_per_report']:>14.1f} {14.5:>14.1f} {14.5-fm['avg_time_per_report']:>+10.1f}")
print()
print("=" * 75)
