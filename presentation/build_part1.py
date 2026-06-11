"""Part 1: Title, Pipeline Architecture, Module 1 and Module 2 (NER Deep Dive)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pfe_engine import PFESlideBuilder, IMG_DIR, CHARTS_DIR

sb = PFESlideBuilder()

# =========================================================================
# SLIDE 1: TITLE
# =========================================================================
sb.title_slide(
    title="Hybrid Clinical Pre-Analysis Module\nfor Rare Disease Diagnosis Support",
    subtitle="Supervisor Meeting: Technical Progress Update",
    authors="Ourred Islem Charaf Eddine  |  Ouddane Youcef Fahed",
    supervisors="Supervisors: Dr. Mezrar Samiha  |  Pr. Keskes Nabil"
)

# =========================================================================
# SLIDE 2: AGENDA
# =========================================================================
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

# =========================================================================
# SLIDE 3: SECTION - SYSTEM ARCHITECTURE
# =========================================================================
sb.section_slide(1, "System Architecture\nComplete Pipeline Overview")

# =========================================================================
# SLIDE 4: PIPELINE ARCHITECTURE (Chart 01)
# =========================================================================
sb.chart_slide(
    "Complete Pipeline Architecture (4 Modules)",
    "01_pipeline_architecture.png",
    "Input: Raw clinical text  |  Output: Structured Phenopacket (JSON)"
)

# =========================================================================
# SLIDE 5: WHAT THE PIPELINE DOES (with unstructured vs structured image)
# =========================================================================
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

# =========================================================================
# SLIDE 6: BILINGUAL ARCHITECTURE (with generated image)
# =========================================================================
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

# =========================================================================
# SLIDE 7: SECTION - MODULE 1
# =========================================================================
sb.section_slide(2, "Module 1\nPreprocessing and De-identification")

# =========================================================================
# SLIDE 8: MODULE 1 DETAILS
# =========================================================================
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

# =========================================================================
# SLIDE 9: SECTION - MODULE 2
# =========================================================================
sb.section_slide(3, "Module 2\nSemantic Extraction (NER)")

# =========================================================================
# SLIDE 10: NER OVERVIEW (with NER highlighting image)
# =========================================================================
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

# =========================================================================
# SLIDE 11: NER ENSEMBLE ARCHITECTURE (Chart 02)
# =========================================================================
sb.chart_slide(
    "English NER: 3 Model Ensemble Architecture",
    "02_ner_ensemble_architecture.png",
    "DeBERTa v3 + d4data + ClinicalBERT results are merged and deduplicated"
)

# =========================================================================
# SLIDE 12: MODEL 1 - DeBERTa-v3
# =========================================================================
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

# =========================================================================
# SLIDE 13: MODEL 2 - d4data
# =========================================================================
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

# =========================================================================
# SLIDE 14: MODEL 3 - ClinicalBERT NER
# =========================================================================
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

# =========================================================================
# SLIDE 15: ENSEMBLE DEDUPLICATION
# =========================================================================
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

# =========================================================================
# SLIDE 16: FRENCH NER - CamemBERT-bio GLiNER
# =========================================================================
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

# =========================================================================
# SLIDE 17: MODEL CONTRIBUTION (Chart 17)
# =========================================================================
sb.chart_slide(
    "Model Contribution: Which Model Finds What?",
    "17_model_contribution.png",
    "Each model contributes unique entities that others miss"
)

# =========================================================================
# SAVE
# =========================================================================
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(out_dir, exist_ok=True)
sb.save(os.path.join(out_dir, "PFE_Presentation_Part1.pptx"))
print(f"Part 1 complete: {sb.num} slides")
