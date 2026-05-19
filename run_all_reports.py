"""
Run ALL CHU Oran hospital reports through the bilingual pipeline.
Reads .docx files from the reports folder and processes each one.
"""

import os
import sys
import json
import time
import re
from docx import Document

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from pipeline import FullPipeline
from evaluation.gold_standard_fr import GOLD_STANDARD_FR
from evaluation.metrics import evaluate_note

REPORTS_DIR = r"c:\DEV\PFE\Rapports Med nov 25 a MAI 26\Rapports Med nov 25 a MAI 26"


def extract_patient_name(filename: str) -> str:
    """Extract patient name from filename."""
    name = os.path.splitext(filename)[0]
    # Remove common suffixes
    for suffix in ["- Copie", "_recu_9", "_Dr_Djoudi", "Dr Djoudi",
                   "Novembre", "Décembre", "Mars", "Nov 25", "Mars 26",
                   "mars 28", "mars 2026", "02_2026", "15_12_2026", "23_03_2026"]:
        name = name.replace(suffix, "")
    return name.strip().rstrip("_ ")


def detect_pathology(text: str, filename: str) -> str:
    """Try to detect the pathology from the report text or filename."""
    combined = (text + " " + filename).lower()
    if "mucoviscidose" in combined:
        return "Mucoviscidose"
    elif "wiskott" in combined:
        return "Wiskott-Aldrich"
    elif "agammaglobulin" in combined:
        return "Agammaglobulinémie (Bruton)"
    elif "scid" in combined or "déficit immunitaire combiné sévère" in combined or "dics" in combined:
        return "SCID"
    elif "skid" in combined:
        return "SCID-like"
    elif "ataxie" in combined or "télangiectasie" in combined or "telangiectasie" in combined:
        return "Ataxie-Télangiectasie"
    elif "hla" in combined:
        return "Déficit HLA-DR"
    elif "dip" in combined or "déficit immunitaire primitif" in combined:
        return "DIP (type non spécifié)"
    elif "hyper ige" in combined or "hyper-ige" in combined or "job" in combined:
        return "Syndrome Hyper-IgE"
    elif "dicv" in combined:
        return "DICV"
    else:
        return "Non identifié"


def collect_all_reports() -> list:
    """Collect all .docx reports recursively."""
    reports = []
    for root, dirs, files in os.walk(REPORTS_DIR):
        for fname in sorted(files):
            if fname.endswith(".docx") and not fname.startswith("~"):
                filepath = os.path.join(root, fname)
                # Determine subfolder
                rel = os.path.relpath(root, REPORTS_DIR)
                subfolder = rel if rel != "." else "Dr Djoudi"
                reports.append({
                    "filepath": filepath,
                    "filename": fname,
                    "subfolder": subfolder,
                    "patient": extract_patient_name(fname),
                })
    return reports


def extract_text(filepath: str) -> str:
    """Extract text from a .docx file."""
    doc = Document(filepath)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def main():
    output_dir = os.path.join(PROJECT_ROOT, "output", "all_reports")
    os.makedirs(output_dir, exist_ok=True)

    reports = collect_all_reports()
    print("=" * 70)
    print(f" CHU ORAN — FULL CORPUS PROCESSING ({len(reports)} reports)")
    print(" Pipeline: PHI → NER (GLiNER) → NegEx → Numeric → HPO → ORDO")
    print("=" * 70)

    # Init pipeline
    start_init = time.time()
    pipeline_obj = FullPipeline()
    init_time = round(time.time() - start_init, 1)
    print(f"\nPipeline initialized in {init_time}s\n")

    all_results = []
    pathology_stats = {}
    ordo_correct = 0
    ordo_total = 0

    for i, report in enumerate(reports):
        note_id = f"CHU_{i+1:03d}"
        print(f"\n{'─'*60}")
        print(f" [{i+1}/{len(reports)}] {note_id}: {report['filename'][:50]}")
        print(f"{'─'*60}")

        try:
            text = extract_text(report["filepath"])
        except Exception as e:
            print(f"  ERROR reading file: {e}")
            continue

        if len(text) < 100:
            print(f"  SKIP: too short ({len(text)} chars)")
            continue

        pathology = detect_pathology(text, report["filename"])
        print(f"  Patient: {report['patient']}")
        print(f"  Pathology: {pathology}")
        print(f"  Text length: {len(text)} chars")

        start = time.time()
        try:
            result = pipeline_obj.process_and_save(
                clinical_text=text,
                note_id=note_id,
                output_dir=output_dir,
                lang="fr",
            )
        except Exception as e:
            print(f"  ERROR in pipeline: {e}")
            continue
        elapsed = round(time.time() - start, 2)

        # Extract key results
        m4 = result.get("module4", {})
        stats = m4.get("stats", {})
        ordo = m4.get("ordo_candidates", [])
        numeric = result.get("module3", {}).get("numeric_phenotypes", [])

        negated = sum(
            1 for cat in ["problem", "treatment", "test"]
            for e in result.get("module2", {}).get("entities", {}).get(cat, [])
            if e.get("negated", False)
        )

        top_ordo = ordo[0] if ordo else None
        top_ordo_name = (top_ordo.get("name_fr") or top_ordo["name"]) if top_ordo else "—"
        top_ordo_score = top_ordo["score"] if top_ordo else 0

        # Check if ORDO is correct
        ordo_match = False
        if top_ordo:
            ordo_total += 1
            tn = top_ordo_name.lower()
            pl = pathology.lower()
            if any(k in tn for k in pl.split("(")[0].strip().lower().split("-")):
                ordo_match = True
                ordo_correct += 1
            elif pathology == "SCID" and "combiné sévère" in tn:
                ordo_match = True
                ordo_correct += 1
            elif pathology == "SCID-like" and ("combiné sévère" in tn or "scid" in tn):
                ordo_match = True
                ordo_correct += 1

        print(f"  Time: {elapsed}s | Entities: {stats.get('total', 0)} | "
              f"HPO matched: {stats.get('matched', 0)} | Numeric: {len(numeric)} | "
              f"Negated: {negated}")
        ordo_marker = "✅" if ordo_match else "❌" if top_ordo else "—"
        print(f"  ORDO: {top_ordo_name} (score={top_ordo_score:.3f}) {ordo_marker}")

        # Track by pathology
        if pathology not in pathology_stats:
            pathology_stats[pathology] = {
                "count": 0, "total_entities": 0, "total_matched": 0,
                "total_numeric": 0, "total_negated": 0,
                "ordo_correct": 0, "patients": set(),
            }
        ps = pathology_stats[pathology]
        ps["count"] += 1
        ps["total_entities"] += stats.get("total", 0)
        ps["total_matched"] += stats.get("matched", 0)
        ps["total_numeric"] += len(numeric)
        ps["total_negated"] += negated
        if ordo_match:
            ps["ordo_correct"] += 1
        ps["patients"].add(report["patient"])

        all_results.append({
            "note_id": note_id,
            "filename": report["filename"],
            "patient": report["patient"],
            "pathology": pathology,
            "subfolder": report["subfolder"],
            "processing_time": elapsed,
            "text_length": len(text),
            "total_entities": stats.get("total", 0),
            "matched_hpo": stats.get("matched", 0),
            "match_rate": stats.get("match_rate", 0),
            "numeric_phenotypes": len(numeric),
            "negated_entities": negated,
            "top_ordo": top_ordo_name,
            "top_ordo_score": top_ordo_score,
            "ordo_correct": ordo_match,
            "unique_hpo": stats.get("unique_hpo", 0),
        })

    # ── Summary ──────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f" FULL CORPUS RESULTS — {len(all_results)} reports processed")
    print(f"{'='*70}")

    total_entities = sum(r["total_entities"] for r in all_results)
    total_matched = sum(r["matched_hpo"] for r in all_results)
    total_numeric = sum(r["numeric_phenotypes"] for r in all_results)
    total_negated = sum(r["negated_entities"] for r in all_results)
    avg_time = sum(r["processing_time"] for r in all_results) / len(all_results) if all_results else 0

    print(f"\n  Reports processed:     {len(all_results)}")
    print(f"  Unique patients:       {len(set(r['patient'] for r in all_results))}")
    print(f"  Total entities:        {total_entities}")
    print(f"  HPO matched:           {total_matched} ({total_matched/total_entities*100:.1f}%)")
    print(f"  Numeric phenotypes:    {total_numeric}")
    print(f"  Negated entities:      {total_negated}")
    print(f"  Avg processing time:   {avg_time:.2f}s/report")
    print(f"  ORDO Top-1 accuracy:   {ordo_correct}/{ordo_total} ({ordo_correct/ordo_total*100:.0f}%)")

    print(f"\n  BY PATHOLOGY:")
    print(f"  {'Pathology':<35s} {'Reports':>7s} {'Patients':>8s} {'Entities':>8s} {'HPO':>5s} {'ORDO':>6s}")
    print(f"  {'─'*35} {'─'*7} {'─'*8} {'─'*8} {'─'*5} {'─'*6}")
    for path, ps in sorted(pathology_stats.items(), key=lambda x: -x[1]["count"]):
        ordo_str = f"{ps['ordo_correct']}/{ps['count']}"
        print(f"  {path:<35s} {ps['count']:>7d} {len(ps['patients']):>8d} "
              f"{ps['total_entities']:>8d} {ps['total_matched']:>5d} {ordo_str:>6s}")

    # Save report
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "pipeline_version": "v3 (bilingual FR+EN)",
        "corpus": "CHU Oran — Full Corpus",
        "total_reports": len(all_results),
        "unique_patients": len(set(r["patient"] for r in all_results)),
        "init_time_seconds": init_time,
        "summary": {
            "total_entities": total_entities,
            "total_matched_hpo": total_matched,
            "match_rate_pct": round(total_matched / total_entities * 100, 1) if total_entities else 0,
            "total_numeric_phenotypes": total_numeric,
            "total_negated": total_negated,
            "avg_processing_time": round(avg_time, 2),
            "ordo_accuracy": f"{ordo_correct}/{ordo_total}",
        },
        "per_report": all_results,
    }
    # Convert sets to lists for JSON
    report_path = os.path.join(output_dir, "full_corpus_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n  Full report saved: {report_path}")
    print(f"\n Done!\n")


if __name__ == "__main__":
    main()
