"""Part 2: Module 3 (Negation), Module 4 (Normalization), Output (Phenopacket), Data."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pfe_engine import PFESlideBuilder, IMG_DIR, CHARTS_DIR

sb = PFESlideBuilder()

# =========================================================================
# SLIDE 1: SECTION - MODULE 3
# =========================================================================
sb.section_slide(4, "Module 3\nHybrid Validation (Negation + Rules)")

# =========================================================================
# SLIDE 2: NEGATION OVERVIEW (with negation image)
# =========================================================================
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

# =========================================================================
# SLIDE 3: NEGATION ARCHITECTURE (Chart 19)
# =========================================================================
sb.chart_slide(
    "3 Layer Hybrid Negation Architecture",
    "19_negation_architecture.png",
    "Layer 1: NegEx rules  |  Layer 2: Distance scoring  |  Layer 3: NegBERT transformer"
)

# =========================================================================
# SLIDE 4: LAYER 1 - NegEx Rules
# =========================================================================
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

# =========================================================================
# SLIDE 5: LAYER 2 - Distance Scoring
# =========================================================================
sb.content("Layer 2: Distance Based Scoring", [
    "Problem: NegEx can be too aggressive with large windows",
    "Solution: score negation confidence based on word distance",
    "How the scoring works:",
    "This layer refines the binary NegEx output into a gradient",
    "Entities close to triggers get high negation confidence",
], subs={
    2: [
        "Count words between trigger word and entity",
        "Distance 0 to 2 words: confidence = 0.95 (very likely negated)",
        "Distance 3 to 4 words: confidence = 0.80 (likely negated)",
        "Distance 5 to 6 words: confidence = 0.60 (possibly negated)",
        "Distance 7+: not considered negated",
    ],
})

# =========================================================================
# SLIDE 6: LAYER 3 - NegBERT Transformer
# =========================================================================
sb.content("Layer 3: NegBERT Transformer Verification", [
    "Final layer: use a transformer model to verify negation",
    "English model: bvanaken/clinical-assertion-negation-bert",
    "French model: MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",
    "How it works:",
    "Why 3 layers instead of just the transformer?",
], subs={
    1: [
        "Trained on clinical assertion classification (i2b2, MedNLI)",
        "Labels: present, absent, possible, conditional, associated",
    ],
    2: [
        "Multilingual NLI (Natural Language Inference) model",
        "We use it as zero shot: hypothesis = 'symptom is absent'",
    ],
    3: [
        "Takes the sentence containing the entity as input",
        "Predicts: is the entity present, absent, or uncertain?",
        "If model says absent with confidence > 0.7, override Layer 1 and 2",
    ],
    4: [
        "Layer 1 (NegEx) is fast and catches obvious negations",
        "Layer 2 (distance) adds confidence granularity",
        "Layer 3 (transformer) catches complex negations NegEx misses",
        "Example: 'The family history of diabetes does not apply here'",
        "NegEx would miss this, but NegBERT understands the context",
    ],
})

# =========================================================================
# SLIDE 7: OTHER MODULE 3 COMPONENTS
# =========================================================================
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

# =========================================================================
# SLIDE 8: NEGATION STATISTICS (Chart 10)
# =========================================================================
sb.chart_slide(
    "Negation Detection: Statistics Across Corpora",
    "10_negation_stats.png",
    "Shows how many entities were negated in each corpus"
)

# =========================================================================
# SLIDE 9: SECTION - MODULE 4
# =========================================================================
sb.section_slide(5, "Module 4\nOntological Normalization")

# =========================================================================
# SLIDE 10: NORMALIZATION OVERVIEW (with cascade image)
# =========================================================================
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

# =========================================================================
# SLIDE 11: HPO ONTOLOGY (with HPO tree image)
# =========================================================================
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

# =========================================================================
# SLIDE 12: SAPBERT (with SapBERT matching image)
# =========================================================================
sb.split_text_img(
    "SapBERT: AI Powered Semantic Matching",
    [
        "When exact match fails, we use SapBERT",
        "SapBERT = Self Alignment Pre training for BERT",
        "Published by Cambridge University (Liu et al. 2021)",
        "How it works:",
        "  1. Convert entity text to a vector (768 dimensions)",
        "  2. Convert all HPO terms to vectors (pre computed)",
        "  3. Compute cosine similarity between them",
        "  4. Return the HPO term with highest similarity",
        "  5. Threshold: similarity must be above 0.70",
        "This catches variations NER missed:",
        "  'fits' matches 'Seizure' (HP:0001250)",
    ],
    os.path.join(IMG_DIR, "sapbert_matching.png"),
)

# =========================================================================
# SLIDE 13: NORMALIZATION CASCADE (Chart 05)
# =========================================================================
sb.chart_slide(
    "Normalization Cascade Distribution",
    "05_normalization_cascade.png",
    "How entities are resolved: abbreviation, French HPO, exact match, SapBERT, or unmatched"
)

# =========================================================================
# SLIDE 14: ORDO DISEASE MATCHING
# =========================================================================
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

# =========================================================================
# SLIDE 15: SECTION - OUTPUT
# =========================================================================
sb.section_slide(6, "System Output\nPhenopacket (ISO 4454:2022)")

# =========================================================================
# SLIDE 16: PHENOPACKET (with phenopacket image)
# =========================================================================
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

# =========================================================================
# SLIDE 17: PHENOPACKET COMPLIANCE (Chart 18)
# =========================================================================
sb.chart_slide(
    "Phenopacket ISO Compliance Check",
    "18_phenopacket_compliance.png",
    "All required fields present and properly formatted across both pipelines"
)

# =========================================================================
# SLIDE 18: SECTION - DATA
# =========================================================================
sb.section_slide(7, "Clinical Data Sources\nCHU Oran + PubMed + GSC")

# =========================================================================
# SLIDE 19: CHU REPORTS (with CHU image)
# =========================================================================
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

# =========================================================================
# SLIDE 20: ENGLISH CORPORA
# =========================================================================
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

# =========================================================================
# SLIDE 21: CROSS LINGUAL EXPERIMENT
# =========================================================================
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

# =========================================================================
# SAVE
# =========================================================================
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(out_dir, exist_ok=True)
sb.save(os.path.join(out_dir, "PFE_Presentation_Part2.pptx"))
print(f"Part 2 complete: {sb.num} slides")
