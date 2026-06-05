"""
Module 4.1 — Clinical Abbreviation Expansion (Bilingual)
Expands common medical abbreviations in both English and French.
Sources: i2b2 corpus, CHU Oran pediatric reports, French medical guides.
"""

EN_ABBREVIATIONS = {
    # General
    "hx": "history", "dx": "diagnosis", "tx": "treatment",
    "rx": "prescription", "sx": "symptoms", "pt": "patient",
    "pts": "patients", "yo": "year old", "y/o": "year old",
    "f/u": "follow up", "c/w": "consistent with",
    "s/p": "status post", "w/": "with", "w/o": "without",
    "b/l": "bilateral", "bilat": "bilateral",
    "r/o": "rule out", "prn": "as needed",
    "bid": "twice daily", "tid": "three times daily",
    "qd": "once daily", "qhs": "at bedtime",
    "po": "by mouth", "iv": "intravenous", "im": "intramuscular",
    # Cardiovascular
    "htn": "hypertension", "afib": "atrial fibrillation",
    "mi": "myocardial infarction", "chf": "congestive heart failure",
    "cad": "coronary artery disease", "dvt": "deep vein thrombosis",
    "pe": "pulmonary embolism", "bp": "blood pressure",
    "hr": "heart rate", "rrr": "regular rate and rhythm",
    "nsr": "normal sinus rhythm",
    # Respiratory
    "sob": "shortness of breath",
    "copd": "chronic obstructive pulmonary disease",
    "uri": "upper respiratory infection",
    "cta": "clear to auscultation",
    # Gastrointestinal
    "gerd": "gastroesophageal reflux disease",
    "gi": "gastrointestinal", "n/v": "nausea and vomiting",
    "abd": "abdominal",
    # Neurological
    "cva": "cerebrovascular accident",
    "tia": "transient ischemic attack",
    "loc": "loss of consciousness", "ms": "mental status",
    "cn": "cranial nerves",
    # Musculoskeletal
    "rom": "range of motion", "ue": "upper extremity",
    "le": "lower extremity", "ot": "occupational therapy",
    # Laboratory
    "cbc": "complete blood count",
    "cmp": "comprehensive metabolic panel",
    "bun": "blood urea nitrogen", "cr": "creatinine",
    "hgb": "hemoglobin", "hct": "hematocrit",
    "plt": "platelets", "wbc": "white blood cell count",
    "ldh": "lactate dehydrogenase",
    "ast": "aspartate aminotransferase",
    "alt": "alanine aminotransferase",
    "inr": "international normalized ratio",
    "pft": "pulmonary function test",
    "fev1": "forced expiratory volume in 1 second",
    "fvc": "forced vital capacity",
    # Other
    "nkda": "no known drug allergies",
    "hbs": "hemoglobin S", "hbss": "sickle cell disease homozygous",
    "dm": "diabetes mellitus", "dm2": "diabetes mellitus type 2",
    "ckd": "chronic kidney disease",
    "esrd": "end stage renal disease",
    "bmi": "body mass index", "pmh": "past medical history",
    "fhx": "family history", "ros": "review of systems",
    "a/p": "assessment and plan", "cc": "chief complaint",
    "hpi": "history of present illness",
    "ra": "room air", "spo2": "oxygen saturation",
    "nsvd": "normal spontaneous vaginal delivery",
}

FR_ABBREVIATIONS = {
    # ── General / Administrative ─────────────────────────────────────────
    "bes": "bon état de santé",
    "hdj": "hôpital de jour",
    "atcd": "antécédents",
    "atcds": "antécédents",
    "cat": "conduite à tenir",
    "etp": "éducation thérapeutique du patient",
    "rdv": "rendez-vous",
    "rm": "rapport médical",
    "cr": "compte rendu",
    # ── Obstetrics / Neonatal ────────────────────────────────────────────
    "sa": "semaines d'aménorrhée",
    "vb": "voie basse",
    "vh": "voie haute",
    "nné": "nouveau-né",
    "nn": "nouveau-né",
    "apgar": "score d'Apgar",
    "pn": "poids de naissance",
    "rciu": "retard de croissance intra-utérin",
    "nsvd": "accouchement normal par voie basse",
    # ── Anthropometry ────────────────────────────────────────────────────
    "ds": "déviation standard",
    "imc": "indice de masse corporelle",
    "rsp": "retard staturo-pondéral",
    "pc": "périmètre crânien",
    "pa": "périmètre abdominal",
    # ── Immunology / DIP ─────────────────────────────────────────────────
    "dip": "déficit immunitaire primitif",
    "dic": "déficit immunitaire combiné",
    "dics": "déficit immunitaire combiné sévère",
    "scid": "déficit immunitaire combiné sévère",
    "dicv": "déficit immunitaire commun variable",
    "ig": "immunoglobulines",
    "igg": "immunoglobulines G",
    "iga": "immunoglobulines A",
    "igm": "immunoglobulines M",
    "ige": "immunoglobulines E",
    "lb": "lymphocytes B",
    "lt": "lymphocytes T",
    "nk": "cellules Natural Killer",
    "bcgite": "complication du BCG",
    "gvh": "réaction du greffon contre l'hôte",
    "hsct": "greffe de cellules souches hématopoïétiques",
    # ── Hematology ───────────────────────────────────────────────────────
    "nfs": "numération formule sanguine",
    "fns": "numération formule sanguine",
    "gb": "globules blancs",
    "gr": "globules rouges",
    "hb": "hémoglobine",
    "plqt": "plaquettes",
    "plt": "plaquettes",
    "pnn": "polynucléaires neutrophiles",
    "vs": "vitesse de sédimentation",
    "crp": "protéine C réactive",
    "tp": "taux de prothrombine",
    "tck": "temps de céphaline kaolin",
    "tq": "temps de Quick",
    # ── Respiratory ──────────────────────────────────────────────────────
    "fr": "fréquence respiratoire",
    "dr": "détresse respiratoire",
    "bpco": "bronchopneumopathie chronique obstructive",
    "cp": "champs pulmonaires",
    "aa": "air ambiant",
    "spo2": "saturation en oxygène",
    "ecbc": "examen cytobactériologique des crachats",
    "efr": "exploration fonctionnelle respiratoire",
    "tdm": "tomodensitométrie",
    "rx": "radiographie",
    # ── Cardiology ───────────────────────────────────────────────────────
    "fc": "fréquence cardiaque",
    "bpm": "battements par minute",
    "ecg": "électrocardiogramme",
    "bsa": "bruits surajoutés",
    "b1b2": "premier et deuxième bruits du cœur",
    # ── ORL ───────────────────────────────────────────────────────────────
    "adp": "adénopathie",
    "orl": "oto-rhino-laryngologie",
    # ── Gastroenterology ─────────────────────────────────────────────────
    "hpm": "hépatomégalie",
    "spm": "splénomégalie",
    "rgo": "reflux gastro-œsophagien",
    "asat": "aspartate aminotransférase",
    "alat": "alanine aminotransférase",
    # ── Genetics ─────────────────────────────────────────────────────────
    "cgh": "hybridation génomique comparative",
    "fish": "hybridation in situ fluorescente",
    "hla": "antigène leucocytaire humain",
    "cmh": "complexe majeur d'histocompatibilité",
    # ── Medications (common in pediatric immunology) ─────────────────────
    "atb": "antibiothérapie",
    "ttt": "traitement",
    "vit": "vitamine",
    "gh": "hormone de croissance",
    # ── Rare diseases ────────────────────────────────────────────────────
    "sma": "amyotrophie spinale",
    "at": "ataxie télangiectasie",
    "wa": "syndrome de Wiskott-Aldrich",
    "hies": "syndrome d'hyper-IgE",
}


def expand_abbreviations(text: str, lang: str = "en") -> str:
    """
    Expand known clinical abbreviations using hybrid approach:
      1. Curated CHU Oran dictionaries (138 entries, bilingual) — highest priority
      2. Downloaded medical abbreviation dataset (~3000 entries) — fallback

    Returns expanded or original text.
    """
    lower = text.strip().lower()

    # Priority 1: Curated dictionaries (language-specific)
    if lang == "fr":
        if lower in FR_ABBREVIATIONS:
            return FR_ABBREVIATIONS[lower]
    else:
        if lower in EN_ABBREVIATIONS:
            return EN_ABBREVIATIONS[lower]

    # Priority 2: Cross-language curated fallback
    if lower in FR_ABBREVIATIONS:
        return FR_ABBREVIATIONS[lower]
    if lower in EN_ABBREVIATIONS:
        return EN_ABBREVIATIONS[lower]

    # Priority 3: Downloaded medical abbreviation dataset
    global _extended_abbreviations
    if _extended_abbreviations is None:
        try:
            from module4_normalization.abbreviation_loader import load_medical_abbreviations
            _extended_abbreviations = load_medical_abbreviations()
        except Exception:
            _extended_abbreviations = {}

    if lower in _extended_abbreviations:
        return _extended_abbreviations[lower]

    return text


# Lazy-loaded extended abbreviation dataset
_extended_abbreviations = None
