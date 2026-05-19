"""
French Gold Standard — Expected HPO phenotypes for CHU Oran reports.
Manually curated from clinical notes to enable quantitative evaluation.
Each entry contains the expected HPO terms present in the report.
"""

GOLD_STANDARD_FR = {
    "NOTE_FR_001": {
        "pathology": "Mucoviscidose (Cystic Fibrosis)",
        "orpha_id": "ORPHA:586",
        "expected_hpo": {
            "HP:0006538": "Recurrent bronchopulmonary infections",  # mucoviscidose, toux grasse, encombrement
            "HP:0002110": "Bronchiectasis",                         # dilatation des bronches implicit
            "HP:0002205": "Recurrent respiratory infections",       # infections respiratoires à répétition
            "HP:0001508": "Failure to thrive",                      # retard pondéral, -1.79 DS
            "HP:0001738": "Exocrine pancreatic insufficiency",      # insuffisance pancréatique exocrine
            "HP:0001945": "Fever",                                  # fébrile T: 38.7°C
            "HP:0001903": "Anemia",                                 # Hb: 11.2 g/dl
            "HP:0001974": "Leukocytosis",                           # GB: 12500
            "HP:0011227": "Elevated C-reactive protein",            # CRP: 45 mg/L
            "HP:0003193": "Allergic rhinitis",                      # rhinite allergique
            "HP:0002719": "Recurrent infections",                   # Pseudomonas
        },
    },
    "NOTE_FR_002": {
        "pathology": "Syndrome de Wiskott-Aldrich",
        "orpha_id": "ORPHA:906",
        "expected_hpo": {
            "HP:0000964": "Eczema",                                 # eczéma depuis 10j
            "HP:0001873": "Thrombocytopenia",                       # thrombopénie, plaquettes 90000
            "HP:0001888": "Lymphopenia",                            # Lymph 1200
            "HP:0000978": "Bruising susceptibility",                # ecchymoses multiples
            "HP:0002110": "Bronchiectasis",                         # DDB cylindrique
            "HP:0002093": "Respiratory insufficiency",              # insuffisance resp chronique
            "HP:0001903": "Anemia",                                 # Hb 10.6
            "HP:0002205": "Recurrent respiratory infections",       # infections resp à répétition
            "HP:0003212": "Increased circulating IgE level",        # IgE 1290
            "HP:0002721": "Immunodeficiency",                       # DIP
            "HP:0001508": "Failure to thrive",                      # malnutrition légère
        },
    },
    "NOTE_FR_003": {
        "pathology": "Agammaglobulinémie congénitale (Bruton)",
        "orpha_id": "ORPHA:47",
        "expected_hpo": {
            "HP:0004313": "Decreased circulating antibody level",   # agammaglobulinémie, IgG 0.33
            "HP:0004315": "Decreased circulating IgG level",        # IgG 0.33 g/l
            "HP:0002719": "Recurrent infections",                   # infections à répétition
            "HP:0000388": "Otitis media",                           # otites purulentes
            "HP:0001369": "Arthritis",                              # arthrite du genou
            "HP:0006538": "Recurrent bronchopulmonary infections",  # toux grasse chronique
            "HP:0002098": "Respiratory distress",                   # détresse respiratoire
            "HP:0002840": "Non-recurrent bacterial meningitis",     # méningite
            "HP:0001888": "Lymphopenia",                            # absence de lymphocytes B
            "HP:0002721": "Immunodeficiency",                       # DIP
        },
    },
    "NOTE_FR_004": {
        "pathology": "SCID atypique",
        "orpha_id": "ORPHA:183660",
        "expected_hpo": {
            "HP:0004430": "Severe combined immunodeficiency",       # DICS atypique
            "HP:0002719": "Recurrent infections",                   # syndrome infectieux
            "HP:0002205": "Recurrent respiratory infections",       # broncho-pneumopathies à répétition
            "HP:0002035": "Chronic diarrhea",                       # diarrhées chroniques
            "HP:0001508": "Failure to thrive",                      # malnutrition sévère -3.67DS
            "HP:0002098": "Respiratory distress",                   # détresse respiratoire
            "HP:0000964": "Eczema",                                 # eczématiforme
            "HP:0000980": "Pallor",                                 # pâleur cutanéo muqueuse
            "HP:0001903": "Anemia",                                 # Hb 9.8
            "HP:0011227": "Elevated C-reactive protein",            # CRP 12
            "HP:0002014": "Diarrhea",                               # diarrhée 06 selles/jour
            "HP:0002240": "Hepatomegaly",                           # ballonnement abdominal
        },
    },
    "NOTE_FR_005": {
        "pathology": "Déficit en HLA-DR (MHC class II deficiency)",
        "orpha_id": "ORPHA:572",
        "expected_hpo": {
            "HP:0004430": "Immunodeficiency",                       # DIP combiné sévère type HLADR
            "HP:0002205": "Recurrent respiratory infections",       # infections resp à répétition
            "HP:0002028": "Chronic diarrhea",                       # diarrhées chroniques
            "HP:0001508": "Failure to thrive",                      # retard staturo-pondéral
            "HP:0004395": "Malnutrition",                           # malnutrition modérée
            "HP:0000980": "Pallor",                                 # pâleur cutanéo-muqueuse
            "HP:0001903": "Anemia",                                 # Hb 10.5
            "HP:0002721": "Immunodeficiency",                       # DIP
        },
    },
}


def get_french_gold_standard():
    """Return the French gold standard."""
    return GOLD_STANDARD_FR


def get_french_gold_note_ids():
    """Return all French gold standard note IDs."""
    return list(GOLD_STANDARD_FR.keys())
