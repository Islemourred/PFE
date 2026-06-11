"""Part 3: Evaluation System, Gold Standard, Main Results (all charts)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pfe_engine import PFESlideBuilder, IMG_DIR, CHARTS_DIR

sb = PFESlideBuilder()

# =========================================================================
# SLIDE 1: SECTION - EVALUATION
# =========================================================================
sb.section_slide(8, "Evaluation System\nGold Standard and Metrics")

# =========================================================================
# SLIDE 2: GOLD STANDARD CONCEPT (with image)
# =========================================================================
sb.split_text_img(
    "What is a Gold Standard?",
    [
        "A Gold Standard = the correct answers for evaluation",
        "Like an answer key for an exam:",
        "  The gold standard has the correct HPO codes",
        "  Our pipeline produces predicted HPO codes",
        "  We compare predicted vs correct to measure quality",
        "Created by medical experts (not by our system)",
        "Each report has:",
        "  List of expected HPO phenotype codes",
        "  Expected ORDO disease code",
        "  Expected negated symptoms",
    ],
    os.path.join(IMG_DIR, "gold_standard_concept.png"),
)

# =========================================================================
# SLIDE 3: OUR 3 GOLD STANDARDS
# =========================================================================
sb.content("Our 3 Gold Standard Datasets", [
    "Gold Standard 1: CHU Oran (French)",
    "Gold Standard 2: PubMed (English)",
    "Gold Standard 3: GSC (English)",
    "Total: 78 reports with expert annotations",
], subs={
    0: [
        "30 French clinical reports from CHU Oran hospital",
        "Annotated by Dr. Tamazirt (medical expert)",
        "8 rare diseases covered: CF, SCID, Wiskott Aldrich, etc.",
        "Average 14 HPO features per report",
    ],
    1: [
        "24 English case reports from PubMed literature",
        "Pre annotated with HPO terms by original authors",
        "Rich phenotypic descriptions (avg 30 features)",
        "Covers diverse rare diseases",
    ],
    2: [
        "24 English clinical cases from OMIM database",
        "Expert curated phenotype annotations",
        "Shorter, more structured (avg 10 features)",
        "Standard benchmark in the phenotyping field",
    ],
})

# =========================================================================
# SLIDE 4: METRICS EXPLAINED (with precision/recall image)
# =========================================================================
sb.split_text_img(
    "Evaluation Metrics: Precision, Recall, F1",
    [
        "Precision = correctness of our extractions",
        "  How many of the HPO codes we found are correct?",
        "  Formula: True Positives / (True Positives + False Positives)",
        "",
        "Recall = completeness of our extractions",
        "  How many of the expected HPO codes did we find?",
        "  Formula: True Positives / (True Positives + False Negatives)",
        "",
        "F1 Score = harmonic mean of Precision and Recall",
        "  Balanced single metric: 2*P*R / (P+R)",
    ],
    os.path.join(IMG_DIR, "precision_recall_visual.png"),
)

# =========================================================================
# SLIDE 5: HPO MATCHING LOGIC
# =========================================================================
sb.content("How We Match: Semantic HPO Matching", [
    "Simple text matching is not enough for HPO evaluation",
    "Problem: 'seizures' and 'epileptic seizures' are related",
    "Our semantic matching approach:",
    "Match types (in order of strictness):",
], subs={
    2: [
        "We use the HPO ontology tree structure",
        "Two terms match if they are the same or related",
        "Parent child relationships count as partial matches",
    ],
    3: [
        "EXACT: same HPO code (e.g., HP:0001250 = HP:0001250)",
        "PARENT: predicted is parent of gold (generalization)",
        "CHILD: predicted is child of gold (specialization)",
        "SIBLING: share a common parent in the HPO tree",
        "SapBERT: semantic similarity above 0.70 threshold",
    ],
})

# =========================================================================
# SLIDE 6: ALL 8 METRICS
# =========================================================================
sb.content("Complete Evaluation Framework: 8 Metrics", [
    "1. HPO Precision / Recall / F1 (micro and macro)",
    "2. Normalization Coverage (% of entities mapped to HPO)",
    "3. Normalization Cascade Distribution (which method matched)",
    "4. ORDO Top K Accuracy (correct disease in top 1, 3, 5)",
    "5. Inconsistency and Negation Detection rates",
    "6. Phenopacket Compliance (ISO 4454 field presence)",
    "7. Processing Efficiency (seconds per report)",
    "8. S.C.O.R.E. Framework (5 dimension quality assessment)",
], subs={
    7: [
        "S = Specificity (precision of HPO terms)",
        "C = Coverage (recall of expected phenotypes)",
        "O = Ontological Fidelity (correct HPO mapping)",
        "R = Robustness (consistency across diseases)",
        "E = Efficiency (processing speed)",
    ],
})

# =========================================================================
# SLIDE 7: SECTION - RESULTS
# =========================================================================
sb.section_slide(9, "Results\nAll Performance Metrics")

# =========================================================================
# SLIDE 8: MAIN RESULT - HPO P/R/F1 (Chart 03)
# =========================================================================
sb.chart_slide(
    "Main Result: HPO Precision, Recall, F1 Score",
    "03_hpo_precision_recall_f1.png",
    "French pipeline (CHU): P=63%, R=89%, F1=74%  |  English results lower due to over-extraction"
)

# =========================================================================
# SLIDE 9: ORDO ACCURACY (Chart 04)
# =========================================================================
sb.chart_slide(
    "ORDO Disease Classification: Top K Accuracy",
    "04_ordo_disease_accuracy.png",
    "Top-3 accuracy reaches 87.5% on French CHU corpus"
)

# =========================================================================
# SLIDE 10: CROSS CORPUS COMPARISON (Chart 07)
# =========================================================================
sb.chart_slide(
    "Cross Corpus Comparison: All 4 Evaluation Conditions",
    "07_cross_corpus_comparison.png",
    "French pipeline significantly outperforms English on same CHU reports"
)

# =========================================================================
# SLIDE 11: PER DISEASE HEATMAP (Chart 06)
# =========================================================================
sb.chart_slide(
    "Per Disease HPO Performance Heatmap",
    "06_per_disease_heatmap.png",
    "SCID achieves highest F1 (81%)  |  Ataxia-Telangiectasia is most challenging (67%)"
)

# =========================================================================
# SLIDE 12: PRECISION RECALL SCATTER (Chart 12)
# =========================================================================
sb.chart_slide(
    "Precision vs Recall Trade off (with F1 Isocurves)",
    "12_precision_recall_scatter.png",
    "CHU French is in the best position (high P and R)  |  English corpora show P-R imbalance"
)

# =========================================================================
# SLIDE 13: NORMALIZATION CASCADE (Chart 05)
# =========================================================================
sb.chart_slide(
    "Normalization Cascade: How Entities Were Resolved",
    "05_normalization_cascade.png",
    "Most entities matched via exact match or SapBERT  |  French HPO dictionary helps FR pipeline"
)

# =========================================================================
# SLIDE 14: MICRO vs MACRO F1 (Chart 09)
# =========================================================================
sb.chart_slide(
    "Micro vs Macro F1: Per Entity vs Per Report Average",
    "09_micro_vs_macro_f1.png",
    "Micro = weighted by entity count  |  Macro = equal weight per report (harder metric)"
)

# =========================================================================
# SLIDE 15: NORMALIZATION COVERAGE (Chart 16)
# =========================================================================
sb.chart_slide(
    "Normalization Coverage Across Corpora",
    "16_normalization_coverage.png",
    "What percentage of extracted entities were successfully mapped to HPO codes"
)

# =========================================================================
# SLIDE 16: FEATURES PER REPORT (Chart 15)
# =========================================================================
sb.chart_slide(
    "HPO Features Extracted Per Report",
    "15_features_per_report.png",
    "English pipeline extracts more features (higher recall but lower precision)"
)

# =========================================================================
# SAVE
# =========================================================================
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(out_dir, exist_ok=True)
sb.save(os.path.join(out_dir, "PFE_Presentation_Part3.pptx"))
print(f"Part 3 complete: {sb.num} slides")
