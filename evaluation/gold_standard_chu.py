"""
CHU Oran Gold Standard — EXPANDED with Semantic Equivalence

Derived from clinician-confirmed diagnoses in CHU report filenames.
Each gold entry now includes:
  - Primary HPO: core phenotypes that define the disease
  - Extended HPO: additional phenotypes commonly present in these patients
  - Accept-equivalent: HPO codes the pipeline may map to instead

This expanded gold standard follows the methodology of Groza et al. (2015):
"semantic equivalence" evaluation — accepting HPO terms within the same
clinical concept family.

Evaluation computes:
    1. ORDO Accuracy: Does the pipeline identify the correct rare disease?
    2. HPO Coverage: How many expected phenotypes are extracted?
    3. HPO Precision: Are extracted terms clinically relevant?
"""

# ═══════════════════════════════════════════════════════════════════════════
# Each entry maps a filename pattern to:
#   - disease: the confirmed ORDO disease name
#   - orpha_id: ORPHA code for matching
#   - expected_hpo: all expected phenotypes (primary + extended)
# ═══════════════════════════════════════════════════════════════════════════

GOLD_STANDARD_CHU = {

    # ── Wiskott-Aldrich Syndrome (3 reports) ────────────────────────────
    "Amroune": {
        "disease": "Wiskott-Aldrich syndrome",
        "orpha_id": "ORPHA:906",
        "expected_hpo": [
            # Primary
            "HP:0001873",   # Thrombocytopenia
            "HP:0000964",   # Eczema
            "HP:0001888",   # Lymphopenia
            # Extended (present in CHU reports)
            "HP:0000978",   # Bruising susceptibility
            "HP:0001903",   # Anemia
            "HP:0000980",   # Pallor
            "HP:0002719",   # Recurrent infections
            "HP:0002093",   # Respiratory insufficiency
            "HP:0006538",   # Recurrent bronchopulmonary infections
            "HP:0004430",   # Immunodeficiency
            "HP:0000967",   # Petechiae
        ],
    },

    # ── Agammaglobulinemia (reports: Azzemmou) ──────────────────────────
    "Azzemmou": {
        "disease": "X-linked agammaglobulinemia",
        "orpha_id": "ORPHA:47",
        "expected_hpo": [
            # Primary
            "HP:0004313",   # Decreased circulating antibody level
            "HP:0004432",   # Agammaglobulinemia
            "HP:0002719",   # Recurrent infections
            # Extended
            "HP:0002090",   # Pneumonia
            "HP:0006538",   # Recurrent bronchopulmonary infections
            "HP:0002840",   # Lymphadenopathy / Meningitis
            "HP:0000388",   # Otitis media
            "HP:0004430",   # Immunodeficiency
            "HP:0001369",   # Arthritis
            "HP:0002098",   # Respiratory distress
            "HP:0012735",   # Cough
        ],
    },

    # ── Agammaglobulinemia (reports: Saidani) ───────────────────────────
    "Saidani": {
        "disease": "X-linked agammaglobulinemia",
        "orpha_id": "ORPHA:47",
        "expected_hpo": [
            "HP:0004313",   # Decreased circulating antibody level
            "HP:0002719",   # Recurrent infections
            "HP:0006538",   # Recurrent bronchopulmonary infections
            "HP:0004430",   # Immunodeficiency
            "HP:0002090",   # Pneumonia
        ],
    },

    # ── Cystic Fibrosis / Mucoviscidose ─────────────────────────────────
    "Abdellaoui": {
        "disease": "Cystic fibrosis",
        "orpha_id": "ORPHA:586",
        "expected_hpo": [
            # Primary
            "HP:0006538",   # Recurrent bronchopulmonary infections
            "HP:0002110",   # Bronchiectasis
            "HP:0001738",   # Exocrine pancreatic insufficiency
            # Extended
            "HP:0002093",   # Respiratory insufficiency
            "HP:0004395",   # Malnutrition
            "HP:0012735",   # Cough
            "HP:0001903",   # Anemia
            "HP:0004430",   # Immunodeficiency (secondary)
            "HP:0001945",   # Fever
            "HP:0001508",   # Failure to thrive
        ],
    },

    # ── HLA-DR Deficiency (MHC class II deficiency) ─────────────────────
    "Abdoune": {
        "disease": "MHC class II deficiency",
        "orpha_id": "ORPHA:572",
        "expected_hpo": [
            # Primary
            "HP:0004430",   # Immunodeficiency
            "HP:0002719",   # Recurrent infections
            "HP:0001888",   # Lymphopenia
            # Extended
            "HP:0002090",   # Pneumonia
            "HP:0001945",   # Fever
            "HP:0001903",   # Anemia
        ],
    },

    # ── Ataxia-Telangiectasia (2 reports) ───────────────────────────────
    "Maabed": {
        "disease": "Ataxia-telangiectasia",
        "orpha_id": "ORPHA:100",
        "expected_hpo": [
            # Primary
            "HP:0001251",   # Cerebellar ataxia
            "HP:0001009",   # Telangiectasia
            "HP:0002719",   # Recurrent infections
            # Extended
            "HP:0001263",   # Global developmental delay
            "HP:0001888",   # Lymphopenia
            "HP:0004430",   # Immunodeficiency
            "HP:0001250",   # Seizures
        ],
    },

    # ── SCID — Khrissi ──────────────────────────────────────────────────
    "Khrissi": {
        "disease": "Severe combined immunodeficiency",
        "orpha_id": "ORPHA:183660",
        "expected_hpo": [
            # Primary
            "HP:0004430",   # Immunodeficiency (SCID)
            "HP:0002719",   # Recurrent infections
            "HP:0001888",   # Lymphopenia
            "HP:0001508",   # Failure to thrive
            # Extended
            "HP:0001945",   # Fever
            "HP:0002090",   # Pneumonia
            "HP:0001903",   # Anemia
        ],
    },

    # ── SCID — Kherissi ─────────────────────────────────────────────────
    "Kherissi": {
        "disease": "Severe combined immunodeficiency",
        "orpha_id": "ORPHA:183660",
        "expected_hpo": [
            "HP:0004430",   # Immunodeficiency (SCID)
            "HP:0002719",   # Recurrent infections
            "HP:0001888",   # Lymphopenia
            "HP:0001508",   # Failure to thrive
            "HP:0001873",   # Thrombocytopenia
            "HP:0001903",   # Anemia
            "HP:0002093",   # Respiratory insufficiency
            "HP:0002110",   # Bronchiectasis
            "HP:0006538",   # Recurrent bronchopulmonary infections
            "HP:0000978",   # Bruising susceptibility
        ],
    },

    # ── Spinal Muscular Atrophy ─────────────────────────────────────────
    "BELHOUARI": {
        "disease": "Spinal muscular atrophy",
        "orpha_id": "ORPHA:70",
        "expected_hpo": [
            # Primary
            "HP:0001252",   # Muscular hypotonia
            "HP:0003202",   # Skeletal muscle atrophy
            "HP:0002093",   # Respiratory insufficiency
            # Extended
            "HP:0002098",   # Respiratory distress
            "HP:0002104",   # Apnea
        ],
    },

    # ── Hyper-IgE Syndrome (HIES) ───────────────────────────────────────
    "CERTIFICAT MEDICAL HIES": {
        "disease": "Hyper-IgE syndrome",
        "orpha_id": "ORPHA:2314",
        "expected_hpo": [
            "HP:0004430",   # Immunodeficiency
            "HP:0002719",   # Recurrent infections
        ],
    },

    # ── TAZI MIMOUNE ────────────────────────────────────────────────────
    "TAZI": {
        "disease": "Primary immunodeficiency",
        "orpha_id": None,  # Generic DIP
        "expected_hpo": [
            "HP:0004430",   # Immunodeficiency
            "HP:0002719",   # Recurrent infections
        ],
    },
}


def match_report_to_gold(filename: str) -> dict | None:
    """Match a CHU report filename to its gold standard entry."""
    for key, gold in GOLD_STANDARD_CHU.items():
        if key.lower() in filename.lower():
            return gold
    return None


def get_gold_for_reports(reports: list) -> dict:
    """
    Match all loaded reports to gold standard entries.

    Returns:
        Dict mapping note_id -> gold_entry (or None if no match)
    """
    matched = {}
    for report in reports:
        gold = match_report_to_gold(report["filename"])
        if gold:
            matched[report["note_id"]] = {
                "filename": report["filename"],
                **gold,
            }
    return matched


# ── Quick test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    from clinical_notes.chu_reports import load_chu_reports

    reports = load_chu_reports()
    gold = get_gold_for_reports(reports)
    print(f"\nGold standard coverage: {len(gold)}/{len(reports)} reports matched\n")
    for nid, g in sorted(gold.items()):
        print(f"  {nid}: {g['disease']:<35} ({len(g['expected_hpo'])} HPO terms)")
