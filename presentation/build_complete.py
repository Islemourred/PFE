"""Build the complete PFE presentation: all 4 parts merged into one PPTX."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pfe_engine import PFESlideBuilder, IMG_DIR, CHARTS_DIR

sb = PFESlideBuilder()

# ====================================================================================
# PART 1: TITLE + ARCHITECTURE + MODULE 1 + MODULE 2 (NER)
# ====================================================================================

# --- TITLE ---
sb.title_slide(
    title="Hybrid Clinical Pre-Analysis Module\nfor Rare Disease Diagnosis Support",
    subtitle="Supervisor Meeting: Technical Progress Update",
    authors="Ourred Islam Charaf Eddine  |  Ouddane Youcef Fahed",
    supervisors="Supervisors: Dr. Mezrar Samiha  |  Dr. Keskes Nabil"
)

# --- AGENDA ---
sb.content("Meeting Agenda", [
    "Pipeline Architecture Overview (4 modules end to end)",
    "Module 1: Preprocessing and PHI Removal",
    "Module 2: Bilingual NER Extraction (all 7 models explained)",
    "Module 3: Hybrid Negation Detection (NegEx + NegBERT)",
    "Module 4: Ontological Normalization Cascade",
    "Output: Phenopacket (ISO 4454:2022)",
    "Data: CHU Oran Reports and English Corpora",
    "Evaluation System: Gold Standard and All Metrics",
    "Results: All 20 charts and performance analysis",
    "Cross Lingual Analysis: French vs English",
])

# --- SECTION: ARCHITECTURE ---
sb.section_slide(1, "System Architecture\nComplete Pipeline Overview")

sb.chart_slide(
    "Complete Pipeline Architecture (4 Modules)",
    "01_pipeline_architecture.png",
    "Input: Raw clinical text  |  Output: Structured Phenopacket (JSON)"
)

sb.split_text_img(
    "What Our System Does",
    [
        "Takes raw unstructured clinical text as input",
        "Automatically detects the language (French or English)",
        "Removes personal health information (PHI)",
        "Extracts medical entities (symptoms, diseases, treatments)",
        "Detects negated symptoms (not present vs present)",
        "Normalizes everything to standard medical codes",
        "Maps symptoms to HPO ontology terms",
        "Matches patient profile to rare diseases (ORDO)",
        "Outputs a structured Phenopacket (ISO standard)",
    ],
    os.path.join(IMG_DIR, "unstructured_structured.png"),
)

sb.split_text_img(
    "Bilingual Architecture: French + English",
    [
        "System handles both French and English clinical text",
        "Language is auto detected using langdetect library",
        "French path: CamemBERT bio GLiNER (zero shot NER)",
        "English path: 3 model ensemble (DeBERTa + d4data + ClinicalBERT)",
        "Both paths share the same normalization pipeline",
        "Both paths share the same negation detection",
        "Both paths produce the same Phenopacket output",
        "This is a key contribution: no other system does both",
    ],
    os.path.join(IMG_DIR, "french_english_pipeline.png"),
)

# --- SECTION: MODULE 1 ---
sb.section_slide(2, "Module 1\nPreprocessing and De-identification")

sb.content("Module 1: Preprocessing and PHI Removal", [
    "Step 1: Language Detection using langdetect library",
    "Step 2: PHI (Protected Health Information) removal",
    "Step 3: Text cleaning and normalization",
], subs={
    0: [
        "Supports French (fr) and English (en)",
        "Confidence based detection with fallback rules",
    ],
    1: [
        "Removes patient names, dates of birth, addresses",
        "Removes phone numbers, medical record numbers",
        "Uses regex patterns adapted for French and English formats",
        "Replaced with placeholder tags: [NAME], [DATE], [PHONE]",
    ],
    2: [
        "Normalizes whitespace and special characters",
        "Preserves medical abbreviations and numeric values",
        "Segments text into sentences using pysbd library",
    ],
})

# --- SECTION: MODULE 2 ---
sb.section_slide(3, "Module 2\nSemantic Extraction (NER)")

sb.split_text_img(
    "Module 2: Named Entity Recognition (NER)",
    [
        "NER = finding medical terms in text automatically",
        "We extract 3 categories of entities:",
        "  PROBLEM: diseases, symptoms, signs",
        "  TREATMENT: medications, procedures, therapies",
        "  TEST: lab tests, diagnostic procedures",
        "Each entity gets: text, position, confidence score",
        "Different models for French vs English text",
    ],
    os.path.join(IMG_DIR, "ner_highlighting.png"),
)

sb.chart_slide(
    "English NER: 3 Model Ensemble Architecture",
    "02_ner_ensemble.png",
    "DeBERTa v3 + d4data + ClinicalBERT results are merged and deduplicated"
)

# Model 1: DeBERTa
sb.content("Model 1: Helios9/BioMed_NER (DeBERTa v3)", [
    "Architecture: DeBERTa v3 base (disentangled attention mechanism)",
    "Training: Fine tuned on biomedical NER datasets (2024)",
    "Entity types it detects:",
    "Why we chose it: Best NER architecture available in 2024",
    "Label mapping in our code:",
], subs={
    2: [
        "Disease_disorder and Sign_symptom mapped to PROBLEM",
        "Medication and Therapeutic_procedure mapped to TREATMENT",
        "Diagnostic_procedure, Lab_value, Biological_structure mapped to TEST",
    ],
    3: [
        "Disentangled attention separates content and position representations",
        "Better at understanding medical context than standard BERT",
        "SOTA performance on clinical NER benchmarks",
    ],
    4: [
        "aggregation_strategy = simple (merges BIO subword tokens)",
        "Chunks text at 480 tokens with sentence boundary splitting",
    ],
})

# Model 2: d4data
sb.content("Model 2: d4data/biomedical-ner-all", [
    "Architecture: Standard BERT base",
    "Training: Fine tuned on 8 biomedical NER datasets combined",
    "Entity types it detects:",
    "Why we added it to the ensemble:",
    "Label mapping in our code:",
], subs={
    2: [
        "Disease mapped to PROBLEM",
        "Chemical mapped to TREATMENT",
        "Gene and Protein mapped to TEST",
        "Species, Cell_line, Cell_type, DNA, RNA are ignored",
    ],
    3: [
        "Trained on 8 different datasets = broad coverage",
        "Catches biomedical entities that DeBERTa misses",
        "Especially good at chemical and gene names",
    ],
    4: [
        "aggregation_strategy = first (uses first subword label)",
        "Different strategy than DeBERTa for complementary results",
    ],
})

# Model 3: ClinicalBERT
sb.content("Model 3: samrawal/bert-base-uncased_clinical-ner", [
    "Architecture: BERT base uncased (ClinicalBERT variant)",
    "Training: Fine tuned on i2b2 2010 clinical NER dataset",
    "Entity types: direct mapping (no conversion needed)",
    "Why we added it as third model:",
    "This completes our thesis proposal from the memoire:",
], subs={
    2: [
        "problem mapped to PROBLEM (diseases, symptoms)",
        "treatment mapped to TREATMENT (medications, procedures)",
        "test mapped to TEST (lab tests, exams)",
    ],
    3: [
        "Pre trained on MIMIC III clinical notes (real hospital data)",
        "Understands clinical writing style: abbreviations, shorthand",
        "i2b2 is the gold standard for clinical NER evaluation",
    ],
    4: [
        "Dr. Mezrar proposed ClinicalBERT in the thesis topic",
        "This is the actual ClinicalBERT fine tuned for NER",
        "Validates the thesis proposal with a concrete implementation",
    ],
})

# Ensemble dedup
sb.content("Ensemble: How 3 Models Work Together", [
    "Step 1: Run all 3 models independently on the same text",
    "Step 2: Merge all results into a single list per category",
    "Step 3: Fragment filtering (remove NER artifacts)",
    "Step 4: Deduplication (keep best version of each entity)",
    "Result: comprehensive entity list with maximum coverage",
], subs={
    2: [
        "Subword fragments like 'ille' or 'cystis' are removed",
        "Short tokens (3 chars or less) filtered unless in known terms list",
        "Known short terms preserved: rash, pain, gait, coma, edema etc.",
    ],
    3: [
        "Group by lowercase text, keep longest text version",
        "Keep highest confidence score across models",
        "Each entity tagged with its source model for traceability",
    ],
})

# French NER
sb.content("French NER: CamemBERT bio GLiNER (Zero Shot)", [
    "Model: almanach/camembert-bio-gliner-v0.1",
    "Architecture: CamemBERT bio + GLiNER zero shot framework",
    "What zero shot means for us:",
    "French clinical labels we defined:",
    "Technical details:",
], subs={
    2: [
        "No fine tuning needed on French clinical data",
        "We define the entity types at inference time",
        "Model generalizes from its biomedical training",
        "Published by ALMAnaCH team (INRIA, France) in 2024",
    ],
    3: [
        "maladie (disease) mapped to PROBLEM",
        "symptome (symptom) mapped to PROBLEM",
        "traitement (treatment) mapped to TREATMENT",
        "medicament (drug) mapped to TREATMENT",
        "examen medical (medical test) mapped to TEST",
    ],
    4: [
        "threshold = 0.4 (confidence cutoff for predictions)",
        "flat_ner = True (no nested entity extraction)",
        "Chunks text at 300 words using sentence boundaries",
    ],
})

sb.chart_slide(
    "Model Contribution: Which Model Finds What?",
    "17_model_contribution.png",
    "Each model contributes unique entities that others miss"
)

# ====================================================================================
# PART 2: MODULE 3 + MODULE 4 + OUTPUT + DATA
# ====================================================================================

# --- SECTION: MODULE 3 ---
sb.section_slide(4, "Module 3\nHybrid Validation (Negation + Rules)")

sb.split_text_img(
    "Module 3: Why Negation Detection Matters",
    [
        "Clinical text often says what is NOT present",
        "Example: 'Patient denies fever, no cough observed'",
        "Without negation detection, our system would say:",
        "  fever = PRESENT (WRONG!)",
        "  cough = PRESENT (WRONG!)",
        "With negation detection, our system correctly says:",
        "  fever = NEGATED (correct)",
        "  cough = NEGATED (correct)",
        "This is critical for accurate patient profiling",
    ],
    os.path.join(IMG_DIR, "negation_detection.png"),
)

sb.chart_slide(
    "3 Layer Hybrid Negation Architecture",
    "19_negation_architecture.png",
    "Layer 1: NegEx rules  |  Layer 2: Distance scoring  |  Layer 3: NegBERT transformer"
)

sb.content("Layer 1: NegEx Rule Based Detection", [
    "NegEx is a classic algorithm for clinical negation (Chapman 2001)",
    "How it works: look for trigger words near entities",
    "English triggers (35+ patterns):",
    "French triggers (20+ patterns):",
    "Window: checks 6 words before and after the entity",
    "If trigger found within window, mark entity as negated",
], subs={
    2: [
        "no, not, without, denies, denied, absence of, negative for",
        "never, none, rules out, ruled out, no evidence of, free of",
        "no sign of, no signs of, did not, does not, has not",
    ],
    3: [
        "pas de, sans, aucun, aucune, nie, absence de, exclut",
        "pas d', ni, negatif, normal, pas retrouve, non retrouve",
    ],
})

sb.content("Layer 2 and 3: Distance + NegBERT Verification", [
    "Layer 2: Distance Based Scoring",
    "Layer 3: NegBERT Transformer Verification",
    "Why 3 layers instead of just the transformer?",
], subs={
    0: [
        "Count words between trigger and entity",
        "0 to 2 words: confidence = 0.95 (very likely negated)",
        "3 to 4 words: confidence = 0.80 (likely negated)",
        "5 to 6 words: confidence = 0.60 (possibly negated)",
    ],
    1: [
        "EN: bvanaken/clinical-assertion-negation-bert (i2b2 trained)",
        "FR: MoritzLaurer/mDeBERTa-v3-base-mnli-xnli (NLI zero shot)",
        "Takes sentence + entity, predicts: present / absent / possible",
        "Override Layer 1 and 2 if transformer confidence > 0.7",
    ],
    2: [
        "Layer 1 (rules) is fast and catches obvious negations",
        "Layer 2 (distance) adds confidence granularity",
        "Layer 3 (transformer) catches complex negations rules miss",
        "Example: 'family history of diabetes does not apply here'",
    ],
})

sb.content("Module 3: Other Validation Components", [
    "3.2 Temporal Consistency Checking:",
    "3.3 Numeric Phenotype Extraction:",
    "3.4 Inconsistency Detection:",
], subs={
    0: [
        "Detects temporal expressions: 'since birth', '3 months ago'",
        "Flags future dates or impossible timelines",
        "Helps build a clinical timeline for the patient",
    ],
    1: [
        "Extracts numeric values: weight, height, blood counts",
        "Converts to HPO terms: 'weight 2.1 kg' becomes Decreased body weight",
        "Uses clinical reference ranges to detect abnormal values",
    ],
    2: [
        "Checks for logical contradictions between entities",
        "Example: cannot have both 'hypertension' and 'hypotension'",
        "Flags age and sex inconsistencies with extracted data",
    ],
})

# --- SECTION: MODULE 4 ---
sb.section_slide(5, "Module 4\nOntological Normalization")

sb.split_text_img(
    "Module 4: From Text to Standardized Medical Codes",
    [
        "Goal: convert extracted text into standard codes",
        "Example: 'seizures' must become HP:0001250",
        "Example: 'SCID' must become ORPHA:183660",
        "We use a 6 step normalization cascade:",
        "  1. Abbreviation expansion (rules)",
        "  2. French HPO dictionary (rules, FR only)",
        "  3. Exact match against HPO labels (rules)",
        "  4. SapBERT semantic similarity (AI)",
        "  5. UMLS CUI cross reference (lookup)",
        "  6. ORDO disease matching (profile)",
    ],
    os.path.join(IMG_DIR, "normalization_cascade.png"),
)

sb.split_text_img(
    "HPO: Human Phenotype Ontology (16,000+ terms)",
    [
        "HPO is the gold standard ontology for phenotypes",
        "Organized as a tree (Directed Acyclic Graph)",
        "Root: Phenotypic Abnormality (HP:0000118)",
        "Each term has:",
        "  A unique ID (HP:0001250 = Seizure)",
        "  A label (human readable name)",
        "  Synonyms (alternative names)",
        "  Parent/child relationships",
        "We parse the hp.owl file (OWL format)",
        "Extract 16,000+ terms with all synonyms",
    ],
    os.path.join(IMG_DIR, "hpo_ontology_tree.png"),
)

sb.split_text_img(
    "SapBERT: AI Powered Semantic Matching",
    [
        "When exact match fails, we use SapBERT",
        "SapBERT = Self Alignment Pre training for BERT",
        "Published by Cambridge University (Liu et al 2021)",
        "How it works:",
        "  1. Convert entity text to a vector (768 dimensions)",
        "  2. Convert all HPO terms to vectors (pre computed)",
        "  3. Compute cosine similarity between them",
        "  4. Return the HPO term with highest similarity",
        "  5. Threshold: similarity must be above 0.70",
        "This catches variations NER missed",
    ],
    os.path.join(IMG_DIR, "sapbert_matching.png"),
)

sb.content("ORDO: Disease Profile Matching", [
    "After normalizing all symptoms to HPO codes, we match to diseases",
    "ORDO = Orphanet Rare Disease Ontology (6000+ diseases)",
    "Each ORDO disease has a list of associated HPO phenotypes",
    "Our matching algorithm:",
    "Output: ranked list of candidate diseases with scores",
], subs={
    3: [
        "1. Collect all HPO terms found in the patient report",
        "2. For each ORDO disease, count how many HPO terms overlap",
        "3. Score = number of matches / total phenotypes in disease profile",
        "4. Rank diseases by overlap score",
        "5. Return top K candidates (we use K = 3 in evaluation)",
    ],
})

# --- SECTION: OUTPUT ---
sb.section_slide(6, "System Output\nPhenopacket (ISO 4454:2022)")

sb.split_text_img(
    "Output: GA4GH Phenopacket Standard",
    [
        "Final output follows the Phenopacket standard",
        "Developed by Global Alliance for Genomics and Health",
        "Published as ISO 4454:2022",
        "Structure of our output JSON:",
        "  id: unique identifier for this analysis",
        "  subject: patient demographics (age, sex)",
        "  phenotypicFeatures: list of HPO terms with status",
        "  diseases: ORDO candidate diseases with scores",
        "  metaData: pipeline version, models used, timestamp",
        "This output is compatible with Exomiser and LIRICAL",
    ],
    os.path.join(IMG_DIR, "phenopacket_output.png"),
)

# --- SECTION: DATA ---
sb.section_slide(7, "Clinical Data Sources\nCHU Oran + PubMed + GSC")

sb.split_text_img(
    "CHU Oran: 30 French Clinical Reports",
    [
        "Source: CHU Oran hospital (real patient records)",
        "30 clinical reports covering 8 rare diseases:",
        "  Cystic Fibrosis, SCID, Wiskott Aldrich",
        "  Agammaglobulinemia, Ataxia Telangiectasia",
        "  MHC Class II Deficiency, SMA, Hyper IgE",
        "Reports are in French (native clinical language)",
        "Average length: 300 to 500 words per report",
        "Gold standard: annotated by Dr. Tamazirt",
        "This is our primary evaluation corpus",
    ],
    os.path.join(IMG_DIR, "chu_hospital_reports.png"),
)

sb.two_column(
    "English Evaluation Corpora",
    [
        "PubMed Case Reports:",
        "24 published rare disease cases",
        "From peer reviewed medical journals",
        "Rich phenotypic descriptions",
        "Average 30 HPO features per report",
        "Pre annotated with HPO terms",
        "Diverse disease coverage",
    ],
    [
        "GSC (Gold Standard Corpus):",
        "24 clinical case studies",
        "From OMIM database entries",
        "Shorter, more structured text",
        "Average 10 HPO features per report",
        "Expert curated phenotype annotations",
        "Benchmark for phenotype extraction",
    ],
    left_title="PubMed Corpus (24 reports)",
    right_title="GSC Corpus (24 reports)",
)

sb.content("Cross Lingual Experiment: CHU Translated", [
    "We also translated CHU French reports to English",
    "Purpose: compare same reports on both pipelines",
    "Process:",
    "This gives us 4 evaluation conditions:",
], subs={
    2: [
        "Used professional medical translation (FR to EN)",
        "Preserved clinical terminology and structure",
        "Ran English pipeline on translated reports",
        "Compared results with French pipeline on originals",
    ],
    3: [
        "1. CHU French (30 reports on French pipeline) = PRIMARY",
        "2. CHU English (30 reports on English pipeline) = TRANSLATED",
        "3. PubMed English (24 reports on English pipeline) = AUXILIARY",
        "4. GSC English (24 reports on English pipeline) = AUXILIARY",
    ],
})

# ====================================================================================
# PART 3: EVALUATION SYSTEM + RESULTS
# ====================================================================================

sb.section_slide(8, "Evaluation System\nGold Standard and Metrics")

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

sb.split_text_img(
    "Evaluation Metrics: Precision, Recall, F1",
    [
        "Precision = correctness of our extractions",
        "  How many of the HPO codes we found are correct?",
        "  Formula: TP / (TP + FP)",
        "",
        "Recall = completeness of our extractions",
        "  How many of the expected HPO codes did we find?",
        "  Formula: TP / (TP + FN)",
        "",
        "F1 Score = harmonic mean of Precision and Recall",
        "  Balanced single metric: 2*P*R / (P+R)",
    ],
    os.path.join(IMG_DIR, "precision_recall_visual.png"),
)

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
        "S = Specificity, C = Coverage, O = Ontological Fidelity",
        "R = Robustness, E = Efficiency",
    ],
})

# --- RESULTS ---
sb.section_slide(9, "Results\nAll Performance Metrics")

sb.chart_slide("Main Result: HPO Precision, Recall, F1 Score",
    "03_hpo_precision_recall_f1.png",
    "French pipeline (CHU): P=63%, R=89%, F1=74%  |  English results lower due to over-extraction")

sb.chart_slide("ORDO Disease Classification: Top K Accuracy",
    "04_ordo_disease_accuracy.png",
    "Top-3 accuracy reaches 87.5% on French CHU corpus")

sb.chart_slide("Cross Corpus Comparison: All 4 Evaluation Conditions",
    "07_cross_corpus_comparison.png",
    "French pipeline significantly outperforms English on same CHU reports")

sb.chart_slide("Per Disease HPO Performance Heatmap",
    "06_per_disease_heatmap.png",
    "SCID achieves highest F1 (81%)  |  Ataxia-Telangiectasia is most challenging (67%)")

sb.chart_slide("Precision vs Recall Trade off (with F1 Isocurves)",
    "12_precision_recall_scatter.png",
    "CHU French is in the best position (high P and R)  |  English corpora show P-R imbalance")

sb.chart_slide("Normalization Cascade: How Entities Were Resolved",
    "05_normalization_cascade.png",
    "Most entities matched via exact match or SapBERT  |  French HPO dictionary helps FR pipeline")

sb.chart_slide("Micro vs Macro F1: Per Entity vs Per Report Average",
    "09_micro_vs_macro.png",
    "Micro = weighted by entity count  |  Macro = equal weight per report")

sb.chart_slide("Normalization Coverage Across Corpora",
    "16_normalization_coverage.png",
    "What percentage of extracted entities were successfully mapped to HPO codes")

sb.chart_slide("HPO Features Extracted Per Report",
    "15_features_per_report.png",
    "English pipeline extracts more features (higher recall but lower precision)")

# ====================================================================================
# PART 4: ANALYSIS + CROSS-LINGUAL + LITERATURE + CONCLUSION
# ====================================================================================

sb.section_slide(10, "Detailed Analysis\nNegation, Timing, and Quality")

sb.chart_slide("Negation Detection Statistics",
    "10_negation_statistics.png",
    "Number of negated entities detected per corpus  |  3-layer hybrid catches what rules miss")

sb.chart_slide("Processing Efficiency: Time Per Report",
    "11_processing_time.png",
    "French pipeline takes longer due to GLiNER zero-shot  |  English ensemble is faster per entity")

sb.chart_slide("S.C.O.R.E. Quality Assessment (5 Dimensions)",
    "08_score_radar.png",
    "Both pipelines score 19/25  |  Strongest in Coverage and Ontological Fidelity")

sb.chart_slide("Phenopacket ISO 4454:2022 Compliance",
    "18_phenopacket_compliance.png",
    "All required fields present  |  Output compatible with Exomiser and LIRICAL")

# --- CROSS LINGUAL ---
sb.section_slide(11, "Cross Lingual Analysis\nFrench vs English")

sb.chart_slide("Cross Lingual Performance Gap",
    "14_cross_lingual_gap.png",
    "French pipeline outperforms English on same CHU reports  |  Gap analysis by metric")

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
    ],
    3: [
        "Shows our French pipeline is well suited for French clinical text",
        "Validates the choice of CamemBERT bio for French NER",
        "Demonstrates that native language processing beats translation",
    ],
})

# --- LITERATURE ---
sb.section_slide(12, "Comparison with Literature\nHow We Compare to Others")

sb.chart_slide("Comparison with Published Systems",
    "13_literature_comparison.png",
    "Our French pipeline competitive with state of the art  |  Key advantage: bilingual + integrated")

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

# --- SUMMARY ---
sb.section_slide(13, "Summary Dashboard\nAll Results at a Glance")

sb.chart_slide("System Performance Summary Dashboard",
    "20_summary_dashboard.png",
    "Complete overview: F1, ORDO accuracy, normalization, timing, features across all corpora")

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

sb.content("Next Steps and Future Work", [
    "Short term (before defense):",
    "Future improvements:",
    "Potential extensions:",
], subs={
    0: [
        "Complete the Results and Discussion chapters (Chapter 6 and 7)",
        "Run final evaluation with all corrections applied",
        "Prepare the defense presentation",
    ],
    1: [
        "Fine tune DeBERTa on clinical NER for better English precision",
        "Add more French clinical reports from other hospitals",
        "Implement confidence calibration for the ensemble",
    ],
    2: [
        "Integration with Exomiser for automated genetic diagnosis",
        "Web interface (Streamlit app already functional)",
        "Multi hospital deployment with anonymized data pipeline",
    ],
})

sb.end_slide("Thank You", "Questions and Discussion")

# =========================================================================
# SAVE COMPLETE PRESENTATION
# =========================================================================
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(out_dir, exist_ok=True)
sb.save(os.path.join(out_dir, "PFE_Supervisor_Meeting_Complete.pptx"))
print(f"\nCOMPLETE PRESENTATION: {sb.num} slides total")
