"""
French Medical Term → HPO Mapping Dictionary (v2 — Extended)
Maps French clinical terms to HPO IDs. Covers all 5 CHU Oran disease profiles.
Source: CHU Oran reports + HPO annotations + ORDO gap analysis.
"""

FR_HPO_MAPPING = {
    # ── Immunology / DIP ─────────────────────────────────────────────────
    "déficit immunitaire": ("HP:0004430", "Immunodeficiency"),
    "déficit immunitaire primitif": ("HP:0004430", "Immunodeficiency"),
    "déficit immunitaire combiné": ("HP:0004430", "Severe combined immunodeficiency"),
    "déficit immunitaire combiné sévère": ("HP:0004430", "Severe combined immunodeficiency"),
    "déficit immunitaire primitif combiné sévère": ("HP:0004430", "Severe combined immunodeficiency"),
    "dics": ("HP:0004430", "Severe combined immunodeficiency"),
    "scid": ("HP:0004430", "Severe combined immunodeficiency"),
    "dip": ("HP:0004430", "Immunodeficiency"),
    "dip type hladr": ("HP:0004430", "Immunodeficiency"),
    "agammaglobulinémie": ("HP:0004313", "Decreased circulating antibody level"),
    "agammaglobulinémie congénitale": ("HP:0004313", "Decreased circulating antibody level"),
    "hypogammaglobulinémie": ("HP:0004313", "Decreased circulating antibody level"),
    "absence de lymphocytes b": ("HP:0001888", "Lymphopenia"),
    "déficit en lymphocytes t cd4+": ("HP:0005403", "Decreased proportion of CD4-positive T cells"),
    "déficit profond en lymphocytes t cd4+": ("HP:0005403", "Decreased proportion of CD4-positive T cells"),
    "déficit en molécules hla de classe ii": ("HP:0004430", "Immunodeficiency"),
    "déficit en hla": ("HP:0004430", "Immunodeficiency"),

    # ── Infections (critical for ORDO matching) ──────────────────────────
    "infections respiratoires à répétition": ("HP:0002205", "Recurrent respiratory infections"),
    "infections respiratoires": ("HP:0002205", "Recurrent respiratory infections"),
    "broncho-pneumopathies à répétition": ("HP:0002205", "Recurrent respiratory infections"),
    "bronchopneumopathie": ("HP:0002205", "Recurrent respiratory infections"),
    "exacerbation": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "exacerbation modérée": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "exacerbation respiratoire": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "pneumopathie": ("HP:0002090", "Pneumonia"),
    "pneumonie": ("HP:0002090", "Pneumonia"),
    "pneumopathie infectieuse": ("HP:0002090", "Pneumonia"),
    "bronchite": ("HP:0002110", "Bronchiectasis"),
    "dilatation des bronches": ("HP:0002110", "Bronchiectasis"),
    "ddb": ("HP:0002110", "Bronchiectasis"),
    "ddb cylindrique": ("HP:0002110", "Bronchiectasis"),
    "encombrement bronchique": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "encombrement bronchique chronique": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "toux grasse": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "toux grasse chronique": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "toux grasse persistante": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "otites purulentes": ("HP:0000388", "Otitis media"),
    "otites": ("HP:0000388", "Otitis media"),
    "otite moyenne": ("HP:0000388", "Otitis media"),
    "otorrhée": ("HP:0000388", "Otitis media"),
    "candidose buccale": ("HP:0002719", "Recurrent infections"),
    "bcgite": ("HP:0002719", "Recurrent infections"),
    "lésion de bcgite": ("HP:0002719", "Recurrent infections"),
    "syndrome infectieux": ("HP:0002719", "Recurrent infections"),
    "infections à répétition": ("HP:0002719", "Recurrent infections"),
    "méningite": ("HP:0002840", "Non-recurrent bacterial meningitis"),
    "sepsis": ("HP:0100806", "Sepsis"),
    "pseudomonas": ("HP:0002719", "Recurrent infections"),

    # ── Respiratory ──────────────────────────────────────────────────────
    "insuffisance respiratoire": ("HP:0002093", "Respiratory insufficiency"),
    "insuffisance respiratoire chronique": ("HP:0002093", "Respiratory insufficiency"),
    "détresse respiratoire": ("HP:0002098", "Respiratory distress"),
    "tirage": ("HP:0002098", "Respiratory distress"),
    "tirage sus sternal": ("HP:0002098", "Respiratory distress"),
    "dyspnée": ("HP:0002094", "Dyspnea"),
    "rhinite": ("HP:0003193", "Allergic rhinitis"),
    "rhinite allergique": ("HP:0003193", "Allergic rhinitis"),
    "râles ronflants": ("HP:0002835", "Aspiration"),
    "râles polymorphes": ("HP:0002835", "Aspiration"),

    # ── Dermatology ──────────────────────────────────────────────────────
    "eczéma": ("HP:0000964", "Eczema"),
    "eczéma résiduel": ("HP:0000964", "Eczema"),
    "eczématiforme": ("HP:0000964", "Eczema"),
    "ecchymoses": ("HP:0000978", "Bruising susceptibility"),
    "ecchymoses multiples": ("HP:0000978", "Bruising susceptibility"),
    "pétéchies": ("HP:0000967", "Petechiae"),
    "pâleur cutanée": ("HP:0000980", "Pallor"),
    "pâleur cutanéo-muqueuse": ("HP:0000980", "Pallor"),
    "pâleur cutanéo muqueuse": ("HP:0000980", "Pallor"),
    "pâleur": ("HP:0000980", "Pallor"),
    "ictère": ("HP:0000952", "Jaundice"),
    "syndrome hémorragique": ("HP:0001892", "Abnormal bleeding"),
    "lésions cutanées": ("HP:0000988", "Skin rash"),
    "éruption cutanée": ("HP:0000988", "Skin rash"),

    # ── Growth / Nutrition ───────────────────────────────────────────────
    "retard staturo-pondéral": ("HP:0001508", "Failure to thrive"),
    "rsp": ("HP:0001508", "Failure to thrive"),
    "retard pondéral": ("HP:0001508", "Failure to thrive"),
    "retard de croissance": ("HP:0001508", "Failure to thrive"),
    "malnutrition": ("HP:0004395", "Malnutrition"),
    "malnutrition légère": ("HP:0001508", "Failure to thrive"),
    "malnutrition modérée": ("HP:0001508", "Failure to thrive"),
    "malnutrition sévère": ("HP:0001508", "Failure to thrive"),
    "cassure de courbe": ("HP:0001508", "Failure to thrive"),
    "diminution de l'appétit": ("HP:0004395", "Malnutrition"),
    "déshydraté": ("HP:0001944", "Dehydration"),
    "déshydratation": ("HP:0001944", "Dehydration"),

    # ── Gastrointestinal ─────────────────────────────────────────────────
    "diarrhée chronique": ("HP:0002035", "Chronic diarrhea"),
    "diarrhée": ("HP:0002014", "Diarrhea"),
    "diarrhées chroniques": ("HP:0002035", "Chronic diarrhea"),
    "diarrhée chronique graisseuse": ("HP:0002035", "Chronic diarrhea"),
    "ballonnement abdominal": ("HP:0003270", "Abdominal distention"),
    "hépatomégalie": ("HP:0002240", "Hepatomegaly"),
    "splénomégalie": ("HP:0001744", "Splenomegaly"),
    "organomégalie": ("HP:0001438", "Organomegaly"),
    "insuffisance pancréatique": ("HP:0001738", "Exocrine pancreatic insufficiency"),
    "insuffisance pancréatique exocrine": ("HP:0001738", "Exocrine pancreatic insufficiency"),

    # ── Hematology ───────────────────────────────────────────────────────
    "anémie": ("HP:0001903", "Anemia"),
    "thrombopénie": ("HP:0001873", "Thrombocytopenia"),
    "thrombocytopénie": ("HP:0001873", "Thrombocytopenia"),
    "thrombopénie avec micro plaquettes": ("HP:0001873", "Thrombocytopenia"),
    "micro plaquettes": ("HP:0001873", "Thrombocytopenia"),
    "lymphopénie": ("HP:0001888", "Lymphopenia"),
    "neutropénie": ("HP:0001875", "Neutropenia"),
    "leucocytose": ("HP:0001974", "Leukocytosis"),
    "pancytopénie": ("HP:0001876", "Pancytopenia"),
    "greffon contre hôte": ("HP:0001880", "Eosinophilia"),

    # ── Fever ────────────────────────────────────────────────────────────
    "fièvre": ("HP:0001945", "Fever"),
    "fébrile": ("HP:0001945", "Fever"),
    "hyperthermie": ("HP:0001945", "Fever"),
    "apyrétique": None,

    # ── Neurology ────────────────────────────────────────────────────────
    "ataxie": ("HP:0001251", "Ataxia"),
    "télangiectasie": ("HP:0001009", "Telangiectasia"),
    "ataxie télangiectasie": ("HP:0001251", "Ataxia"),
    "hypotonie": ("HP:0001252", "Muscular hypotonia"),
    "amyotrophie spinale": ("HP:0007269", "Spinal muscular atrophy"),
    "retard psychomoteur": ("HP:0001263", "Global developmental delay"),

    # ── Musculoskeletal ──────────────────────────────────────────────────
    "arthrite": ("HP:0001369", "Arthritis"),
    "arthrite du genou": ("HP:0001369", "Arthritis"),
    "hippocratisme digital": ("HP:0001217", "Clubbing"),

    # ── Genetic / Lab ────────────────────────────────────────────────────
    "consanguinité": ("HP:0000031", "Consanguinity"),
    "mucoviscidose": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "test de la sueur positif": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "test de la sueur": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "mutation homozygote": None,

    # ── Immunoglobulins ──────────────────────────────────────────────────
    "hyper-ige": ("HP:0003212", "Increased circulating IgE level"),
    "ige élevée": ("HP:0003212", "Increased circulating IgE level"),
    "ige 1290": ("HP:0003212", "Increased circulating IgE level"),
    "déficit en igg": ("HP:0004315", "Decreased circulating IgG level"),
    "déficit en iga": ("HP:0002720", "Decreased circulating IgA level"),
    "déficit en igm": ("HP:0002850", "Decreased circulating IgM level"),
    "igg 0,33": ("HP:0004315", "Decreased circulating IgG level"),
    "igg": ("HP:0004315", "Decreased circulating IgG level"),
    "immunoglobulines g": ("HP:0004315", "Decreased circulating IgG level"),
    "iga": ("HP:0002720", "Decreased circulating IgA level"),
    "igm": ("HP:0002850", "Decreased circulating IgM level"),

    # ── Wiskott-Aldrich specific ─────────────────────────────────────────
    "syndrome de wiskott aldrich": ("HP:0002665", "Lymphoma"),
    "wiskott aldrich": ("HP:0002665", "Lymphoma"),
}

# ── French→English translation for SapBERT fallback ─────────────────────
FR_EN_TRANSLATIONS = {
    "kinésithérapie": "physiotherapy",
    "kinésithérapie respiratoire": "respiratory physiotherapy",
    "nébulisation": "nebulization",
    "antibiothérapie": "antibiotic therapy",
    "cure d'immunoglobuline": "immunoglobulin therapy",
    "cure d'immunoglobulines": "immunoglobulin therapy",
    "immunoglobuline": "immunoglobulin",
    "immunoglobulines": "immunoglobulins",
    "bilan immunologique": "immunological workup",
    "bilan du déficit immunitaire": "immunodeficiency workup",
    "bilan de déficit immunitaire": "immunodeficiency workup",
    "examen clinique": "clinical examination",
    "examen de la peau": "skin examination",
    "examen orl": "ENT examination",
    "examen pleuro pulmonaire": "pulmonary examination",
    "examen cardiovasculaire": "cardiovascular examination",
    "examen abdominal": "abdominal examination",
    "examen digestif": "digestive examination",
    "auscultation": "auscultation",
    "auscultation pulmonaire": "pulmonary auscultation",
    "numération formule sanguine": "complete blood count",
    "protéine c réactive": "C-reactive protein",
    "saturation en oxygène": "oxygen saturation",
    "bruits surajoutés": "heart murmur",
    "souffle": "murmur",
    "caries dentaires": "dental caries",
    "cicatrices": "scars",
    "râles bronchiques": "bronchial rales",
    "air ambiant": "room air",
    "apyrétique": "afebrile",
    "bactrim": "trimethoprim-sulfamethoxazole",
    "itraconazole": "itraconazole",
    "colistine": "colistin",
    "ciprofloxacine": "ciprofloxacin",
}


def lookup_french_hpo(term: str):
    """Look up a French clinical term in the FR→HPO dictionary."""
    lower = term.strip().lower()

    if lower in FR_HPO_MAPPING:
        mapping = FR_HPO_MAPPING[lower]
        if mapping is None:
            return None
        return {
            "hpo_id": mapping[0], "hpo_name": mapping[1],
            "match_type": "french_exact", "confidence": 0.95,
        }

    # Substring matching for compound terms
    best_match = None
    best_len = 0
    for key, mapping in FR_HPO_MAPPING.items():
        if mapping is None:
            continue
        if key in lower and len(key) > best_len:
            best_match = mapping
            best_len = len(key)

    if best_match and best_len >= 4:
        return {
            "hpo_id": best_match[0], "hpo_name": best_match[1],
            "match_type": "french_partial", "confidence": 0.85,
        }

    return None


def translate_to_english(term: str) -> str:
    """Translate French clinical term to English for SapBERT fallback."""
    lower = term.strip().lower()
    return FR_EN_TRANSLATIONS.get(lower, term)
