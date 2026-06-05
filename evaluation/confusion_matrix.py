"""
Confusion Matrix & Visualization Generator
Produces publication-ready figures for the mémoire (Chapter 5).

Generates:
  1. Per-note confusion matrix heatmap
  2. Match method distribution pie chart
  3. Summary metrics bar chart

Usage:
    python evaluation/confusion_matrix.py
"""

import os
import sys
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def generate_confusion_heatmap(report: dict, output_dir: str):
    """Generate per-note TP/FP/FN heatmap."""
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use("Agg")
    import numpy as np

    metrics = [m for m in report["per_note_metrics"]
               if m.get("tp", 0) + m.get("fn", 0) > 0]

    if not metrics:
        print("  No evaluable notes found for heatmap.")
        return

    note_ids = [m["note_id"] for m in metrics]
    tp_vals = [m["tp"] for m in metrics]
    fp_vals = [m["fp"] for m in metrics]
    fn_vals = [m["fn"] for m in metrics]

    data = np.array([tp_vals, fp_vals, fn_vals])

    fig, ax = plt.subplots(figsize=(max(10, len(note_ids) * 0.9), 4))

    # Color scheme: TP=green, FP=orange, FN=red
    colors = ["#2ecc71", "#e67e22", "#e74c3c"]
    labels = ["TP (Correct)", "FP (Extra)", "FN (Missed)"]

    x = np.arange(len(note_ids))
    width = 0.25

    for i, (vals, color, label) in enumerate(zip(data, colors, labels)):
        bars = ax.bar(x + i * width, vals, width, label=label, color=color,
                      edgecolor="white", linewidth=0.5)
        # Add value labels on bars
        for bar, val in zip(bars, vals):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.2,
                        str(val), ha="center", va="bottom", fontsize=8, fontweight="bold")

    ax.set_xlabel("Clinical Note", fontsize=11)
    ax.set_ylabel("Count", fontsize=11)
    ax.set_title("Per-Note Evaluation: TP / FP / FN Distribution", fontsize=13, fontweight="bold")
    ax.set_xticks(x + width)
    ax.set_xticklabels(note_ids, rotation=45, ha="right", fontsize=9)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    ax.set_axisbelow(True)

    plt.tight_layout()
    path = os.path.join(output_dir, "confusion_heatmap.png")
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def generate_prf1_chart(report: dict, output_dir: str):
    """Generate per-note Precision/Recall/F1 bar chart."""
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use("Agg")
    import numpy as np

    metrics = [m for m in report["per_note_metrics"]
               if m.get("tp", 0) + m.get("fn", 0) > 0]

    if not metrics:
        print("  No evaluable notes found for P/R/F1 chart.")
        return

    note_ids = [m["note_id"] for m in metrics]
    p_vals = [m["precision"] for m in metrics]
    r_vals = [m["recall"] for m in metrics]
    f1_vals = [m["f1"] for m in metrics]

    fig, ax = plt.subplots(figsize=(max(10, len(note_ids) * 0.9), 5))

    x = np.arange(len(note_ids))
    width = 0.25

    ax.bar(x - width, p_vals, width, label="Precision", color="#3498db", edgecolor="white")
    ax.bar(x, r_vals, width, label="Recall", color="#2ecc71", edgecolor="white")
    ax.bar(x + width, f1_vals, width, label="F1-Score", color="#9b59b6", edgecolor="white")

    # Add aggregate line
    agg = report.get("aggregate", {})
    if agg.get("micro_f1"):
        ax.axhline(y=agg["micro_f1"], color="#e74c3c", linestyle="--", linewidth=1.5,
                    label=f"Micro F1 = {agg['micro_f1']:.3f}")

    ax.set_xlabel("Clinical Note", fontsize=11)
    ax.set_ylabel("Score", fontsize=11)
    ax.set_title("Per-Note Precision, Recall & F1-Score", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(note_ids, rotation=45, ha="right", fontsize=9)
    ax.set_ylim(0, 1.15)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    ax.set_axisbelow(True)

    plt.tight_layout()
    path = os.path.join(output_dir, "prf1_chart.png")
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def generate_match_method_pie(output_dir: str):
    """Generate normalization method distribution pie chart."""
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use("Agg")

    methods = {}
    total = 0

    for fname in os.listdir(output_dir):
        if fname.endswith("_full_output.json"):
            path = os.path.join(output_dir, fname)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            m4 = data.get("module4", data.get("step2", {}))
            for cat in ["problem", "treatment", "test"]:
                for ent in m4.get(cat, []):
                    mt = ent.get("match_type", "no_match")
                    methods[mt] = methods.get(mt, 0) + 1
                    total += 1

    if not methods or total == 0:
        print("  No entity data found for pie chart.")
        return

    # Clean up labels
    label_map = {
        "exact_label": "Exact Label Match",
        "exact_synonym": "Exact Synonym Match",
        "clinical_synonym": "Clinical Synonym",
        "substring_match": "Substring Match",
        "sapbert_similarity": "SapBERT (AI)",
        "french_dict": "French Dictionary",
        "no_match": "Unmatched",
    }
    colors_map = {
        "exact_label": "#2ecc71",
        "exact_synonym": "#27ae60",
        "clinical_synonym": "#1abc9c",
        "substring_match": "#16a085",
        "sapbert_similarity": "#3498db",
        "french_dict": "#9b59b6",
        "no_match": "#95a5a6",
    }

    labels = []
    sizes = []
    colors = []
    for method, count in sorted(methods.items(), key=lambda x: -x[1]):
        labels.append(f"{label_map.get(method, method)}\n({count}, {count/total*100:.1f}%)")
        sizes.append(count)
        colors.append(colors_map.get(method, "#bdc3c7"))

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts = ax.pie(
        sizes, labels=labels, colors=colors,
        startangle=90, textprops={"fontsize": 9},
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    ax.set_title("Normalization Method Distribution", fontsize=14, fontweight="bold", pad=20)

    plt.tight_layout()
    path = os.path.join(output_dir, "match_method_pie.png")
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def generate_summary_table(report: dict, output_dir: str):
    """Generate a summary metrics table as an image."""
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use("Agg")

    agg = report.get("aggregate", {})
    if not agg:
        print("  No aggregate metrics for summary table.")
        return

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.axis("off")

    table_data = [
        ["Micro Precision", f"{agg.get('micro_precision', 0):.4f}"],
        ["Micro Recall", f"{agg.get('micro_recall', 0):.4f}"],
        ["Micro F1-Score", f"{agg.get('micro_f1', 0):.4f}"],
        ["Macro Precision", f"{agg.get('macro_precision', 0):.4f}"],
        ["Macro Recall", f"{agg.get('macro_recall', 0):.4f}"],
        ["Macro F1-Score", f"{agg.get('macro_f1', 0):.4f}"],
        ["Total TP", str(agg.get("total_tp", 0))],
        ["Total FP", str(agg.get("total_fp", 0))],
        ["Total FN", str(agg.get("total_fn", 0))],
    ]

    table = ax.table(
        cellText=table_data,
        colLabels=["Metric", "Value"],
        cellLoc="center",
        loc="center",
        colWidths=[0.5, 0.3],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 1.5)

    # Style header
    for j in range(2):
        table[0, j].set_facecolor("#2c3e50")
        table[0, j].set_text_props(color="white", fontweight="bold")

    # Alternate row colors
    for i in range(1, len(table_data) + 1):
        color = "#ecf0f1" if i % 2 == 0 else "white"
        for j in range(2):
            table[i, j].set_facecolor(color)

    ax.set_title("Aggregate Evaluation Metrics", fontsize=13, fontweight="bold", pad=20)

    plt.tight_layout()
    path = os.path.join(output_dir, "summary_metrics_table.png")
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def main():
    output_dir = os.path.join(PROJECT_ROOT, "output")
    report_path = os.path.join(output_dir, "evaluation_report.json")

    if not os.path.exists(report_path):
        print("ERROR: No evaluation report found. Run 'python run_all_notes.py' first.")
        return

    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    print("=" * 60)
    print(" GENERATING VISUALIZATIONS FOR MÉMOIRE")
    print("=" * 60)

    print("\n1. Confusion heatmap (TP/FP/FN)...")
    generate_confusion_heatmap(report, output_dir)

    print("\n2. Precision/Recall/F1 chart...")
    generate_prf1_chart(report, output_dir)

    print("\n3. Match method distribution...")
    generate_match_method_pie(output_dir)

    print("\n4. Summary metrics table...")
    generate_summary_table(report, output_dir)

    print(f"\n{'=' * 60}")
    print(f" All figures saved to: {output_dir}/")
    print(f" Use these in Chapter 5 of the mémoire.")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
