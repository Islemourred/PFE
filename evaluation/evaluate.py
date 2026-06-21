"""
Unified Evaluation Engine — All 8 Thesis Metrics for Both Languages.

Runs the full pipeline on CHU (French) and PubMed (English) datasets,
then computes every metric required by Mezrar's thesis objectives:

  1. HPO Precision / Recall / F1 (Micro + Macro)
  2. Normalization Coverage + Cascade Distribution
  3. ORDO Top-K Accuracy (Disease Classification)
  4. Inconsistency & Negation Detection
  5. Phenopacket Compliance (ISO 4454:2022)
  6. Cross-Lingual Comparison (FR vs EN)
  7. Processing Efficiency
  8. S.C.O.R.E. Framework (Automated Approximation)

Usage:
    python evaluation/evaluate.py               # Full run (both languages)
    python evaluation/evaluate.py --lang fr      # French only
    python evaluation/evaluate.py --lang en      # English only
    python evaluation/evaluate.py --limit 5      # Quick test (5 per language)
    python evaluation/evaluate.py --skip-run      # Metrics only (from saved outputs)
"""

import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

import sys
import json
import time
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

OUTPUT_DIR = Path(PROJECT_ROOT) / "output"


# ═══════════════════════════════════════════════════════════════════════
#  PHASE 1: Run Pipeline on All Reports
# ═══════════════════════════════════════════════════════════════════════

def run_pipeline_on_dataset(dataset: str, limit=None) -> list[dict]:
    """Run the pipeline on a dataset and return per-report results."""
    from evaluation.hpo_matcher import compute_semantic_tp, match_ordo_by_name
    from pipeline import FullPipeline

    if dataset == "chu":
        from clinical_notes.chu_gold_v2.loader import load_chu_gold_v2
        reports, gold_map = load_chu_gold_v2()
        lang_label = "French (CHU)"
        out_subdir = "chu_evaluation"
    elif dataset == "gsc":
        from clinical_notes.gsc_downloader import load_gsc_cases
        from evaluation.gold_standard_gsc import GOLD_STANDARD_GSC
        reports = load_gsc_cases()
        gold_map = {}
        for case in reports:
            nid = case.get("note_id", "")
            if nid in GOLD_STANDARD_GSC:
                gs = GOLD_STANDARD_GSC[nid]
                gold_map[nid] = {
                    "disease": gs["disease"],
                    "orpha_id": gs["orpha_id"],
                    "expected_hpo": gs["expected_hpo"],
                }
        lang_label = "English (GSC Clinical Cases)"
        out_subdir = "gsc_evaluation"
    elif dataset == "rarearena":
        from clinical_notes.rarearena_loader import load_rarearena_cases
        from evaluation.gold_standard_ra import GOLD_STANDARD_RA
        reports = load_rarearena_cases()
        gold_map = {}
        for case in reports:
            nid = case.get("note_id", "")
            if nid in GOLD_STANDARD_RA:
                gs = GOLD_STANDARD_RA[nid]
                gold_map[nid] = {
                    "disease": gs["disease"],
                    "orpha_id": gs["orpha_id"],
                    "expected_hpo": gs["expected_hpo"],
                }
        lang_label = "English (RareArena - Lancet 2026)"
        out_subdir = "rarearena_evaluation"
    elif dataset == "chu_en":
        from clinical_notes.chu_gold_v2.loader_en import load_chu_gold_v2_en
        reports, gold_map = load_chu_gold_v2_en()
        lang_label = "English (CHU Translated FR→EN)"
        out_subdir = "chu_en_evaluation"
        force_lang = "en"  # Force English pipeline on translated text
    else:
        from clinical_notes.pubmed_cases import load_pubmed_cases
        from evaluation.gold_standard_en import GOLD_STANDARD_EN
        reports = load_pubmed_cases()
        # Build gold map keyed by note_id
        gold_map = {}
        for case in reports:
            disease = case.get("disease", "")
            if disease in GOLD_STANDARD_EN:
                raw_hpo = GOLD_STANDARD_EN[disease].get("expected_hpo", {})
                # Handle both dict (keys are IDs) and list (IDs directly) formats
                hpo_list = list(raw_hpo.keys()) if isinstance(raw_hpo, dict) else list(raw_hpo)
                gold_map[case["note_id"]] = {
                    "disease": disease,
                    "orpha_id": GOLD_STANDARD_EN[disease].get("orpha_id", ""),
                    "expected_hpo": hpo_list,
                }
        lang_label = "English (PubMed)"
        out_subdir = "pubmed_evaluation"

    # Default: auto-detect language (None), unless overridden by dataset
    try:
        force_lang
    except NameError:
        force_lang = None

    if limit:
        reports = reports[:limit]

    eval_dir = OUTPUT_DIR / out_subdir
    eval_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"  RUNNING PIPELINE — {lang_label}")
    print(f"  Reports: {len(reports)} | Gold standard: {len(gold_map)} matched")
    print(f"{'='*70}")

    start_init = time.time()
    pipeline_obj = FullPipeline()
    print(f"  Init time: {time.time() - start_init:.1f}s\n")

    results = []

    for i, report in enumerate(reports, 1):
        note_id = report.get("note_id", f"REPORT_{i:03d}")
        disease_name = report.get("disease", report.get("filename", ""))
        gold = gold_map.get(note_id)
        text = report.get("text", "")

        print(f"  [{i}/{len(reports)}] {note_id} — {disease_name[:50]}")

        start = time.time()
        try:
            result = pipeline_obj.process_and_save(
                clinical_text=text,
                note_id=note_id,
                output_dir=str(eval_dir),
                lang=force_lang,
            )
        except Exception as e:
            print(f"    [ERROR] {e}")
            continue
        elapsed = round(time.time() - start, 2)

        # Extract pipeline outputs
        m4 = result.get("module4", {})
        stats = m4.get("stats", {})
        ordo_candidates = m4.get("ordo_candidates", [])

        # Collect non-negated HPO IDs
        extracted_hpo = set()
        for cat in ["problem", "treatment", "test"]:
            for e in m4.get(cat, []):
                if e.get("hpo_id") and not e.get("negated", False):
                    extracted_hpo.add(e["hpo_id"])
        for np_item in result.get("module3", {}).get("numeric_phenotypes", []):
            if np_item.get("hpo_id"):
                extracted_hpo.add(np_item["hpo_id"])

        entry = {
            "note_id": note_id,
            "disease": disease_name,
            "time": elapsed,
            "total_entities": stats.get("total", 0),
            "matched_hpo": stats.get("matched", 0),
            "coverage": stats.get("matched", 0) / max(stats.get("total", 1), 1),
            "extracted_hpo": sorted(extracted_hpo),
        }

        if gold:
            expected_orpha = gold.get("orpha_id", "")
            expected_disease = gold.get("disease", disease_name)
            expected_hpo = set(gold.get("expected_hpo", []))

            # ORDO matching — strict ORPHA ID only (no fuzzy name matching)
            ordo_correct = False
            ordo_top1 = False
            ordo_top5 = False
            ordo_top10 = False
            ordo_top_name = ordo_candidates[0].get("name", "") if ordo_candidates else ""
            ordo_top_score = ordo_candidates[0].get("score", 0) if ordo_candidates else 0

            if ordo_candidates and expected_orpha:
                ordo_top1 = ordo_candidates[0].get("ordo_id") == expected_orpha
                ordo_correct = any(
                    c.get("ordo_id") == expected_orpha
                    for c in ordo_candidates[:3]
                )
                ordo_top5 = any(
                    c.get("ordo_id") == expected_orpha
                    for c in ordo_candidates[:5]
                )
                ordo_top10 = any(
                    c.get("ordo_id") == expected_orpha
                    for c in ordo_candidates[:10]
                )

            # Semantic HPO matching
            tp, fn, fp, matched_pairs = compute_semantic_tp(extracted_hpo, expected_hpo)
            hpo_recall = tp / max(len(expected_hpo), 1)
            hpo_precision = tp / max(len(extracted_hpo), 1) if extracted_hpo else 0
            hpo_f1 = 2 * hpo_precision * hpo_recall / max(hpo_precision + hpo_recall, 1e-9)

            entry.update({
                "has_gold": True, "expected_disease": expected_disease,
                "expected_orpha": expected_orpha, "ordo_correct": ordo_correct,
                "ordo_top1": ordo_top1, "ordo_top5": ordo_top5, "ordo_top10": ordo_top10,
                "ordo_top": ordo_top_name, "ordo_score": ordo_top_score,
                "expected_hpo_count": len(expected_hpo),
                "hpo_tp": tp, "hpo_fn": fn, "hpo_fp": fp,
                "hpo_recall": hpo_recall, "hpo_precision": hpo_precision, "hpo_f1": hpo_f1,
                "semantic_matches": [(e, g) for e, g in matched_pairs],
            })
            status = "✓" if ordo_correct else "✗"
            print(f"    ORDO: [{status}] {ordo_top_name[:40]}")
            print(f"    HPO:  P={hpo_precision:.1%} R={hpo_recall:.1%} F1={hpo_f1:.1%}")
        else:
            entry["has_gold"] = False
            print(f"    Entities: {stats.get('total',0)} | HPO: {stats.get('matched',0)} | {elapsed}s")

        results.append(entry)

    return results


def load_saved_outputs(subdir: str) -> list[dict]:
    """Load *_full_output.json files from a subdirectory."""
    d = OUTPUT_DIR / subdir
    outputs = []
    if d.exists():
        for f in sorted(d.glob("*_full_output.json")):
            with open(f, encoding="utf-8") as fh:
                outputs.append(json.load(fh))
    return outputs


# ═══════════════════════════════════════════════════════════════════════
#  PHASE 2: Compute All 8 Metrics
# ═══════════════════════════════════════════════════════════════════════

def compute_hpo_metrics(results: list[dict]) -> dict:
    """Metric 1: HPO P/R/F1."""
    gold = [r for r in results if r.get("has_gold")]
    if not gold:
        return {}
    total_tp = sum(r.get("hpo_tp", 0) for r in gold)
    total_fn = sum(r.get("hpo_fn", 0) for r in gold)
    total_ext = sum(len(r.get("extracted_hpo", [])) for r in gold)
    micro_p = total_tp / max(total_ext, 1)
    micro_r = total_tp / max(total_tp + total_fn, 1)
    micro_f1 = 2 * micro_p * micro_r / max(micro_p + micro_r, 1e-9)
    macro_p = sum(r.get("hpo_precision", 0) for r in gold) / len(gold)
    macro_r = sum(r.get("hpo_recall", 0) for r in gold) / len(gold)
    macro_f1 = 2 * macro_p * macro_r / max(macro_p + macro_r, 1e-9)
    return {
        "micro_precision": round(micro_p, 4), "micro_recall": round(micro_r, 4),
        "micro_f1": round(micro_f1, 4), "macro_precision": round(macro_p, 4),
        "macro_recall": round(macro_r, 4), "macro_f1": round(macro_f1, 4),
        "total_tp": total_tp, "total_fn": total_fn, "total_extracted": total_ext,
    }


def compute_cascade(outputs: list[dict]) -> dict:
    """Metric 2: Normalization cascade distribution."""
    match_types = Counter()
    confs = {}
    total = matched = 0
    for out in outputs:
        m4 = out.get("module4", {})
        for cat in ["problem", "treatment", "test"]:
            for e in m4.get(cat, []):
                total += 1
                mt = e.get("match_type", "none")
                if e.get("matched", False):
                    matched += 1
                    match_types[mt] += 1
                    confs.setdefault(mt, []).append(e.get("confidence", 0))
                else:
                    match_types["no_match"] += 1
    cascade = {}
    for mt, cnt in match_types.most_common():
        avg = sum(confs.get(mt, [0])) / max(len(confs.get(mt, [1])), 1)
        cascade[mt] = {"count": cnt, "pct": round(cnt / max(total, 1) * 100, 1), "avg_conf": round(avg, 3)}
    return {"total": total, "matched": matched, "coverage": round(matched / max(total, 1), 3), "cascade": cascade}


def compute_ordo(results: list[dict]) -> dict:
    """Metric 3: ORDO Top-K accuracy (strict ORPHA ID matching)."""
    gold = [r for r in results if r.get("has_gold")]
    top1 = sum(1 for r in gold if r.get("ordo_top1"))
    top3 = sum(1 for r in gold if r.get("ordo_correct"))
    top5 = sum(1 for r in gold if r.get("ordo_top5"))
    top10 = sum(1 for r in gold if r.get("ordo_top10"))
    n = max(len(gold), 1)
    return {
        "top1": top1, "top3": top3, "top5": top5, "top10": top10,
        "total": len(gold),
        "top1_acc": round(top1 / n, 3),
        "top3_acc": round(top3 / n, 3),
        "top5_acc": round(top5 / n, 3),
        "top10_acc": round(top10 / n, 3),
        # Backward compatibility
        "correct": top3, "accuracy": round(top3 / n, 3),
    }


def compute_detection(outputs: list[dict]) -> dict:
    """Metric 4: Negation & inconsistency detection."""
    negated = 0
    cues = Counter()
    temporal = inconsistencies = 0
    for out in outputs:
        w = out.get("module3_warnings", {})
        temporal += len(w.get("temporal", []))
        inconsistencies += len(w.get("inconsistencies", []))
        for cat in ["problem", "treatment", "test"]:
            for e in out.get("module4", {}).get(cat, []):
                if e.get("negated"):
                    negated += 1
                    if e.get("negation_cue"):
                        cues[e["negation_cue"]] += 1
    return {"negated": negated, "cues": dict(cues.most_common(10)),
            "temporal": temporal, "inconsistencies": inconsistencies, "reports": len(outputs)}


def compute_phenopacket(outputs: list[dict]) -> dict:
    """Metric 5: Phenopacket compliance."""
    required = ["id", "subject", "phenotypicFeatures", "metaData"]
    total = len(outputs)
    ok = 0
    total_feat = 0
    with_interp = with_excl = 0
    for out in outputs:
        pp = out.get("phenopacket", {})
        if all(pp.get(f) for f in required):
            ok += 1
        feats = pp.get("phenotypicFeatures", [])
        total_feat += len(feats)
        if pp.get("interpretations"):
            with_interp += 1
        if any(f.get("excluded") for f in feats):
            with_excl += 1
    return {"compliant": ok, "total": total, "rate": f"{ok}/{total} ({ok/max(total,1):.0%})",
            "avg_features": round(total_feat / max(total, 1), 1),
            "with_interpretations": with_interp, "with_excluded": with_excl}





# ═══════════════════════════════════════════════════════════════════════
#  PHASE 3: Print & Save Full Report
# ═══════════════════════════════════════════════════════════════════════

def print_report(lang: str, results: list[dict], outputs: list[dict]) -> dict:
    """Compute and print all metrics for one language."""
    hpo = compute_hpo_metrics(results)
    cascade = compute_cascade(outputs)
    ordo = compute_ordo(results)
    detect = compute_detection(outputs)
    pp = compute_phenopacket(outputs)

    avg_time = sum(r.get("time", 0) for r in results) / max(len(results), 1)

    print(f"\n{'─'*70}")
    print(f"  {lang} — RESULTS")
    print(f"{'─'*70}")

    # 1. HPO
    print(f"\n  1. HPO P/R/F1:")
    print(f"     Micro  P={hpo.get('micro_precision',0):.3f}  R={hpo.get('micro_recall',0):.3f}  F1={hpo.get('micro_f1',0):.3f}")
    print(f"     Macro  P={hpo.get('macro_precision',0):.3f}  R={hpo.get('macro_recall',0):.3f}  F1={hpo.get('macro_f1',0):.3f}")

    # 2. Cascade
    print(f"\n  2. Normalization: {cascade['matched']}/{cascade['total']} = {cascade['coverage']:.1%}")
    for mt, info in cascade["cascade"].items():
        print(f"     {mt:<25} {info['count']:>5} ({info['pct']:>5.1f}%)  conf={info['avg_conf']:.3f}")

    # 3. ORDO Top-K Accuracy
    print(f"\n  3. ORDO Disease Classification (n={ordo['total']})")
    print(f"     Top-1:  {ordo['top1']:>2}/{ordo['total']} = {ordo['top1_acc']:.1%}")
    print(f"     Top-3:  {ordo['top3']:>2}/{ordo['total']} = {ordo['top3_acc']:.1%}")
    print(f"     Top-5:  {ordo['top5']:>2}/{ordo['total']} = {ordo['top5_acc']:.1%}")
    print(f"     Top-10: {ordo['top10']:>2}/{ordo['total']} = {ordo['top10_acc']:.1%}")

    # 4. Detection
    print(f"\n  4. Detection: {detect['negated']} negated | {detect['inconsistencies']} inconsistencies")
    if detect["cues"]:
        print(f"     Top cues: {detect['cues']}")

    # 5. Phenopacket
    print(f"\n  5. Phenopacket: {pp['rate']} | avg {pp['avg_features']} features/report")

    # 6. Efficiency
    print(f"\n  6. Efficiency: {avg_time:.2f}s/report ({len(results)} reports)")

    return {
        "hpo": hpo, "cascade": cascade, "ordo": ordo, "detection": detect,
        "phenopacket": pp, "efficiency": {"avg_time": round(avg_time, 2), "reports": len(results)},
        "per_report": results,
    }


def print_crosslingual(fr: dict, en: dict):
    """Metric 6: Cross-lingual comparison."""
    print(f"\n{'─'*70}")
    print(f"  6. CROSS-LINGUAL COMPARISON (FR vs EN)")
    print(f"{'─'*70}")
    rows = [
        ("HPO Micro F1", fr["hpo"].get("micro_f1", 0), en["hpo"].get("micro_f1", 0)),
        ("HPO Macro F1", fr["hpo"].get("macro_f1", 0), en["hpo"].get("macro_f1", 0)),
        ("ORDO Top-3", fr["ordo"].get("top3_acc", 0), en["ordo"].get("top3_acc", 0)),
        ("Norm Coverage", fr["cascade"].get("coverage", 0), en["cascade"].get("coverage", 0)),
        ("Avg Time", fr["efficiency"]["avg_time"], en["efficiency"]["avg_time"]),
    ]
    print(f"\n  {'Metric':<20} {'French':>10} {'English':>10} {'Δ':>8}")
    print(f"  {'─'*50}")
    for name, fv, ev in rows:
        if name == "Avg Time":
            print(f"  {name:<20} {fv:>9.2f}s {ev:>9.2f}s {fv-ev:>+7.2f}s")
        else:
            print(f"  {name:<20} {fv:>9.1%} {ev:>9.1%} {fv-ev:>+7.1%}")


def main():
    limit = None
    skip_run = "--skip-run" in sys.argv
    lang_filter = None  # None = both, "fr" = French only, "en" = English only

    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        if idx + 1 < len(sys.argv):
            limit = int(sys.argv[idx + 1])

    if "--lang" in sys.argv:
        idx = sys.argv.index("--lang")
        if idx + 1 < len(sys.argv):
            lang_filter = sys.argv[idx + 1].lower()
            if lang_filter not in ("fr", "en", "none"):
                print(f"  ERROR: --lang must be 'fr', 'en', or 'none', got '{lang_filter}'")
                sys.exit(1)

    run_fr = lang_filter in (None, "fr")
    run_en = lang_filter in (None, "en")

    label = {"fr": "FRENCH ONLY", "en": "ENGLISH ONLY"}.get(lang_filter, "ALL LANGUAGES")
    print("=" * 70)
    print(f"  UNIFIED EVALUATION — {label}")
    print("=" * 70)

    # ── Phase 1: Run pipeline (or load saved) ─────────────────────────
    fr_results, en_results = [], []

    if skip_run:
        print("\n  --skip-run: Loading metrics from saved outputs...")
        for path, lst, needed in [
            ("chu_evaluation_report.json", fr_results, run_fr),
            ("pubmed_evaluation_report.json", en_results, run_en),
        ]:
            if not needed:
                continue
            rp = OUTPUT_DIR / path
            if rp.exists():
                with open(rp, encoding="utf-8") as f:
                    data = json.load(f)
                lst.extend(data.get("per_report", []))
    else:
        print("\n  Phase 1: Running pipeline...")
        if run_fr:
            fr_results = run_pipeline_on_dataset("chu", limit=limit)
        if run_en:
            en_results = run_pipeline_on_dataset("pubmed", limit=limit)

    # Load full output JSONs for cascade/detection/phenopacket metrics
    fr_outputs = load_saved_outputs("chu_evaluation") if run_fr else []
    en_outputs = load_saved_outputs("pubmed_evaluation") if run_en else []

    # ── GSC dataset (optional) ────────────────────────────────────────
    run_gsc = "--gsc" in sys.argv
    gsc_results, gsc_outputs = [], []

    if run_gsc:
        gsc_results = run_pipeline_on_dataset("gsc", limit=limit)
        gsc_outputs = load_saved_outputs("gsc_evaluation")

    # ── RareArena dataset (optional) ──────────────────────────────────
    run_ra = "--rarearena" in sys.argv
    ra_results, ra_outputs = [], []

    if run_ra:
        ra_results = run_pipeline_on_dataset("rarearena", limit=limit)
        ra_outputs = load_saved_outputs("rarearena_evaluation")

    # ── CHU Translated (optional) ─────────────────────────────────────
    run_chu_en = "--chu-en" in sys.argv
    chu_en_results, chu_en_outputs = [], []

    if run_chu_en:
        chu_en_results = run_pipeline_on_dataset("chu_en", limit=limit)
        chu_en_outputs = load_saved_outputs("chu_en_evaluation")

    parts = []
    if run_fr:
        parts.append(f"{len(fr_results)} FR results")
    if run_en:
        parts.append(f"{len(en_results)} EN results")
    if run_gsc:
        parts.append(f"{len(gsc_results)} GSC results")
    if run_ra:
        parts.append(f"{len(ra_results)} RareArena results")
    if run_chu_en:
        parts.append(f"{len(chu_en_results)} CHU-EN results")
    print(f"\n  Loaded: {' + '.join(parts)}")

    out_parts = []
    if run_fr:
        out_parts.append(f"{len(fr_outputs)} FR JSONs")
    if run_en:
        out_parts.append(f"{len(en_outputs)} EN JSONs")
    if run_gsc:
        out_parts.append(f"{len(gsc_outputs)} GSC JSONs")
    if run_ra:
        out_parts.append(f"{len(ra_outputs)} RareArena JSONs")
    if run_chu_en:
        out_parts.append(f"{len(chu_en_outputs)} CHU-EN JSONs")
    print(f"  Outputs: {' + '.join(out_parts)}")

    # ── Phase 2: Compute all metrics ──────────────────────────────────
    fr, en, gsc, ra, chu_en = None, None, None, None, None
    if run_fr:
        fr = print_report("FRENCH (CHU Oran)", fr_results, fr_outputs)
    if run_en:
        en = print_report("ENGLISH (PubMed)", en_results, en_outputs)
    if run_gsc:
        gsc = print_report("ENGLISH (GSC Clinical Cases)", gsc_results, gsc_outputs)
    if run_ra:
        ra = print_report("ENGLISH (RareArena - Lancet 2026)", ra_results, ra_outputs)
    if run_chu_en:
        chu_en = print_report("ENGLISH (CHU Translated FR→EN)", chu_en_results, chu_en_outputs)

    # ── Phase 3: Cross-lingual (only when both) ──────────────────────
    if fr and en:
        print_crosslingual(fr, en)

    # ── Save full report ──────────────────────────────────────────────
    full_report = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}

    if fr:
        full_report["french"] = {k: v for k, v in fr.items() if k != "per_report"}
        full_report["french_per_report"] = fr.get("per_report", [])
    if en:
        full_report["english"] = {k: v for k, v in en.items() if k != "per_report"}
        full_report["english_per_report"] = en.get("per_report", [])
    if gsc:
        full_report["gsc"] = {k: v for k, v in gsc.items() if k != "per_report"}
        full_report["gsc_per_report"] = gsc.get("per_report", [])
    if ra:
        full_report["rarearena"] = {k: v for k, v in ra.items() if k != "per_report"}
        full_report["rarearena_per_report"] = ra.get("per_report", [])

    # Save per-language reports
    save_list = []
    if fr:
        save_list.append(("chu_evaluation_report.json", fr, "CHU Oran"))
    if en:
        save_list.append(("pubmed_evaluation_report.json", en, "PubMed English"))
    if gsc:
        save_list.append(("gsc_evaluation_report.json", gsc, "GSC Clinical Cases"))
    if ra:
        save_list.append(("rarearena_evaluation_report.json", ra, "RareArena (Lancet 2026)"))

    for name, data, dataset_label in save_list:
        report = {
            "timestamp": full_report["timestamp"],
            "pipeline": "v4.0 (DeBERTa-v3 bilingual)",
            "dataset": dataset_label,
            "total_reports": data["efficiency"]["reports"],
            "gold_standard_reports": data["ordo"]["total"],
            "metrics": {
                "ordo_top1_accuracy": data["ordo"]["top1_acc"],
                "ordo_top3_accuracy": data["ordo"]["top3_acc"],
                "ordo_top5_accuracy": data["ordo"]["top5_acc"],
                "ordo_top10_accuracy": data["ordo"]["top10_acc"],
                "hpo_micro_precision": data["hpo"].get("micro_precision"),
                "hpo_micro_recall": data["hpo"].get("micro_recall"),
                "hpo_micro_f1": data["hpo"].get("micro_f1"),
                "hpo_macro_precision": data["hpo"].get("macro_precision"),
                "hpo_macro_recall": data["hpo"].get("macro_recall"),
                "hpo_macro_f1": data["hpo"].get("macro_f1"),
                "normalization_coverage": data["cascade"]["coverage"],
                "avg_time_per_report": data["efficiency"]["avg_time"],
            },
            "per_report": data.get("per_report", []),
        }
        with open(OUTPUT_DIR / name, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    report_path = OUTPUT_DIR / "all_metrics_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n{'='*70}")
    print(f"  Reports saved:")
    print(f"    {report_path}")
    if fr:
        print(f"    {OUTPUT_DIR / 'chu_evaluation_report.json'}")
    if en:
        print(f"    {OUTPUT_DIR / 'pubmed_evaluation_report.json'}")
    if gsc:
        print(f"    {OUTPUT_DIR / 'gsc_evaluation_report.json'}")
    if ra:
        print(f"    {OUTPUT_DIR / 'rarearena_evaluation_report.json'}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()

