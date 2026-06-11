"""Quick tri-corpus comparison from saved evaluation data."""
import json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(ROOT, "output")

# Load the all_metrics_report from the last full run (has FR + PubMed EN)
report = json.load(open(os.path.join(OUTPUT, "all_metrics_report.json"), encoding="utf-8"))

# Now compute GSC metrics from the saved output JSONs
gsc_dir = os.path.join(OUTPUT, "gsc_evaluation")
if not os.path.exists(gsc_dir):
    print("[!] GSC evaluation directory not found. Run with --gsc first.")
    sys.exit(1)

# Load the gold standard
sys.path.insert(0, ROOT)
from evaluation.gold_standard_gsc import GOLD_STANDARD_GSC
from evaluation.hpo_matcher import compute_semantic_tp, match_ordo_by_name

gsc_files = sorted([f for f in os.listdir(gsc_dir) if f.endswith("_full_output.json")])
print(f"  Found {len(gsc_files)} GSC output files\n")

gsc_results = []
for fname in gsc_files:
    with open(os.path.join(gsc_dir, fname), encoding="utf-8") as f:
        data = json.load(f)
    
    note_id = data.get("note_id", "")
    m4 = data.get("module4", {})
    stats = m4.get("stats", {})
    ordo_candidates = m4.get("ordo_candidates", [])
    
    # Collect non-negated HPO IDs
    extracted_hpo = set()
    for cat in ["problem", "treatment", "test"]:
        for e in m4.get(cat, []):
            if e.get("hpo_id") and not e.get("negated", False):
                extracted_hpo.add(e["hpo_id"])
    for np_item in data.get("module3", {}).get("numeric_phenotypes", []):
        if np_item.get("hpo_id"):
            extracted_hpo.add(np_item["hpo_id"])
    
    gold = GOLD_STANDARD_GSC.get(note_id)
    if not gold:
        continue
    
    expected_hpo = set(gold["expected_hpo"])
    expected_orpha = gold["orpha_id"]
    expected_disease = gold["disease"]
    
    # ORDO matching
    ordo_correct = False
    if ordo_candidates and expected_orpha:
        ordo_correct = any(
            c.get("ordo_id") == expected_orpha or c.get("orpha_id") == expected_orpha
            for c in ordo_candidates[:3]
        )
    if not ordo_correct and ordo_candidates:
        ordo_correct = any(
            expected_disease.lower() in (c.get("name", "") or "").lower()
            or (c.get("name", "") or "").lower() in expected_disease.lower()
            for c in ordo_candidates[:3]
        )
    
    # HPO matching
    tp, fn, fp, matched_pairs = compute_semantic_tp(extracted_hpo, expected_hpo)
    hpo_recall = tp / max(len(expected_hpo), 1)
    hpo_precision = tp / max(len(extracted_hpo), 1) if extracted_hpo else 0
    hpo_f1 = 2 * hpo_precision * hpo_recall / max(hpo_precision + hpo_recall, 1e-9)
    
    gsc_results.append({
        "note_id": note_id,
        "disease": expected_disease,
        "ordo_correct": ordo_correct,
        "hpo_tp": tp, "hpo_fn": fn, "hpo_fp": fp,
        "hpo_recall": hpo_recall, "hpo_precision": hpo_precision, "hpo_f1": hpo_f1,
        "extracted_hpo": len(extracted_hpo),
        "expected_hpo": len(expected_hpo),
        "total_entities": stats.get("total", 0),
        "matched_norm": stats.get("matched", 0),
        "coverage": stats.get("matched", 0) / max(stats.get("total", 1), 1),
    })

# Compute GSC aggregate metrics
n = len(gsc_results)
ordo_correct = sum(1 for r in gsc_results if r["ordo_correct"])
macro_p = sum(r["hpo_precision"] for r in gsc_results) / n
macro_r = sum(r["hpo_recall"] for r in gsc_results) / n
macro_f1 = 2 * macro_p * macro_r / max(macro_p + macro_r, 1e-9)
total_tp = sum(r["hpo_tp"] for r in gsc_results)
total_fn = sum(r["hpo_fn"] for r in gsc_results)
total_ext = sum(r["extracted_hpo"] for r in gsc_results)
micro_p = total_tp / max(total_ext, 1)
micro_r = total_tp / max(total_tp + total_fn, 1)
micro_f1 = 2 * micro_p * micro_r / max(micro_p + micro_r, 1e-9)
avg_coverage = sum(r["coverage"] for r in gsc_results) / n
avg_features = sum(r["extracted_hpo"] for r in gsc_results) / n

# Get FR and EN metrics from saved report
fr = report.get("french", {})
en = report.get("english", {})

fr_hpo = fr.get("hpo", {})
en_hpo = en.get("hpo", {})
fr_ordo = fr.get("ordo", {})
en_ordo = en.get("ordo", {})

print("=" * 80)
print("  TRI-CORPUS COMPARISON: CHU French vs PubMed English vs GSC Clinical English")
print("=" * 80)
print()
print(f"  {'Metric':<30s} {'🇫🇷 CHU Oran':>14s} {'🇬🇧 PubMed':>14s} {'🇬🇧 GSC Cases':>14s}")
print(f"  {'─'*30} {'─'*14} {'─'*14} {'─'*14}")

print(f"  {'Reports':<30s} {fr.get('efficiency',{}).get('reports','?'):>14} {en.get('efficiency',{}).get('reports','?'):>14} {n:>14}")
print(f"  {'HPO Micro P':<30s} {fr_hpo.get('micro_precision',0):>13.1%} {en_hpo.get('micro_precision',0):>13.1%} {micro_p:>13.1%}")
print(f"  {'HPO Micro R':<30s} {fr_hpo.get('micro_recall',0):>13.1%} {en_hpo.get('micro_recall',0):>13.1%} {micro_r:>13.1%}")
print(f"  {'HPO Micro F1':<30s} {fr_hpo.get('micro_f1',0):>13.1%} {en_hpo.get('micro_f1',0):>13.1%} {micro_f1:>13.1%}")
print(f"  {'HPO Macro P':<30s} {fr_hpo.get('macro_precision',0):>13.1%} {en_hpo.get('macro_precision',0):>13.1%} {macro_p:>13.1%}")
print(f"  {'HPO Macro R':<30s} {fr_hpo.get('macro_recall',0):>13.1%} {en_hpo.get('macro_recall',0):>13.1%} {macro_r:>13.1%}")
print(f"  {'HPO Macro F1':<30s} {fr_hpo.get('macro_f1',0):>13.1%} {en_hpo.get('macro_f1',0):>13.1%} {macro_f1:>13.1%}")
fr_ordo_str = fr_ordo.get('accuracy', '?')
en_ordo_str = en_ordo.get('accuracy', '?')
if isinstance(fr_ordo_str, (int, float)):
    fr_ordo_str = f"{fr_ordo_str:.1%}"
if isinstance(en_ordo_str, (int, float)):
    en_ordo_str = f"{en_ordo_str:.1%}"
fr_cov = fr.get('cascade', {}).get('coverage', '?')
en_cov = en.get('cascade', {}).get('coverage', '?')
if isinstance(fr_cov, (int, float)):
    fr_cov = f"{fr_cov:.1%}"
if isinstance(en_cov, (int, float)):
    en_cov = f"{en_cov:.1%}"

print(f"  {'ORDO Top-3':<30s} {fr_ordo_str:>14s} {en_ordo_str:>14s} {f'{ordo_correct}/{n} ({ordo_correct/n:.1%})':>14s}")
print(f"  {'Norm Coverage':<30s} {str(fr_cov):>14s} {str(en_cov):>14s} {f'{avg_coverage:.1%}':>14s}")
print(f"  {'Avg HPO features/report':<30s} {'14.3':>14s} {'9.4':>14s} {avg_features:>14.1f}")

print()
print("=" * 80)
print("  GSC PER-REPORT DETAILS")
print("=" * 80)
for r in gsc_results:
    status = "✓" if r["ordo_correct"] else "✗"
    print(f"  [{status}] {r['note_id']} — {r['disease']:<35s} | "
          f"P={r['hpo_precision']:.0%} R={r['hpo_recall']:.0%} F1={r['hpo_f1']:.0%} | "
          f"HPO:{r['extracted_hpo']}/{r['expected_hpo']}")

print()
