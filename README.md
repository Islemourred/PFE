# Module de Pré-Analyse Clinique Hybride pour le Diagnostic des Maladies Rares

> Projet de Fin d'Études — ESI SBA 2025/2026  
> Ouddane Youcef Fahed & Ourred Islam Charaf Eddine  
> Encadré par : Dr. Mezrar Samiha & Dr. Keskes Nabil

## Vue d'ensemble

Pipeline hybride **neuro-symbolique bilingue** (FR/EN) pour la pré-analyse automatisée de notes cliniques, conçu pour assister le diagnostic des maladies rares. Le système combine **8 modèles de deep learning** spécialisés avec des règles déterministes pour extraire, valider et normaliser les données cliniques selon les ontologies standardisées.

## Architecture

```
Note Clinique (FR ou EN)
    │
    ├── 🔍 Détection de langue (langdetect)
    │
    ├── [Module 1] Désidentification
    │     EN: obi/deid_roberta_i2b2 (RoBERTa)
    │     FR: Jean-Baptiste/camembert-ner + regex
    │
    ├── [Module 2] Extraction d'Entités (NER)
    │     EN: Helios9/BioMed_NER (DeBERTa-v3, SOTA 2024)
    │         + d4data/biomedical-ner-all (ensemble)
    │     FR: almanach/camembert-bio-gliner-v0.1 (zero-shot)
    │
    ├── [Module 3] Validation par Règles
    │     ├── Négation:      NegEx + bvanaken/clinical-assertion-negation-bert (EN)
    │     │                  NegEx + MoritzLaurer/mDeBERTa-v3-mnli-xnli (FR)
    │     ├── Temporel:      dateparser (200+ formats internationaux)
    │     ├── Numérique:     Raisonnement valeurs → phénotypes (T°, SpO2, etc.)
    │     └── Incohérences:  Conflits sexe/anatomie, interactions médicamenteuses
    │
    ├── [Module 4] Normalisation Ontologique (cascade 4 niveaux)
    │     ├── Abréviations:  3,911 termes (OpenMedData, auto-téléchargé)
    │     ├── HPO Exact:     16,000+ termes EN + 25,054 labels FR (Orphanet/INSERM)
    │     ├── SapBERT:       Similarité sémantique (cambridgeltl/SapBERT-PubMedBERT)
    │     ├── UMLS:          Cross-référence CUI
    │     └── ORDO:          4,335 profils maladies rares (phenotype.hpoa)
    │
    └── 📄 Sortie: Phenopacket JSON (ISO 4454:2022 — GA4GH)
```

## Structure du Projet

```
code/
├── pipeline.py                         # Orchestrateur principal (4 modules)
├── app.py                              # Interface Streamlit
├── run_all_notes.py                    # Batch runner + évaluation
├── log_config.py                       # Logging structuré centralisé
│
├── clinical_notes/                     # Données de test
│   ├── mock_data.py                    #   10 notes cliniques EN
│   └── mock_data_fr.py                 #   5 notes cliniques FR
│
├── data/                               # Datasets (auto-téléchargés + cachés)
│   ├── hpo_terms.json                  #   16K termes HPO parsés
│   ├── hpo_french_labels.json          #   25,054 labels FR (Orphanet)
│   ├── hpo_fr_en_translations.json     #   25,054 traductions FR→EN
│   ├── medical_abbreviations.json      #   3,911 abréviations médicales
│   ├── ordo_profiles.json              #   4,335 profils ORDO
│   └── sapbert_hpo_index.npz           #   Index SapBERT pré-calculé
│
├── module1_preprocessing/              # Module 1 : Prétraitement
│   ├── phi_remover.py                  #   Désidentification PHI
│   └── language_detector.py            #   Détection de langue
│
├── module2_extraction/                 # Module 2 : Extraction sémantique
│   └── clinical_ner.py                 #   NER bilingue (DeBERTa-v3 + GLiNER)
│
├── module3_validation/                 # Module 3 : Validation
│   ├── negex.py                        #   NegEx + transformers (bilingue)
│   ├── temporal.py                     #   Raisonnement temporel
│   ├── numeric.py                      #   Parsing numérique → phénotypes
│   └── inconsistency.py               #   Détection d'incohérences
│
├── module4_normalization/              # Module 4 : Normalisation ontologique
│   ├── normalizer.py                   #   Orchestrateur cascade 4 niveaux
│   ├── abbreviations.py               #   Expansion d'abréviations
│   ├── abbreviation_loader.py          #   Téléchargeur (3,911 termes)
│   ├── exact_matcher.py               #   Matching exact HPO
│   ├── french_hpo.py                   #   Lookup HPO français
│   ├── french_hpo_loader.py            #   Téléchargeur Orphanet (25K labels)
│   ├── hpo_parser.py                   #   Parseur OWL → JSON
│   ├── sapbert_linker.py              #   SapBERT similarité cosinus
│   ├── umls_mapper.py                 #   Mapping HPO ↔ UMLS CUI
│   ├── ordo_loader.py                 #   Téléchargeur ORDO (4,335 maladies)
│   └── ordo_matcher.py                #   Matching phénotype → maladies rares
│
├── output_builder/                     # Génération de sortie
│   └── phenopacket_builder.py         #   Phenopackets ISO 4454:2022
│
├── evaluation/                         # Évaluation quantitative
│   ├── gold_standard.py               #   Ground truth HPO (EN)
│   ├── gold_standard_fr.py            #   Ground truth HPO (FR)
│   ├── metrics.py                     #   Precision, Recall, F1
│   ├── confusion_matrix.py            #   Visualisations (heatmap, bar, pie)
│   ├── generate_results.py            #   Tableaux pour le mémoire
│   └── tune_threshold.py             #   Optimisation seuil SapBERT
│
├── output/                             # Résultats du pipeline (JSON)
├── requirements.txt                    # Dépendances Python
└── README.md                          # Ce fichier
```

## Installation

### Prérequis
- Python 3.10+
- ~4 Go d'espace disque (modèles HuggingFace)
- Connexion internet (premier lancement uniquement)

### Étapes

```bash
# 1. Cloner le projet
git clone <repo-url>
cd code

# 2. Créer un environnement virtuel (recommandé)
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. (Optionnel) Déplacer le cache HuggingFace si espace disque limité
set HF_HOME=D:\hf_cache        # Windows
# export HF_HOME=/data/hf_cache  # Linux
```

> **Note :** Les modèles transformers et les datasets sont automatiquement téléchargés au premier lancement. Aucune configuration manuelle n'est nécessaire.

## Exécution

### 1. Pipeline batch (évaluation sur 15 notes EN + FR)

```bash
python run_all_notes.py
```

Résultat : fichiers JSON dans `output/` + métriques P/R/F1.

### 2. Interface interactive (Streamlit)

```bash
streamlit run app.py
```

Ouvre une interface web à `http://localhost:8501` pour analyser des notes cliniques en temps réel.

### 3. Évaluation quantitative

```bash
# Générer les tableaux de résultats (LaTeX/Markdown)
python evaluation/generate_results.py

# Générer les visualisations (confusion matrix, bar charts)
python evaluation/confusion_matrix.py

# Optimiser le seuil SapBERT
python evaluation/tune_threshold.py
```

### 4. Traitement d'une seule note (Python)

```python
from pipeline import FullPipeline

pipeline = FullPipeline()

# Note en français
result = pipeline.process(
    "Le patient présente une hypotonie axiale, un retard psychomoteur "
    "et des crises épileptiques depuis l'âge de 3 mois.",
    note_id="NOTE_FR_001"
)

# Note en anglais
result = pipeline.process(
    "Patient is a 55yo male with progressive muscle weakness, "
    "elevated CK levels, and respiratory insufficiency.",
    note_id="NOTE_EN_001"
)
```

## Modèles Utilisés

| Composant | Modèle | Architecture |
|-----------|--------|:------------:|
| Désidentification (EN) | `obi/deid_roberta_i2b2` | RoBERTa |
| Désidentification (FR) | `Jean-Baptiste/camembert-ner` | CamemBERT |
| NER (EN, primaire) | `Helios9/BioMed_NER` | **DeBERTa-v3** (SOTA 2024) |
| NER (EN, ensemble) | `d4data/biomedical-ner-all` | BERT |
| NER (FR) | `almanach/camembert-bio-gliner-v0.1` | CamemBERT-bio + GLiNER |
| Négation (EN) | `bvanaken/clinical-assertion-negation-bert` | BioBERT |
| Négation (FR) | `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` | mDeBERTa-v3 (zero-shot) |
| Normalisation | `cambridgeltl/SapBERT-from-PubMedBERT-fulltext` | PubMedBERT |

## Datasets Auto-Téléchargés

| Dataset | Source | Entrées | Fichier cache |
|---------|--------|:-------:|---------------|
| Abréviations médicales | OpenMedData | 3,911 | `data/medical_abbreviations.json` |
| Labels HPO français | Orphanet/INSERM | 25,054 | `data/hpo_french_labels.json` |
| Traductions FR→EN | HPO Consortium | 25,054 | `data/hpo_fr_en_translations.json` |
| Profils ORDO | phenotype.hpoa | 4,335 | `data/ordo_profiles.json` |

## Ontologies

- **HPO** (*Human Phenotype Ontology*) — 16,000+ termes phénotypiques
- **UMLS** (*Unified Medical Language System*) — Cross-référence CUI
- **ORDO** (*Orphanet Rare Disease Ontology*) — 4,335 maladies rares

## Références

- Alsentzer et al. (2019) — ClinicalBERT
- Chapman et al. (2001) — NegEx
- Sun & Tao (2023) — SapBERT + règles pour la normalisation
- Dong et al. (2021, 2023) — Text→UMLS→ORDO linking
- Borisova et al. (2021) — Approche hybride multilingue
