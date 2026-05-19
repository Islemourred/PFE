# Module de Pré-Analyse Clinique Hybride pour le Diagnostic des Maladies Rares

> Projet de Fin d'Études — ESI SBA 2025/2026  
> Ouddane Youcef Fahed & Ourred Islam Charaf Eddine  
> Encadré par : Dr. Mezrar Samiha & Dr. Keskes Nabil

## Architecture

Pipeline hybride neuro-symbolique en 4 modules :

```
Texte clinique brut
    │
    ▼
[Module 1] Désidentification (RoBERTa — obi/deid_roberta_i2b2)
    │
    ▼
[Module 2] Extraction NER (ClinicalBERT — samrawal/bert-base-uncased_clinical-ner)
    │
    ▼
[Module 3] Validation par Règles
    ├── NegEx (détection de négation — Chapman et al., 2001)
    ├── Raisonnement temporel (détection d'impossibilités)
    ├── Parsing numérique (valeurs → phénotypes HPO)
    └── Détection d'incohérences (sexe/anatomie, conflits médicamenteux)
    │
    ▼
[Module 4] Normalisation Ontologique Hybride
    ├── Expansion d'abréviations (100+ termes cliniques)
    ├── Exact Match HPO (labels + synonymes, O(1))
    ├── SapBERT (similarité cosinus, seuil configurable)
    ├── UMLS CUI (cross-références HPO)
    └── ORDO (matching profil phénotypique → maladies rares)
    │
    ▼
Phenopacket JSON (ISO 4454:2022 — GA4GH)
```

## Structure du Projet

```
code/
├── pipeline.py                         # Orchestrateur unifié (4 modules)
├── app.py                              # Interface Streamlit
├── run_all_notes.py                    # Exécution batch + évaluation
├── mock_data.py                        # 10 notes cliniques de test
│
├── module1_preprocessing/              # Module 1 : Prétraitement
│   └── phi_remover.py                  # Désidentification PHI + extraction patient_info
│
├── module2_extraction/                 # Module 2 : Extraction sémantique
│   └── clinical_ner.py                 # NER avec positions (start/end)
│
├── module3_validation/                 # Module 3 : Validation par règles
│   ├── negex.py                        # NegEx — détection de négation
│   ├── temporal.py                     # Raisonnement temporel
│   ├── numeric.py                      # Parsing numérique → phénotypes
│   └── inconsistency.py               # Détection d'incohérences
│
├── module4_normalization/              # Module 4 : Normalisation ontologique
│   ├── abbreviations.py               # Expansion d'abréviations cliniques
│   ├── exact_matcher.py               # Matching exact HPO (labels + synonymes)
│   ├── sapbert_linker.py              # SapBERT similarité cosinus
│   ├── hpo_parser.py                  # Parseur OWL itératif (hp.owl)
│   ├── umls_mapper.py                 # Mapping HPO ↔ UMLS CUI
│   ├── ordo_matcher.py                # Matching phénotype → ORDO maladies rares
│   └── pipeline.py                    # Orchestrateur Module 4
│
├── output_builder/                     # Génération de sortie
│   └── phenopacket_builder.py         # Phenopackets ISO 4454:2022
│
├── evaluation/                         # Évaluation quantitative
│   ├── gold_standard.py               # Ground truth HPO
│   ├── metrics.py                     # P, R, F1 (micro/macro)
│   └── generate_results.py            # Tableaux pour le mémoire
│
├── hp.owl                              # Ontologie HPO (73 MB)
├── hpo_terms.json                      # Cache JSON (4 MB)
└── sapbert_hpo_index.npz              # Index SapBERT (30 MB)
```

## Installation

```bash
pip install transformers torch pysbd numpy lxml
```

## Exécution

```bash
# Pipeline sur les 10 notes cliniques
python run_all_notes.py

# Interface Streamlit
streamlit run app.py

# Tableaux de résultats
python evaluation/generate_results.py
```

## Technologies

| Composant | Modèle / Outil |
|-----------|---------------|
| Désidentification | `obi/deid_roberta_i2b2` (RoBERTa) |
| Extraction NER | `samrawal/bert-base-uncased_clinical-ner` |
| Négation | NegEx (Chapman et al., 2001) |
| Normalisation sémantique | `cambridgeltl/SapBERT-from-PubMedBERT-fulltext` |
| Ontologies | HPO, ORDO (Orphanet), UMLS |
| Format de sortie | Phenopackets ISO 4454:2022 (GA4GH) |
