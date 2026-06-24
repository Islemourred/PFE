"""
Generate SCORE Framework Charts for All Datasets.
Computes S.C.O.R.E. dimensions from saved evaluation outputs and generates:
  1. SCORE per-dataset bar chart (grouped by dimension)
  2. SCORE radar chart (all datasets overlay)
  3. SCORE composite comparison bar chart
"""

import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = Path(PROJECT_ROOT) / "output"
FIGURES_DIR = Path(PROJECT_ROOT).parent / "memoire_PFE" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════
#  SCORE Computation from Pipeline Outputs
# ═══════════════════════════════════════════════════════════════════════

REQUIRED_FIELDS = {
    "name": 3, "age": 3, "sex": 2, "origin": 1, "diagnosis": 3,
    "consanguinity": 1, "father": 1, "mother": 1,
}

def compute_score_for_outputs(outputs: list[dict], dataset_label: str) -> dict:
    """Compute SCORE framework dimensions from pipeline outputs."""
    all_s, all_c, all_o, all_r, all_e = [], [], [], [], []
    
    for out in outputs:
        m4 = out.get("module4", {})
        m3_warnings = out.get("module3_warnings", {})
        pp = out.get("phenopacket", {})
        
        # ── S: Structuring ──────────────────────────────────────────
        # Check presence of key fields in phenopacket
        subject = pp.get("subject", {})
        fields_present = 0
        fields_total = 0
        
        # Check subject fields
        if subject.get("id"):
            fields_present += 3  # name weight
        fields_total += 3
        
        if subject.get("timeAtLastEncounter"):
            fields_present += 3  # age weight  
        fields_total += 3
        
        if subject.get("sex") and subject["sex"] != "UNKNOWN_SEX":
            fields_present += 2  # sex weight
        fields_total += 2
        
        # Check phenotypic features exist
        feats = pp.get("phenotypicFeatures", [])
        if len(feats) > 0:
            fields_present += 3  # diagnosis weight
        fields_total += 3
        
        # Check interpretations
        if pp.get("interpretations"):
            fields_present += 2
        fields_total += 2
        
        # Check metadata
        if pp.get("metaData"):
            fields_present += 1
        fields_total += 1
        
        s_score = (fields_present / max(fields_total, 1)) * 100
        all_s.append(s_score)
        
        # ── C: Clinical Coherence ───────────────────────────────────
        n_inconsistencies = len(m3_warnings.get("temporal", []))
        n_inconsistencies += len(m3_warnings.get("inconsistencies", []))
        
        # Count total entities as total checks
        total_entities = 0
        for cat in ["problem", "treatment", "test"]:
            total_entities += len(m4.get(cat, []))
        
        total_checks = max(total_entities, 5)  # Minimum 5 checks
        c_score = (1 - n_inconsistencies / total_checks) * 100
        c_score = max(0, min(100, c_score))
        all_c.append(c_score)
        
        # ── O: Ontological Coverage ─────────────────────────────────
        matched = 0
        total = 0
        for cat in ["problem", "treatment", "test"]:
            for e in m4.get(cat, []):
                total += 1
                if e.get("matched", False) or e.get("hpo_id"):
                    matched += 1
        
        o_score = (matched / max(total, 1)) * 100
        all_o.append(o_score)
        
        # ── R: Reliability ──────────────────────────────────────────
        confidences = []
        for cat in ["problem", "treatment", "test"]:
            for e in m4.get(cat, []):
                conf = e.get("confidence", e.get("score", 0))
                if conf:
                    confidences.append(float(conf))
        
        r_score = (sum(confidences) / max(len(confidences), 1)) * 100 if confidences else 50.0
        r_score = min(100, r_score)
        all_r.append(r_score)
        
        # ── E: Explainability ───────────────────────────────────────
        traceable = 0
        total_e_check = 0
        for cat in ["problem", "treatment", "test"]:
            for e in m4.get(cat, []):
                total_e_check += 1
                # Entity is traceable if it has source text, model info, and match type
                has_text = bool(e.get("text") or e.get("original_text"))
                has_model = bool(e.get("model") or e.get("source"))
                has_match = bool(e.get("match_type") or e.get("hpo_id"))
                if has_text and (has_model or has_match):
                    traceable += 1
        
        e_score = (traceable / max(total_e_check, 1)) * 100
        all_e.append(e_score)
    
    # Compute means
    mean_s = np.mean(all_s) if all_s else 0
    mean_c = np.mean(all_c) if all_c else 0
    mean_o = np.mean(all_o) if all_o else 0
    mean_r = np.mean(all_r) if all_r else 0
    mean_e = np.mean(all_e) if all_e else 0
    
    # Composite SCORE (weighted)
    composite = 0.20 * mean_s + 0.25 * mean_c + 0.20 * mean_o + 0.20 * mean_r + 0.15 * mean_e
    
    result = {
        "dataset": dataset_label,
        "n_reports": len(outputs),
        "S": {"mean": round(mean_s, 1), "min": round(min(all_s) if all_s else 0, 1), "max": round(max(all_s) if all_s else 0, 1)},
        "C": {"mean": round(mean_c, 1), "min": round(min(all_c) if all_c else 0, 1), "max": round(max(all_c) if all_c else 0, 1)},
        "O": {"mean": round(mean_o, 1), "min": round(min(all_o) if all_o else 0, 1), "max": round(max(all_o) if all_o else 0, 1)},
        "R": {"mean": round(mean_r, 1), "min": round(min(all_r) if all_r else 0, 1), "max": round(max(all_r) if all_r else 0, 1)},
        "E": {"mean": round(mean_e, 1), "min": round(min(all_e) if all_e else 0, 1), "max": round(max(all_e) if all_e else 0, 1)},
        "composite": round(composite, 1),
    }
    
    # Rating
    if composite >= 90: result["rating"] = "Excellent"
    elif composite >= 75: result["rating"] = "Good"
    elif composite >= 60: result["rating"] = "Acceptable"
    elif composite >= 40: result["rating"] = "Fair"
    else: result["rating"] = "Poor"
    
    return result


def load_outputs(subdir: str) -> list[dict]:
    """Load all *_full_output.json from a subdirectory."""
    d = OUTPUT_DIR / subdir
    outputs = []
    if d.exists():
        for f in sorted(d.glob("*_full_output.json")):
            with open(f, encoding="utf-8") as fh:
                outputs.append(json.load(fh))
    return outputs


# ═══════════════════════════════════════════════════════════════════════
#  Chart Generation
# ═══════════════════════════════════════════════════════════════════════

COLORS = {
    "HPC FR": "#3b82f6",
    "HPC EN": "#8b5cf6", 
    "PubMed EN": "#10b981",
    "GSC EN": "#f59e0b",
    "RareArena EN": "#ef4444",
}

def chart_score_grouped_bar(all_scores: list[dict]):
    """Chart 1: Grouped bar chart of SCORE dimensions per dataset."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    dims = ["S", "C", "O", "R", "E"]
    dim_labels = ["Structuring", "Clinical\nCoherence", "Ontological\nCoverage", "Reliability", "Explainability"]
    n_datasets = len(all_scores)
    x = np.arange(len(dims))
    width = 0.15
    
    for i, score_data in enumerate(all_scores):
        label = score_data["dataset"]
        values = [score_data[d]["mean"] for d in dims]
        color = list(COLORS.values())[i % len(COLORS)]
        offset = (i - n_datasets / 2 + 0.5) * width
        bars = ax.bar(x + offset, values, width, label=label, color=color, alpha=0.85, edgecolor="white", linewidth=0.5)
        
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f"{val:.0f}",
                    ha="center", va="bottom", fontsize=7, fontweight="bold")
    
    ax.set_xlabel("SCORE Dimension", fontsize=11)
    ax.set_ylabel("Score (0-100)", fontsize=11)
    ax.set_title("SCORE Framework — Per-Dimension Results Across All Datasets", fontsize=13, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(dim_labels, fontsize=9)
    ax.set_ylim(0, 110)
    ax.legend(loc="upper right", fontsize=8, framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    fig.tight_layout()
    path = FIGURES_DIR / "score_dimensions_all_datasets.pdf"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    print(f"  Saved: {path}")
    plt.close(fig)


def chart_score_radar(all_scores: list[dict]):
    """Chart 2: Radar chart overlay of all datasets."""
    dims = ["S", "C", "O", "R", "E"]
    dim_labels = ["Structuring", "Clinical\nCoherence", "Ontological\nCoverage", "Reliability", "Explainability"]
    
    angles = np.linspace(0, 2 * np.pi, len(dims), endpoint=False).tolist()
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    for i, score_data in enumerate(all_scores):
        label = score_data["dataset"]
        values = [score_data[d]["mean"] for d in dims]
        values += values[:1]
        color = list(COLORS.values())[i % len(COLORS)]
        ax.plot(angles, values, "o-", linewidth=2, label=label, color=color, markersize=5)
        ax.fill(angles, values, alpha=0.08, color=color)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dim_labels, fontsize=9)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=7)
    ax.set_title("SCORE Framework — Radar Comparison Across Datasets", fontsize=13, fontweight="bold", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=8)
    ax.grid(True, alpha=0.3)
    
    fig.tight_layout()
    path = FIGURES_DIR / "score_radar_all_datasets.pdf"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    print(f"  Saved: {path}")
    plt.close(fig)


def chart_score_composite(all_scores: list[dict]):
    """Chart 3: Composite SCORE horizontal bar chart."""
    fig, ax = plt.subplots(figsize=(10, 4))
    
    datasets = [s["dataset"] for s in all_scores]
    composites = [s["composite"] for s in all_scores]
    ratings = [s["rating"] for s in all_scores]
    colors = [list(COLORS.values())[i % len(COLORS)] for i in range(len(all_scores))]
    
    y_pos = np.arange(len(datasets))
    bars = ax.barh(y_pos, composites, color=colors, alpha=0.85, edgecolor="white", height=0.6)
    
    for bar, val, rating in zip(bars, composites, ratings):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f"{val:.1f} ({rating})", ha="left", va="center", fontsize=10, fontweight="bold")
    
    # Rating zone backgrounds
    ax.axvspan(0, 40, alpha=0.05, color="red")
    ax.axvspan(40, 60, alpha=0.05, color="orange")
    ax.axvspan(60, 75, alpha=0.05, color="yellow")
    ax.axvspan(75, 90, alpha=0.05, color="lightgreen")
    ax.axvspan(90, 100, alpha=0.05, color="green")
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(datasets, fontsize=10)
    ax.set_xlabel("Composite SCORE (0-100)", fontsize=11)
    ax.set_title("SCORE Framework — Composite Quality Assessment per Dataset", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlim(0, 105)
    ax.grid(axis="x", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.invert_yaxis()
    
    fig.tight_layout()
    path = FIGURES_DIR / "score_composite_all_datasets.pdf"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    print(f"  Saved: {path}")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  SCORE Framework — All Datasets Computation")
    print("=" * 60)
    
    datasets = [
        ("chu_evaluation", "HPC FR"),
        ("chu_en_evaluation", "HPC EN"),
        ("pubmed_evaluation", "PubMed EN"),
        ("gsc_evaluation", "GSC EN"),
        ("rarearena_evaluation", "RareArena EN"),
    ]
    
    all_scores = []
    
    for subdir, label in datasets:
        outputs = load_outputs(subdir)
        if not outputs:
            print(f"  [SKIP] {label}: No outputs found in {subdir}/")
            continue
        
        score = compute_score_for_outputs(outputs, label)
        all_scores.append(score)
        
        print(f"\n  {label} ({score['n_reports']} reports):")
        print(f"    S={score['S']['mean']:5.1f}  C={score['C']['mean']:5.1f}  O={score['O']['mean']:5.1f}  R={score['R']['mean']:5.1f}  E={score['E']['mean']:5.1f}")
        print(f"    Composite: {score['composite']:.1f} ({score['rating']})")
    
    if not all_scores:
        print("\n  ERROR: No datasets found!")
        return
    
    # Save JSON
    score_path = OUTPUT_DIR / "score_all_datasets.json"
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(all_scores, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved: {score_path}")
    
    # Generate charts
    print("\n  Generating charts...")
    chart_score_grouped_bar(all_scores)
    chart_score_radar(all_scores)
    chart_score_composite(all_scores)
    
    print(f"\n{'=' * 60}")
    print("  Done! 3 charts generated.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
