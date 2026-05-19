"""
Module 3.4 — Inconsistency Detector (Bilingual)
Detects logical contradictions and clinical inconsistencies in patient data.
Checks: sex/anatomy conflicts, lab value contradictions, drug-disease conflicts.
Supports both English and French clinical terminology.
"""

import re

# Sex-specific anatomy/conditions (English + French)
FEMALE_ONLY = {
    # English
    "ovarian", "ovary", "uterine", "uterus", "endometrial",
    "endometriosis", "cervical", "cervix", "pregnancy", "pregnant",
    "menstrual", "menstruation", "menarche", "gravida", "para",
    # French
    "ovarien", "ovarienne", "ovaire", "utérin", "utérine", "utérus",
    "endométrial", "endométriose", "cervical", "col utérin",
    "grossesse", "enceinte", "menstruel", "menstruation", "ménarche",
}
MALE_ONLY = {
    # English
    "testicular", "testicle", "prostate", "prostatic", "penile",
    "epididymitis", "varicocele",
    # French
    "testiculaire", "testicule", "prostate", "prostatique",
    "pénien", "épididymite", "varicocèle",
}

# Dangerous drug-disease combinations (bilingual)
DRUG_DISEASE_CONFLICTS = [
    {"drugs": ["warfarin", "heparin", "enoxaparin", "rivaroxaban", "apixaban",
               "aspirin", "warfarine", "héparine", "aspirine", "anticoagulant"],
     "conditions": ["hemophilia", "bleeding disorder", "hemorrhage",
                     "hémophilie", "trouble hémorragique", "hémorragie",
                     "syndrome hémorragique", "saignement"],
     "severity": "critical",
     "message": "Anticoagulant/antiplatelet prescribed with bleeding disorder"},
    {"drugs": ["metformin", "metformine"],
     "conditions": ["renal failure", "kidney failure", "ckd stage 4", "ckd stage 5", "esrd",
                     "insuffisance rénale", "insuffisance renale"],
     "severity": "warning",
     "message": "Metformin with severe renal impairment (lactic acidosis risk)"},
    {"drugs": ["nsaid", "ibuprofen", "naproxen", "ketorolac", "aspirin",
               "ibuprofène", "naproxène", "aspirine", "ains"],
     "conditions": ["gi bleed", "gastrointestinal bleed", "peptic ulcer",
                     "hémorragie digestive", "ulcère gastrique", "ulcère peptique"],
     "severity": "warning",
     "message": "NSAID with history of GI bleeding"},
]


def detect_inconsistencies(text: str, entities: dict, patient_info: dict) -> list:
    """
    Detect clinical inconsistencies in a patient note.

    Args:
        text: clean clinical text
        entities: NER entities dict
        patient_info: {"sex": "male"/"female", "age": "55"}

    Returns:
        List of inconsistency warnings
    """
    warnings = []
    text_lower = text.lower()

    # 1. Sex/anatomy conflicts
    sex = patient_info.get("sex", "").lower()
    if sex == "male":
        for term in FEMALE_ONLY:
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                warnings.append({
                    "type": "sex_anatomy_conflict",
                    "severity": "critical",
                    "message": f"Female-specific term '{term}' found in male patient record",
                    "term": term,
                })
    elif sex == "female":
        for term in MALE_ONLY:
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                warnings.append({
                    "type": "sex_anatomy_conflict",
                    "severity": "critical",
                    "message": f"Male-specific term '{term}' found in female patient record",
                    "term": term,
                })

    # 2. Lab value contradictions
    has_hypoglycemia = bool(re.search(
        r'(?:glucose|gluc|glycémie|dextro)\s*[:\s]*\d{1,2}\s*(?:mg/dL|g/l)?', text_lower
    ))
    has_high_a1c = bool(re.search(
        r'(?:hba1c|a1c)\s*[:\s]*(?:1[0-9]|[89])(?:[.,]\d)?\s*%', text_lower
    ))
    if has_hypoglycemia and has_high_a1c:
        warnings.append({
            "type": "lab_value_conflict",
            "severity": "warning",
            "message": "Acute hypoglycemia with elevated HbA1c — consider glycemic variability or brittle diabetes",
        })

    # 3. Drug-disease conflicts
    all_entity_text = " ".join(
        e["text"].lower()
        for cat in entities.values()
        if isinstance(cat, list)
        for e in cat
    )
    combined = text_lower + " " + all_entity_text

    for conflict in DRUG_DISEASE_CONFLICTS:
        found_drug = any(d in combined for d in conflict["drugs"])
        found_condition = any(c in combined for c in conflict["conditions"])
        if found_drug and found_condition:
            warnings.append({
                "type": "drug_disease_conflict",
                "severity": conflict["severity"],
                "message": conflict["message"],
            })

    return warnings
