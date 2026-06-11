"""Part 4: Remaining Charts, Cross-Lingual Analysis, Literature, Conclusion."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pfe_engine import PFESlideBuilder, IMG_DIR, CHARTS_DIR

sb = PFESlideBuilder()

# =========================================================================
# SLIDE 1: SECTION - DETAILED ANALYSIS
# =========================================================================
sb.section_slide(10, "Detailed Analysis\nNegation, Timing, and Quality")

# =========================================================================
# SLIDE 2: NEGATION STATS (Chart 10)
# =========================================================================
sb.chart_slide(
    "Negation Detection Statistics",
    "10_negation_stats.png",
    "Number of negated entities detected per corpus  |  3-layer hybrid catches what rules miss"
)

# =========================================================================
# SLIDE 3: PROCESSING TIME (Chart 11)
# =========================================================================
sb.chart_slide(
    "Processing Efficiency: Time Per Report",
    "11_processing_time.png",
    "French pipeline takes longer due to GLiNER zero-shot  |  English ensemble is faster per entity"
)

# =========================================================================
# SLIDE 4: SCORE RADAR (Chart 08)
# =========================================================================
sb.chart_slide(
    "S.C.O.R.E. Quality Assessment (5 Dimensions)",
    "08_score_radar.png",
    "Both pipelines score 19/25  |  Strongest in Coverage and Ontological Fidelity"
)

# =========================================================================
# SLIDE 5: PHENOPACKET COMPLIANCE (Chart 18)
# =========================================================================
sb.chart_slide(
    "Phenopacket ISO 4454:2022 Compliance",
    "18_phenopacket_compliance.png",
    "All required fields present  |  Output compatible with Exomiser and LIRICAL"
)

# =========================================================================
# SLIDE 6: SECTION - CROSS LINGUAL
# =========================================================================
sb.section_slide(11, "Cross Lingual Analysis\nFrench vs English")

# =========================================================================
# SLIDE 7: CROSS LINGUAL GAP (Chart 14)
# =========================================================================
sb.chart_slide(
    "Cross Lingual Performance Gap",
    "14_cross_lingual_gap.png",
    "French pipeline outperforms English on same CHU reports  |  Gap analysis by metric"
)

# =========================================================================
# SLIDE 8: WHY FRENCH IS BETTER
# =========================================================================
sb.content("Why French Pipeline Outperforms English", [
    "Key finding: French F1 = 73.8% vs English F1 = 37.4% on CHU",
    "Root cause analysis:",
    "Technical explanation:",
    "This is actually a positive result for our thesis:",
], subs={
    1: [
        "French GLiNER is more precise (fewer false positives)",
        "English 3 model ensemble has very high recall but low precision",
        "English models extract too many entities (over extraction)",
        "Translation from French to English introduces noise",
    ],
    2: [
        "GLiNER zero shot with threshold 0.4 acts as a natural filter",
        "DeBERTa + d4data + ClinicalBERT combined = aggressive extraction",
        "More models = more entities found = more false positives",
        "The ensemble trades precision for recall by design",
    ],
    3: [
        "Shows our French pipeline is well suited for French clinical text",
        "Validates the choice of CamemBERT bio for French NER",
        "Demonstrates that native language processing beats translation",
        "Supports the bilingual architecture decision",
    ],
})

# =========================================================================
# SLIDE 9: SECTION - LITERATURE
# =========================================================================
sb.section_slide(12, "Comparison with Literature\nHow We Compare to Others")

# =========================================================================
# SLIDE 10: LITERATURE COMPARISON (Chart 13)
# =========================================================================
sb.chart_slide(
    "Comparison with Published Systems",
    "13_literature_comparison.png",
    "Our French pipeline competitive with state of the art  |  Key advantage: bilingual + integrated"
)

# =========================================================================
# SLIDE 11: OUR CONTRIBUTIONS vs LITERATURE
# =========================================================================
sb.content("What Makes Our System Unique", [
    "1. First bilingual pipeline (French + English) for rare disease pre-analysis",
    "2. First to combine GLiNER zero shot with transformer ensemble",
    "3. 3 layer hybrid negation (NegEx + distance + NegBERT)",
    "4. Complete normalization cascade (6 steps, rules + AI)",
    "5. Phenopacket ISO output (compatible with diagnostic tools)",
    "6. Evaluated on real hospital data (CHU Oran)",
    "Compared to existing work:",
], subs={
    6: [
        "Sun and Tao 2023: NER + NEN but English only, no negation",
        "Dong et al 2023: UMLS/ORDO linking but no integrated pipeline",
        "Borisova et al 2021: Hybrid but for Bulgarian only, no phenotyping",
        "Kim et al 2021: Hybrid NER but for clinical trials only",
        "Our system: first to integrate ALL components end to end",
    ],
})

# =========================================================================
# SLIDE 12: SECTION - SUMMARY
# =========================================================================
sb.section_slide(13, "Summary Dashboard\nAll Results at a Glance")

# =========================================================================
# SLIDE 13: SUMMARY DASHBOARD (Chart 20)
# =========================================================================
sb.chart_slide(
    "System Performance Summary Dashboard",
    "20_summary_dashboard.png",
    "Complete overview: F1, ORDO accuracy, normalization, timing, features across all corpora"
)

# =========================================================================
# SLIDE 14: KEY FINDINGS
# =========================================================================
sb.content("Key Findings Summary", [
    "French Pipeline Performance:",
    "English Pipeline Performance:",
    "System Capabilities:",
    "Evaluation Coverage:",
], subs={
    0: [
        "HPO Macro F1 = 73.8% (best result)",
        "ORDO Top 3 Accuracy = 87.5%",
        "Normalization Coverage = 35%",
        "S.C.O.R.E. = 19/25",
    ],
    1: [
        "CHU English F1 = 37.4% (precision limited by over extraction)",
        "PubMed F1 = 46.9% (better on phenotype rich text)",
        "GSC F1 = 27.0% (hardest corpus, short text)",
        "High recall across all English corpora (80%+)",
    ],
    2: [
        "Bilingual: processes French and English clinical text",
        "3 layer negation: catches complex negations",
        "6 step normalization: rules + AI cascade",
        "ISO compliant output: Phenopacket standard",
    ],
    3: [
        "108 total reports evaluated across 4 corpora",
        "8 rare diseases in CHU corpus",
        "All 8 thesis metrics computed",
        "20 publication quality charts generated",
    ],
})

# =========================================================================
# SLIDE 15: NEXT STEPS
# =========================================================================
sb.content("Next Steps and Future Work", [
    "Short term (before defense):",
    "Future improvements:",
    "Potential extensions:",
], subs={
    0: [
        "Complete the Results and Discussion chapters (Chapter 6 and 7)",
        "Run final evaluation with all corrections applied",
        "Prepare the defense presentation",
        "Write the conclusion and perspectives",
    ],
    1: [
        "Fine tune DeBERTa on clinical NER for better English precision",
        "Add more French clinical reports from other hospitals",
        "Implement confidence calibration for the ensemble",
        "Add abbreviation expansion for French medical terms",
    ],
    2: [
        "Integration with Exomiser for automated genetic diagnosis",
        "Web interface (Streamlit app already functional)",
        "Multi hospital deployment with anonymized data pipeline",
        "Support for Arabic clinical text (third language)",
    ],
})

# =========================================================================
# SLIDE 16: END
# =========================================================================
sb.end_slide(
    "Thank You",
    "Questions and Discussion"
)

# =========================================================================
# SAVE
# =========================================================================
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(out_dir, exist_ok=True)
sb.save(os.path.join(out_dir, "PFE_Presentation_Part4.pptx"))
print(f"Part 4 complete: {sb.num} slides")
