# Hybrid Clinical Pre-Analysis Module for Rare Disease Diagnosis

> **Final Year Project** — ESI Sidi Bel Abbes 2025/2026  
> Ouddane Youcef Fahed & Ourred Islam Charaf Eddine  
> Supervised by: Dr. Mezrar Samiha & Pr. Keskes Nabil

## Overview

A hybrid **neuro-symbolic bilingual** (French/English) pipeline for automated pre-analysis of clinical notes, designed to assist in rare disease diagnosis. The system combines **8 specialized deep learning models** with deterministic rules to extract, validate, and normalize clinical data according to standardized ontologies, producing structured patient records in the **Phenopackets standard (ISO 4454:2022)**.

### Key Results

| Metric | Result | Context |
|--------|:------:|---------|
| HPO Phenotype F1 (French) | **60.0%** | 17 real hospital reports |
| HPO Recall (French) | **69.5%** | Recall-favoring design |
| ORDO Top-1 Accuracy | **88.2%** | 15/17 cases correct |
| SCORE Composite | **78.0** | "Good" quality rating |
| Processing Time (CPU) | **82 s/report** | Acceptable for batch use |
| Total Evaluation Cases | **112** | 5 datasets |

## Architecture

```
Clinical Note (FR or EN)
    |
    |-- Language Detection (langdetect)
    |
    |-- [Module 1] Preprocessing & De-identification
    |     EN: obi/deid_roberta_i2b2 (RoBERTa)
    |     FR: Jean-Baptiste/camembert-ner + regex
    |
    |-- [Module 2] Named Entity Recognition (NER)
    |     EN: Helios9/BioMed_NER (DeBERTa-v3, SOTA 2024)
    |         + d4data/biomedical-ner-all (ensemble)
    |         + ClinicalBERT (supplementary)
    |     FR: almanach/camembert-bio-gliner-v0.1 (zero-shot)
    |     Merging: IoU-based entity fusion
    |
    |-- [Module 3] Clinical Validation
    |     |-- Negation:       NegEx + bvanaken/clinical-assertion-negation-bert (EN)
    |     |                   NegEx + MoritzLaurer/mDeBERTa-v3-mnli-xnli (FR)
    |     |-- Temporal:       dateparser (200+ international formats)
    |     |-- Numeric:        Value reasoning to phenotypes (Temp, SpO2, etc.)
    |     |-- Inconsistency:  Sex/anatomy conflicts, drug interactions
    |     +-- Deduplication:  Entity dedup + confidence scoring
    |
    |-- [Module 4] Ontological Normalization (5-level cascade)
    |     Level 1: Exact label match (HPO EN + 25,054 FR labels)
    |     Level 2: Synonym match (HPO synonyms)
    |     Level 3: Fuzzy match (Levenshtein distance)
    |     Level 4: SapBERT neural similarity (cosine, adaptive threshold)
    |     Level 5: Text scan match (substring search)
    |     + Abbreviation expansion (3,911 terms)
    |     + ORDO disease matching (4,335 rare diseases)
    |
    |-- [Module 5] Output Generation
    |     |-- Phenopacket JSON (ISO 4454:2022, GA4GH)
    |     |-- Clinical synthesis report
    |     |-- SCORE quality assessment (5 dimensions)
    |     +-- Inconsistency detection report
    |
    +-- Bilingual Pipeline
          FR text --> CamemBERT-bio GLiNER (native FR NER)
                 --> Translation (FR->EN) --> EN NER ensemble
                 --> Entity fusion (FR + EN results)
```

## Project Structure

```
code/
|-- pipeline.py                         # Main orchestrator (5 modules)
|-- app.py                              # Streamlit desktop interface
|-- download_all.py                     # Download all models & data
|-- log_config.py                       # Centralized structured logging
|-- requirements.txt                    # Python dependencies
|-- run_servers.bat                     # Launch Flask + Next.js servers
|
|-- clinical_notes/                     # Test datasets
|   |-- chu_gold_v2/                    #   17 real French hospital reports (CHU Oran)
|   |-- gsc_cases/                      #   75 Gold Standard Corpus cases
|   |-- rarearena_cases/                #   10 RareArena benchmark cases
|   +-- mock_data*.py                   #   Synthetic EN + FR test notes
|
|-- data/                               # Datasets (auto-downloaded & cached)
|   |-- hpo_terms.json                  #   16K HPO terms parsed
|   |-- hpo_french_labels.json          #   25,054 FR labels (Orphanet)
|   |-- hpo_fr_en_translations.json     #   25,054 FR->EN translations
|   |-- medical_abbreviations.json      #   3,911 medical abbreviations
|   |-- ordo_profiles.json              #   4,335 ORDO disease profiles
|   +-- sapbert_hpo_index.npz           #   Pre-computed SapBERT index
|
|-- module1_preprocessing/              # Module 1: Preprocessing
|   |-- phi_remover.py                  #   PHI de-identification
|   +-- language_detector.py            #   Language detection
|
|-- module2_extraction/                 # Module 2: Semantic extraction
|   +-- clinical_ner.py                 #   Bilingual NER (DeBERTa-v3 + GLiNER)
|
|-- module3_validation/                 # Module 3: Clinical validation
|   |-- negex.py                        #   NegEx + transformers (bilingual)
|   |-- temporal.py                     #   Temporal reasoning
|   |-- numeric.py                      #   Numeric parsing to phenotypes
|   +-- inconsistency.py               #   Inconsistency detection
|
|-- module4_normalization/              # Module 4: Ontological normalization
|   |-- normalizer.py                   #   5-level cascade orchestrator
|   |-- abbreviations.py               #   Abbreviation expansion
|   |-- abbreviation_loader.py          #   Loader (3,911 terms)
|   |-- exact_matcher.py               #   Exact HPO matching
|   |-- french_hpo.py                   #   French HPO lookup
|   |-- french_hpo_loader.py            #   Orphanet loader (25K labels)
|   |-- hpo_parser.py                   #   OWL to JSON parser
|   |-- hpo_text_scanner.py             #   Level 5 text scan matcher
|   |-- sapbert_linker.py               #   SapBERT cosine similarity
|   |-- umls_mapper.py                  #   HPO <-> UMLS CUI mapping
|   |-- ordo_loader.py                  #   ORDO loader (4,335 diseases)
|   +-- ordo_matcher.py                 #   Phenotype to disease matching
|
|-- output_builder/                     # Module 5: Output generation
|   +-- phenopacket_builder.py          #   Phenopackets ISO 4454:2022
|
|-- evaluation/                         # Evaluation framework
|   |-- evaluate.py                     #   Main evaluation engine
|   |-- gold_standard_chu_v2.py         #   CHU Oran gold standard (17 FR)
|   |-- gold_standard_en.py             #   English gold standard (10 EN)
|   |-- gold_standard_gsc.py            #   GSC gold standard (75 cases)
|   |-- gold_standard_ra.py             #   RareArena gold standard (10 cases)
|   |-- hpo_matcher.py                  #   HPO semantic matching for eval
|   |-- generate_thesis_charts.py       #   Thesis figure generation
|   +-- generate_score_charts.py        #   SCORE framework charts
|
|-- web/                                # Next.js multi-user web interface
|   |-- server.py                       #   Flask REST API backend
|   |-- src/                            #   Next.js frontend
|   |   |-- app/                        #     Pages & global styles
|   |   |-- components/                 #     React components
|   |   +-- lib/                        #     Supabase client & utilities
|   +-- import_all_reports.py           #   Bulk import tool
|
|-- output/                             # Pipeline results (JSON)
+-- presentation/                       # Thesis presentation slides generator
```

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+ (for Next.js web interface)
- ~4 GB disk space (HuggingFace models)
- Internet connection (first launch only)

### Steps

```bash
# 1. Clone the project
git clone https://github.com/Islemourred/PFE.git
cd code

# 2. Create a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Download all models and data
python download_all.py

# 5. (Optional) Install Next.js web interface
cd web
npm install
cd ..

# 6. (Optional) Move HuggingFace cache if disk space is limited
set HF_HOME=D:\hf_cache        # Windows
# export HF_HOME=/data/hf_cache  # Linux
```

> **Note:** Transformer models and datasets are automatically downloaded on first launch. No manual configuration is required.

## Usage

### 1. Streamlit Desktop Interface

```bash
streamlit run app.py
```

Opens a web interface at `http://localhost:8501` for interactive clinical note analysis.

### 2. Next.js Multi-User Web Interface + Flask API

```bash
# Option A: Use the batch launcher
run_servers.bat

# Option B: Start manually
cd web
python server.py              # Flask API on port 5000
npm run dev                   # Next.js on port 3000
```

### 3. Batch Pipeline Evaluation

```bash
# Run the full evaluation on all 112 cases (5 datasets)
python -m evaluation.evaluate

# Generate thesis charts and figures
python -m evaluation.generate_thesis_charts
python -m evaluation.generate_score_charts
```

### 4. Single Note Processing (Python API)

```python
from pipeline import FullPipeline

pipeline = FullPipeline()

# French clinical note
result = pipeline.process(
    "Le patient presente une hypotonie axiale, un retard psychomoteur "
    "et des crises epileptiques depuis l'age de 3 mois.",
    note_id="NOTE_FR_001"
)

# English clinical note
result = pipeline.process(
    "Patient is a 55yo male with progressive muscle weakness, "
    "elevated CK levels, and respiratory insufficiency.",
    note_id="NOTE_EN_001"
)

# Access structured output
print(result["phenopacket"])        # ISO 4454 Phenopacket
print(result["disease_candidates"]) # Ranked ORDO diseases
print(result["score_metrics"])      # SCORE quality assessment
```

## Models Used

| Component | Model | Architecture |
|-----------|-------|:------------:|
| De-identification (EN) | `obi/deid_roberta_i2b2` | RoBERTa |
| De-identification (FR) | `Jean-Baptiste/camembert-ner` | CamemBERT |
| NER (EN, primary) | `Helios9/BioMed_NER` | **DeBERTa-v3** (SOTA 2024) |
| NER (EN, ensemble) | `d4data/biomedical-ner-all` | BERT |
| NER (FR, zero-shot) | `almanach/camembert-bio-gliner-v0.1` | CamemBERT-bio + GLiNER |
| Negation (EN) | `bvanaken/clinical-assertion-negation-bert` | BioBERT |
| Negation (FR) | `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` | mDeBERTa-v3 (zero-shot) |
| Normalization | `cambridgeltl/SapBERT-from-PubMedBERT-fulltext` | PubMedBERT |

## Evaluation Datasets

| Dataset | Cases | Language | Source |
|---------|:-----:|:--------:|--------|
| CHU Oran (HPC) | 17 | French | Real hospital reports (Children's Hospital of Oran) |
| CHU Oran Translated | 10 | English | Translated subset of HPC reports |
| Gold Standard Corpus (GSC) | 75 | English | Community benchmark dataset |
| RareArena | 10 | English | Rare disease benchmark |
| **Total** | **112** | **FR + EN** | |

## SCORE Quality Framework

The system includes the SCORE framework for systematic quality assessment across five dimensions:

| Dimension | Description | Average Score |
|-----------|-------------|:------------:|
| **S**tructuring | Completeness of Phenopacket fields | 75.8 |
| **C**linical Coherence | Logical consistency of findings | 73.5 |
| **O**ntological Coverage | HPO normalization success rate | 62.1 |
| **R**eliability | Confidence and negation accuracy | 87.5 |
| **E**xplainability | Traceability and justification | 91.2 |
| **Composite** | Weighted average | **78.0** |

## Ontologies

- **HPO** (*Human Phenotype Ontology*) — 16,000+ phenotypic terms
- **UMLS** (*Unified Medical Language System*) — Cross-reference CUI
- **ORDO** (*Orphanet Rare Disease Ontology*) — 4,335 rare diseases
- **Phenopackets** (*ISO 4454:2022*) — GA4GH standard for patient records

## Tech Stack

| Layer | Technology |
|-------|-----------|
| NLP Backend | Python 3.10, PyTorch, HuggingFace Transformers |
| API | Flask REST API |
| Desktop UI | Streamlit |
| Web UI | Next.js 15, React 19 |
| Database | Supabase (PostgreSQL) |
| Ontology Parsing | OWL, JSON, HPOA |
| Output Format | Phenopackets JSON (ISO 4454) |

## References

- Alsentzer et al. (2019) — ClinicalBERT
- Chapman et al. (2001) — NegEx
- Liu et al. (2021) — SapBERT
- Sun & Tao (2023) — SapBERT + rules for normalization
- Dong et al. (2021, 2023) — Text to UMLS to ORDO linking
- Borisova et al. (2021) — Multilingual hybrid approach
- Jacobsen et al. (2022) — Phenopackets (ISO 4454)
- Kohler et al. (2021) — Human Phenotype Ontology

## License

This project was developed as a Final Year Project (PFE) at ESI Sidi Bel Abbes. For academic use only.
