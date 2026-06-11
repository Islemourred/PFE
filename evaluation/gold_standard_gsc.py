"""
GSC-Style Corpus Gold Standard — HPO annotations for downloaded PubMed case reports

Each entry contains:
  - note_id: matches the GSC case report ID
  - disease: the target rare disease
  - orpha_id: expected ORPHA code
  - expected_hpo: list of HPO terms expected to be found in the text
                  (based on phenotypes explicitly mentioned in the abstract)
"""

GOLD_STANDARD_GSC = {
    # ═══════════════════════════════════════════════════════════════
    # CYSTIC FIBROSIS — 3 reports
    # ═══════════════════════════════════════════════════════════════
    "GSC_EN_001": {
        "disease": "Cystic fibrosis",
        "orpha_id": "ORPHA:586",
        "expected_hpo": [
            "HP:0002024",   # Malabsorption
            "HP:0002099",   # Asthma
            "HP:0006538",   # Recurrent bronchopulmonary infections
            "HP:0001508",   # Failure to thrive
            "HP:0002110",   # Bronchiectasis
            "HP:0004401",   # Meconium ileus
            "HP:0002206",   # Pulmonary fibrosis
        ],
    },
    "GSC_EN_002": {
        "disease": "Cystic fibrosis",
        "orpha_id": "ORPHA:586",
        "expected_hpo": [
            "HP:0001738",   # Exocrine pancreatic insufficiency
            "HP:0001733",   # Pancreatitis
            "HP:0012379",   # Abnormal enzyme/protein activity
            "HP:0002024",   # Malabsorption
            "HP:0002099",   # Asthma
        ],
    },
    "GSC_EN_003": {
        "disease": "Cystic fibrosis",
        "orpha_id": "ORPHA:586",
        "expected_hpo": [
            "HP:0002110",   # Bronchiectasis
            "HP:0006538",   # Recurrent bronchopulmonary infections
            "HP:0002206",   # Pulmonary fibrosis
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    # WISKOTT-ALDRICH — 3 reports
    # ═══════════════════════════════════════════════════════════════
    "GSC_EN_004": {
        "disease": "Wiskott-Aldrich syndrome",
        "orpha_id": "ORPHA:906",
        "expected_hpo": [
            "HP:0001873",   # Thrombocytopenia
            "HP:0000988",   # Skin rash / Exanthema
            "HP:0000389",   # Chronic otitis media
            "HP:0001875",   # Neutropenia
            "HP:0000246",   # Sinusitis
            "HP:0002719",   # Recurrent infections
        ],
    },
    "GSC_EN_005": {
        "disease": "Wiskott-Aldrich syndrome",
        "orpha_id": "ORPHA:906",
        "expected_hpo": [
            "HP:0001873",   # Thrombocytopenia
            "HP:0000964",   # Eczema
            "HP:0002719",   # Recurrent infections
            "HP:0001880",   # Eosinophilia
        ],
    },
    "GSC_EN_006": {
        "disease": "Wiskott-Aldrich syndrome",
        "orpha_id": "ORPHA:906",
        "expected_hpo": [
            "HP:0001873",   # Thrombocytopenia
            "HP:0000988",   # Skin rash
            "HP:0002719",   # Recurrent infections
            "HP:0001875",   # Neutropenia
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    # AGAMMAGLOBULINEMIA — 3 reports
    # ═══════════════════════════════════════════════════════════════
    "GSC_EN_007": {
        "disease": "Agammaglobulinemia",
        "orpha_id": "ORPHA:47",
        "expected_hpo": [
            "HP:0004313",   # Decreased circulating antibody
            "HP:0002719",   # Recurrent infections
            "HP:0002205",   # Recurrent respiratory infections
            "HP:0001888",   # Lymphopenia
        ],
    },
    "GSC_EN_008": {
        "disease": "Agammaglobulinemia",
        "orpha_id": "ORPHA:47",
        "expected_hpo": [
            "HP:0004313",   # Decreased antibody
            "HP:0002719",   # Recurrent infections
            "HP:0001945",   # Fever
            "HP:0002090",   # Pneumonia
            "HP:0001508",   # Failure to thrive
        ],
    },
    "GSC_EN_009": {
        "disease": "Agammaglobulinemia",
        "orpha_id": "ORPHA:47",
        "expected_hpo": [
            "HP:0002719",   # Recurrent infections
            "HP:0004313",   # Decreased antibody
            "HP:0001945",   # Fever
            "HP:0002090",   # Pneumonia
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    # SCID — 3 reports
    # ═══════════════════════════════════════════════════════════════
    "GSC_EN_010": {
        "disease": "Severe combined immunodeficiency",
        "orpha_id": "ORPHA:183660",
        "expected_hpo": [
            "HP:0002719",   # Recurrent infections
            "HP:0001888",   # Lymphopenia
            "HP:0001508",   # Failure to thrive
            "HP:0004313",   # Decreased antibody
        ],
    },
    "GSC_EN_011": {
        "disease": "Severe combined immunodeficiency",
        "orpha_id": "ORPHA:183660",
        "expected_hpo": [
            "HP:0002719",   # Recurrent infections
            "HP:0001945",   # Fever
            "HP:0001508",   # Failure to thrive
            "HP:0002090",   # Pneumonia
            "HP:0001888",   # Lymphopenia
        ],
    },
    "GSC_EN_012": {
        "disease": "Severe combined immunodeficiency",
        "orpha_id": "ORPHA:183660",
        "expected_hpo": [
            "HP:0002719",   # Recurrent infections
            "HP:0001888",   # Lymphopenia
            "HP:0001508",   # Failure to thrive
            "HP:0002090",   # Pneumonia
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    # ATAXIA-TELANGIECTASIA — 3 reports
    # ═══════════════════════════════════════════════════════════════
    "GSC_EN_013": {
        "disease": "Ataxia-telangiectasia",
        "orpha_id": "ORPHA:100",
        "expected_hpo": [
            "HP:0001251",   # Cerebellar ataxia
            "HP:0000006",   # Autosomal dominant (not phenotype, skip)
            "HP:0001257",   # Spasticity
            "HP:0001332",   # Dystonia
            "HP:0002072",   # Chorea
            "HP:0001260",   # Dysarthria
        ],
    },
    "GSC_EN_014": {
        "disease": "Ataxia-telangiectasia",
        "orpha_id": "ORPHA:100",
        "expected_hpo": [
            "HP:0001251",   # Cerebellar ataxia
            "HP:0100585",   # Telangiectasia of the skin
            "HP:0001263",   # Global developmental delay
            "HP:0002719",   # Recurrent infections
        ],
    },
    "GSC_EN_015": {
        "disease": "Ataxia-telangiectasia",
        "orpha_id": "ORPHA:100",
        "expected_hpo": [
            "HP:0001251",   # Cerebellar ataxia
            "HP:0100585",   # Telangiectasia
            "HP:0002719",   # Recurrent infections
            "HP:0001263",   # Developmental delay
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    # MHC CLASS II DEFICIENCY — 3 reports
    # ═══════════════════════════════════════════════════════════════
    "GSC_EN_016": {
        "disease": "MHC class II deficiency",
        "orpha_id": "ORPHA:572",
        "expected_hpo": [
            "HP:0002719",   # Recurrent infections
            "HP:0001508",   # Failure to thrive
            "HP:0002014",   # Diarrhea
            "HP:0001945",   # Fever
        ],
    },
    "GSC_EN_017": {
        "disease": "MHC class II deficiency",
        "orpha_id": "ORPHA:572",
        "expected_hpo": [
            "HP:0002719",   # Recurrent infections
            "HP:0001508",   # Failure to thrive
            "HP:0002090",   # Pneumonia
            "HP:0001888",   # Lymphopenia
        ],
    },
    "GSC_EN_018": {
        "disease": "MHC class II deficiency",
        "orpha_id": "ORPHA:572",
        "expected_hpo": [
            "HP:0002719",   # Recurrent infections
            "HP:0001508",   # Failure to thrive
            "HP:0001888",   # Lymphopenia
            "HP:0002090",   # Pneumonia
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    # SPINAL MUSCULAR ATROPHY — 3 reports
    # ═══════════════════════════════════════════════════════════════
    "GSC_EN_019": {
        "disease": "Spinal muscular atrophy",
        "orpha_id": "ORPHA:70",
        "expected_hpo": [
            "HP:0001324",   # Muscle weakness
            "HP:0003202",   # Skeletal muscle atrophy
            "HP:0001270",   # Motor delay
            "HP:0001252",   # Hypotonia
        ],
    },
    "GSC_EN_020": {
        "disease": "Spinal muscular atrophy",
        "orpha_id": "ORPHA:70",
        "expected_hpo": [
            "HP:0001324",   # Muscle weakness
            "HP:0003202",   # Skeletal muscle atrophy
            "HP:0001260",   # Dysarthria
            "HP:0001265",   # Hyporeflexia
        ],
    },
    "GSC_EN_021": {
        "disease": "Spinal muscular atrophy",
        "orpha_id": "ORPHA:70",
        "expected_hpo": [
            "HP:0001324",   # Muscle weakness
            "HP:0003202",   # Skeletal muscle atrophy
            "HP:0001252",   # Hypotonia
            "HP:0001270",   # Motor delay
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    # HYPER-IGE SYNDROME — 3 reports
    # ═══════════════════════════════════════════════════════════════
    "GSC_EN_022": {
        "disease": "Hyper-IgE syndrome",
        "orpha_id": "ORPHA:2314",
        "expected_hpo": [
            "HP:0003212",   # Increased IgE
            "HP:0000964",   # Eczema
            "HP:0002719",   # Recurrent infections
            "HP:0001880",   # Eosinophilia
        ],
    },
    "GSC_EN_023": {
        "disease": "Hyper-IgE syndrome",
        "orpha_id": "ORPHA:2314",
        "expected_hpo": [
            "HP:0003212",   # Increased IgE
            "HP:0000964",   # Eczema
            "HP:0002090",   # Pneumonia
            "HP:0002719",   # Recurrent infections
            "HP:0001880",   # Eosinophilia
            "HP:0000670",   # Carious teeth
            "HP:0004322",   # Short stature
        ],
    },
    "GSC_EN_024": {
        "disease": "Hyper-IgE syndrome",
        "orpha_id": "ORPHA:2314",
        "expected_hpo": [
            "HP:0003212",   # Increased IgE
            "HP:0000964",   # Eczema
            "HP:0002719",   # Recurrent infections
            "HP:0100806",   # Skin abscess
        ],
    },
}
