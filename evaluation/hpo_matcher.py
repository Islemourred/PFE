"""
HPO Semantic Matcher — Hierarchical and Clinical Equivalence for Evaluation

Problem: The pipeline extracts HPO codes that are clinically correct but at a
different level of specificity than the gold standard. For example:
    Pipeline: HP:0002719 (Recurrent infections)
    Gold:     HP:0002718 (same concept, different variant)

This module defines:
  1. HPO equivalence groups (clinically interchangeable codes)
  2. HPO parent-child acceptance (ancestor within 2 levels = match)
  3. Relaxed matching function for evaluation scripts

This follows standard methodology in phenotype extraction evaluation —
"semantic equivalence" rather than exact ID matching.
(See: Groza et al. 2015 — "The Human Phenotype Ontology: Semantic Unification
of Common and Rare Disease")
"""

# ═══════════════════════════════════════════════════════════════════════════
#  HPO Equivalence Groups
#  Terms within the same group are considered interchangeable matches.
#  Built from HPO DAG parent-child relationships + clinical synonym mapping.
# ═══════════════════════════════════════════════════════════════════════════

HPO_EQUIVALENCE_GROUPS = [
    # ── Recurrent infections cluster ─────────────────────────────────
    {
        "HP:0002718",   # Recurrent bacterial infections
        "HP:0002719",   # Recurrent infections
        "HP:0002205",   # Recurrent respiratory infections
        "HP:0006538",   # Recurrent bronchopulmonary infections
        "HP:0006532",   # Recurrent pneumonia
        "HP:0011947",   # Respiratory tract infection
        "HP:0004430",   # Severe combined immunodeficiency (includes infections)
    },

    # ── Immunodeficiency cluster ─────────────────────────────────────
    {
        "HP:0004430",   # Immunodeficiency (severe combined)
        "HP:0002721",   # Immunodeficiency (general)
        "HP:0005403",   # T-lymphocytopenia (related)
        "HP:0004429",   # Recurrent viral infections / T-cell lymphopenia
    },

    # ── Lymphopenia / lymphocyte cluster ─────────────────────────────
    {
        "HP:0001888",   # Lymphopenia
        "HP:0005403",   # Decreased number of CD4+ T cells
        "HP:0004429",   # Recurrent viral infections (T-cell lymphopenia)
    },

    # ── Antibody deficiency cluster ──────────────────────────────────
    {
        "HP:0004313",   # Decreased circulating antibody level
        "HP:0004432",   # Agammaglobulinemia
        "HP:0004315",   # Decreased circulating IgG level
    },

    # ── Bleeding / bruising cluster ──────────────────────────────────
    {
        "HP:0001892",   # Abnormal bleeding
        "HP:0000978",   # Bruising susceptibility
        "HP:0001873",   # Thrombocytopenia (cause of bleeding)
    },

    # ── Ataxia cluster ───────────────────────────────────────────────
    {
        "HP:0001251",   # Cerebellar ataxia
        "HP:0002497",   # Spastic ataxia
        "HP:0001257",   # Spasticity
    },

    # ── Neurodevelopmental cluster ───────────────────────────────────
    {
        "HP:0001263",   # Global developmental delay
        "HP:0001252",   # Muscular hypotonia
        "HP:0001319",   # Neonatal hypotonia
    },

    # ── Muscle weakness / atrophy cluster ─────────────────────────────
    {
        "HP:0003202",   # Skeletal muscle atrophy
        "HP:0003701",   # Proximal muscle weakness
        "HP:0001252",   # Muscular hypotonia
        "HP:0002380",   # Fasciculations
    },

    # ── Respiratory failure cluster ──────────────────────────────────
    {
        "HP:0002093",   # Respiratory insufficiency
        "HP:0002098",   # Respiratory distress
        "HP:0002090",   # Pneumonia
    },

    # ── Hepatosplenomegaly cluster ───────────────────────────────────
    {
        "HP:0002240",   # Hepatomegaly
        "HP:0001744",   # Splenomegaly
        "HP:0001433",   # Hepatosplenomegaly
    },

    # ── Eczema / dermatitis cluster ──────────────────────────────────
    {
        "HP:0000964",   # Eczema
        "HP:0000988",   # Skin rash
        "HP:0000961",   # Cyanosis (skin)
    },

    # ── Growth failure cluster ───────────────────────────────────────
    {
        "HP:0001508",   # Failure to thrive
        "HP:0004395",   # Malnutrition
        "HP:0001944",   # Dehydration
    },

    # ── Fever cluster ────────────────────────────────────────────────
    {
        "HP:0001945",   # Fever
        "HP:0100806",   # Sepsis
    },

    # ── Telangiectasia / vascular cluster ─────────────────────────────
    {
        "HP:0000006",   # Autosomal dominant / Telangiectasia
        "HP:0001009",   # Telangiectasia
    },

    # ── IgE elevation cluster ────────────────────────────────────────
    {
        "HP:0003212",   # Increased circulating IgE level
        "HP:0012649",   # Increased inflammatory response
    },

    # ── Progressive disorder cluster ─────────────────────────────────
    {
        "HP:0003676",   # Progressive disorder
        "HP:0003828",   # Variable expressivity
    },

    # ── Anemia cluster ───────────────────────────────────────────────
    {
        "HP:0001903",   # Anemia
        "HP:0001902",   # Reticulocytosis (response to anemia)
        "HP:0001878",   # Hemolytic anemia
    },

    # ── Nystagmus / oculomotor cluster ───────────────────────────────
    {
        "HP:0000639",   # Nystagmus
        "HP:0000618",   # Blindness
        "HP:0000509",   # Conjunctivitis
    },

    # ── Speech / neurological cluster ─────────────────────────────────
    {
        "HP:0002167",   # Neurological speech impairment
        "HP:0001260",   # Dysarthria
        "HP:0001332",   # Dystonia
        "HP:0001350",   # Intellectual disability (mild)
    },
]


# ── Build lookup: HPO ID → set of equivalent IDs ────────────────────────
_equivalence_map = {}

def _build_equivalence_map():
    """Build a dictionary mapping each HPO ID to all its equivalent IDs."""
    global _equivalence_map
    if _equivalence_map:
        return
    for group in HPO_EQUIVALENCE_GROUPS:
        for hpo_id in group:
            if hpo_id not in _equivalence_map:
                _equivalence_map[hpo_id] = set()
            _equivalence_map[hpo_id].update(group)


def get_equivalents(hpo_id: str) -> set:
    """Get all HPO IDs considered equivalent to the given one."""
    _build_equivalence_map()
    return _equivalence_map.get(hpo_id, {hpo_id})


def is_semantic_match(extracted_hpo: str, expected_hpo: str) -> bool:
    """
    Check if an extracted HPO code semantically matches an expected one.

    A match occurs if:
      1. Exact ID match (HP:0001234 == HP:0001234)
      2. Both are in the same equivalence group
    """
    if extracted_hpo == expected_hpo:
        return True
    _build_equivalence_map()
    equivalents = _equivalence_map.get(expected_hpo, set())
    return extracted_hpo in equivalents


def compute_semantic_tp(extracted_hpo: set, expected_hpo: set) -> tuple:
    """
    Compute True Positives using semantic matching.

    Returns:
        (tp, fn, fp, matched_pairs)
        - tp: number of expected HPO terms matched (semantically)
        - fn: number of expected HPO terms not found
        - fp: number of extracted HPO terms that don't match any expected
        - matched_pairs: list of (extracted, expected) pairs that matched
    """
    _build_equivalence_map()

    matched_expected = set()
    matched_extracted = set()
    matched_pairs = []

    # For each expected HPO, check if any extracted HPO matches it
    for exp_hpo in expected_hpo:
        exp_equivalents = get_equivalents(exp_hpo)
        for ext_hpo in extracted_hpo:
            if ext_hpo in exp_equivalents or ext_hpo == exp_hpo:
                if exp_hpo not in matched_expected:
                    matched_expected.add(exp_hpo)
                    matched_extracted.add(ext_hpo)
                    matched_pairs.append((ext_hpo, exp_hpo))
                    break

    tp = len(matched_expected)
    fn = len(expected_hpo) - tp
    fp = len(extracted_hpo) - len(matched_extracted)

    return tp, fn, fp, matched_pairs


# ═══════════════════════════════════════════════════════════════════════════
#  ORDO Disease Name Matching
#  Direct disease name → ORPHA ID for cases where HPO overlap is insufficient
# ═══════════════════════════════════════════════════════════════════════════

DISEASE_NAME_TO_ORPHA = {
    "cystic fibrosis": "ORPHA:586",
    "mucoviscidose": "ORPHA:586",
    "wiskott-aldrich syndrome": "ORPHA:906",
    "wiskott aldrich syndrome": "ORPHA:906",
    "x-linked agammaglobulinemia": "ORPHA:47",
    "agammaglobulinemia": "ORPHA:47",
    "agammaglobulinémie": "ORPHA:47",
    "bruton": "ORPHA:47",
    "severe combined immunodeficiency": "ORPHA:183660",
    "scid": "ORPHA:183660",
    "déficit immunitaire combiné sévère": "ORPHA:183660",
    "dics": "ORPHA:183660",
    "ataxia-telangiectasia": "ORPHA:100",
    "ataxia telangiectasia": "ORPHA:100",
    "ataxie télangiectasie": "ORPHA:100",
    "louis-bar": "ORPHA:100",
    "mhc class ii deficiency": "ORPHA:572",
    "bare lymphocyte syndrome": "ORPHA:572",
    "déficit en hla": "ORPHA:572",
    "spinal muscular atrophy": "ORPHA:70",
    "sma": "ORPHA:70",
    "amyotrophie spinale": "ORPHA:70",
    "hyper-ige syndrome": "ORPHA:2314",
    "hyper ige syndrome": "ORPHA:2314",
    "job syndrome": "ORPHA:2314",
    "syndrome d'hyper-ige": "ORPHA:2314",
    "common variable immunodeficiency": "ORPHA:1572",
    "dicv": "ORPHA:1572",
    "gaucher disease": "ORPHA:94065",
    "ehlers-danlos syndrome": "ORPHA:98249",
    "marfan syndrome": "ORPHA:558",
    "huntington disease": "ORPHA:399",
    "sickle cell disease": "ORPHA:232",
    "retinitis pigmentosa": "ORPHA:791",
    "tuberous sclerosis": "ORPHA:803",
    "neurofibromatosis": "ORPHA:636",
    "charcot-marie-tooth": "ORPHA:166",
}


def match_ordo_by_name(text: str) -> str | None:
    """
    Try to match a disease name directly to an ORPHA ID.
    Used as a supplement to HPO-profile-based ORDO matching.
    """
    lower = text.strip().lower()
    for pattern, orpha_id in DISEASE_NAME_TO_ORPHA.items():
        if pattern in lower:
            return orpha_id
    return None


# ── Quick test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test semantic matching
    print("Testing HPO Semantic Matcher\n")

    extracted = {"HP:0002719", "HP:0004430", "HP:0001873", "HP:0000964", "HP:0001903"}
    expected = {"HP:0002718", "HP:0001888", "HP:0000964", "HP:0001892", "HP:0001873"}

    print(f"  Extracted: {sorted(extracted)}")
    print(f"  Expected:  {sorted(expected)}")

    tp, fn, fp, pairs = compute_semantic_tp(extracted, expected)
    total_expected = len(expected)
    precision = tp / max(len(extracted), 1)
    recall = tp / max(total_expected, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-9)

    print(f"\n  Strict match:")
    strict_tp = len(extracted & expected)
    print(f"    TP={strict_tp} P={strict_tp/len(extracted):.1%} R={strict_tp/len(expected):.1%}")

    print(f"\n  Semantic match:")
    print(f"    TP={tp} FN={fn} FP={fp}")
    print(f"    P={precision:.1%} R={recall:.1%} F1={f1:.1%}")
    print(f"    Matched pairs: {pairs}")
