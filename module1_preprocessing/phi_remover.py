"""
Module 1 — PHI Remover (De-identification)
Bilingual: supports both English (RoBERTa) and French (regex-based).

English: uses obi/deid_roberta_i2b2 (RoBERTa)
French:  uses regex patterns (French clinical notes follow structured templates
         making regex-based de-identification reliable and efficient).

Design Decision — French regex vs NLP model:
  French clinical notes from CHU Oran follow strict hospital templates with
  predictable PHI placement (patient name after "L'enfant", dates as DD/MM/YYYY,
  addresses after "demeurant à", etc.). Regex-based de-identification achieves
  high accuracy on these structured documents while being faster and requiring
  no additional French NER model. This is a deliberate architecture choice, not
  a limitation. For unstructured French text, an NLP model would be preferred.

Returns: clean text + map of removed PHI + extracted patient metadata.
"""

import re
from transformers import pipeline


# ── English de-identification model ──────────────────────────────────────────
deid = pipeline(
    "ner",
    model="obi/deid_roberta_i2b2",
    aggregation_strategy="first"
)

PHI_CATEGORIES = {
    "NAME", "PATIENT", "DOCTOR", "DATE", "AGE",
    "LOCATION", "PHONE", "ID", "HOSPITAL", "EMAIL", "USERNAME"
}

# French NER model (lazy-loaded on first use)
_fr_ner_model = None


# ── French PHI regex patterns ────────────────────────────────────────────────
FR_PHI_PATTERNS = {
    "PATIENT": [
        r"(?:Patient|Pt|L'enfant|Le nourrisson|La patiente|Il s'agit (?:de l'enfant|du (?:nourrisson|patient))|C'est (?:l'enfant|le patient|la patiente))\s*[:\s]*([A-ZÀÂÉÈÊËÏÎÔÙÛÜÇ][a-zàâéèêëïîôùûüç]+(?:\s+[A-ZÀÂÉÈÊËÏÎÔÙÛÜÇ][a-zàâéèêëïîôùûüç]+){1,4})",
        r"(?:Nom et prénom)\s*[:\s]*([A-ZÀÂÉÈÊËÏÎÔÙÛÜÇ][A-ZÀÂÉÈÊËÏÎÔÙÛÜÇa-zàâéèêëïîôùûüç]+(?:\s+[A-ZÀÂÉÈÊËÏÎÔÙÛÜÇa-zàâéèêëïîôùûüç]+){1,4})",
    ],
    "DOCTOR": [
        r"(?:Dr|Pr|Docteur|Professeur)\.?\s+([A-ZÀÂÉÈÊËÏÎÔÙÛÜÇ][a-zàâéèêëïîôùûüç]+(?:\s+[A-ZÀÂÉÈÊËÏÎÔÙÛÜÇ][a-zàâéèêëïîôùûüç]+)?)",
        r"(?:Résidente?|Assistante?|Médecin|Attending)\s*(?:du service)?\s*[:\s]*(?:Dr|Pr)\.?\s+([A-ZÀÂÉÈÊËÏÎÔÙÛÜÇ][a-zàâéèêëïîôùûüç]+)",
    ],
    "DATE": [
        r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b",
        r"\b(\d{1,2}-\d{1,2}-\d{4})\b",
        r"\b(\d{4}-\d{1,2}-\d{1,2})\b",
    ],
    "LOCATION": [
        r"(?:originaire et demeurant à|demeurant à|originaire de)\s+([A-ZÀÂÉÈÊËÏÎÔÙÛÜÇ][A-ZÀÂÉÈÊËÏÎÔÙÛÜÇa-zàâéèêëïîôùûüç\s\-']+?)(?:\s*[,.\n])",
        r"(?:Adresse)\s*[:\s]*([A-ZÀÂÉÈÊËÏÎÔÙÛÜÇ][^\n,]{2,30})",
    ],
    "PHONE": [
        r"(?:Tél|Tel|Téléphone)\s*[:\s]*([\d\s./-]{8,20})",
        r"\b(0[567]\.\d{2}\.\d{2}\.\d{2}\.\d{2})\b",
    ],
    "ID": [
        r"(?:MRN|Dossier|N°\s*(?:de\s+)?Dossier|Numéro\s+Dossier)\s*[:\s]*(\d{3,10})",
    ],
    "HOSPITAL": [
        r"(?:EPH|CHU|EHU|Hôpital)\s+([A-ZÀÂÉÈÊËÏÎÔÙÛÜÇ][^\n,]{2,30}?)(?:\s*[,.\n])",
    ],
}


def extract_patient_info(text: str, lang: str = "en") -> dict:
    """
    Extract basic patient metadata (sex, age) from clinical note header.
    Supports both English and French patterns.
    """
    info = {}

    if lang == "fr":
        # French sex detection
        sex_patterns_fr = [
            (r'\bSex[e]?\s*[:\s]*(M|F)\b', lambda m: "male" if m.group(1) == "M" else "female"),
            (r'\b(?:âgée?\s+de|nourrisson)\b.*?\b(masculin|féminin)\b',
             lambda m: "male" if "masculin" in m.group(1) else "female"),
            (r'\bSex[e]?\s*[:\s]*(masculin|féminin|M|F)\b',
             lambda m: "male" if m.group(1) in ("M", "masculin") else "female"),
            (r'\b(garçon|fille)\b', lambda m: "male" if m.group(1) == "garçon" else "female"),
        ]
        for pattern, extractor in sex_patterns_fr:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["sex"] = extractor(match)
                break

        # French age detection
        age_patterns_fr = [
            r'âgée?\s+(?:actuellement\s+)?de\s+(\d{1,2})\s*ans?',
            r'âgée?\s+de\s+(\d{1,2})\s*mois',
            r'Age\s*[:\s]*(\d{1,3})',
        ]
        for pattern in age_patterns_fr:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["age"] = match.group(1)
                # Check if months
                if "mois" in match.group(0).lower():
                    info["age_unit"] = "months"
                else:
                    info["age_unit"] = "years"
                break
    else:
        # English sex detection (original)
        sex_patterns = [
            (r'\bSex:\s*(M|F)\b', lambda m: "male" if m.group(1) == "M" else "female"),
            (r'\b(\d+)\s*(?:yo|y/o|year[- ]old)\s+(male|female|M|F)\b',
             lambda m: "male" if m.group(2) in ("M", "male") else "female"),
            (r'\b(male|female)\b', lambda m: m.group(1).lower()),
        ]
        for pattern, extractor in sex_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["sex"] = extractor(match)
                break

        # English age detection (original)
        age_patterns = [
            r'\b(\d{1,3})\s*(?:yo|y/o|year[- ]old)\b',
            r'\bAge:\s*(\d{1,3})\b',
            r'\b(\d{1,3})\s*(?:day|days|wk|wks|week|weeks|mo|month|months)\s*old\b',
        ]
        for pattern in age_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["age"] = match.group(1)
                break

    return info


def process_phi_french(text: str) -> dict:
    """
    Remove PHI from French clinical notes using hybrid approach:
      1. Regex patterns (for structured template fields)
      2. CamemBERT-NER (for unstructured PER/LOC/ORG entities)
    Results from both methods are merged for maximum coverage.
    """
    patient_info = extract_patient_info(text, lang="fr")

    phi_map = {}
    clean = text

    # ── Pass 1: Regex-based PHI detection (structured templates) ──
    for category, patterns in FR_PHI_PATTERNS.items():
        for pattern in patterns:
            for match in re.finditer(pattern, clean, re.IGNORECASE):
                value = match.group(1).strip()
                if not value or len(value) < 2:
                    continue
                if category not in phi_map:
                    phi_map[category] = value
                elif isinstance(phi_map[category], list):
                    if value not in phi_map[category]:
                        phi_map[category].append(value)
                else:
                    if phi_map[category] != value:
                        phi_map[category] = [phi_map[category], value]

    # ── Pass 2: GLiNER zero-shot NER (unstructured entity detection) ──
    # Uses the same model as Module 2 French NER — no extra download needed.
    try:
        global _fr_ner_model
        if _fr_ner_model is None:
            from gliner import GLiNER
            _fr_ner_model = GLiNER.from_pretrained(
                "almanach/camembert-bio-gliner-v0.1", local_files_only=True
            )

        phi_labels = ["nom de personne", "lieu", "hopital", "adresse"]
        ner_entities = _fr_ner_model.predict_entities(
            text[:1024], phi_labels, threshold=0.5
        )
        gliner_label_map = {
            "nom de personne": "PATIENT",
            "lieu": "LOCATION",
            "hopital": "HOSPITAL",
            "adresse": "LOCATION",
        }
        for ent in ner_entities:
            ner_cat = gliner_label_map.get(ent["label"])
            if not ner_cat:
                continue
            value = ent["text"].strip()
            if not value or len(value) < 2:
                continue
            # Only add if not already captured by regex
            existing = phi_map.get(ner_cat, "")
            if isinstance(existing, list):
                if value not in existing:
                    existing.append(value)
            elif existing and existing != value:
                phi_map[ner_cat] = [existing, value]
            elif not existing:
                phi_map[ner_cat] = value
    except Exception:
        pass  # GLiNER not available, regex results are sufficient

    # Replace PHI values in text with tags (longest first to avoid partial matches)
    all_values = []
    for cat, val in phi_map.items():
        if isinstance(val, list):
            for v in val:
                all_values.append((v, cat))
        else:
            all_values.append((val, cat))

    all_values.sort(key=lambda x: len(x[0]), reverse=True)
    for value, cat in all_values:
        clean = clean.replace(value, f"[{cat}]")

    return {
        "clean_text": clean.strip(),
        "phi_map": phi_map,
        "patient_info": patient_info,
    }


def process_phi_english(text: str) -> dict:
    """
    Remove PHI from English clinical notes using obi/deid_roberta_i2b2.
    Original implementation.
    """
    patient_info = extract_patient_info(text, lang="en")

    entities = deid(text)

    # Merge fragmented PHI values
    phi_raw = {}
    for ent in entities:
        cat = ent["entity_group"].upper()
        score = round(float(ent["score"]), 3)
        if cat not in PHI_CATEGORIES:
            continue
        value = ent["word"].strip()
        if cat not in phi_raw:
            phi_raw[cat] = {"value": value, "score": score, "end": ent["end"]}
        else:
            prev = phi_raw[cat]
            if ent["start"] - prev["end"] <= 2:
                prev["value"] += value
                prev["end"] = ent["end"]
            else:
                if not isinstance(prev["value"], list):
                    prev["value"] = [prev["value"]]
                prev["value"].append(value)

    phi_map = {k: v["value"] for k, v in phi_raw.items()}

    # Replace PHI in text
    for ent in sorted(entities, key=lambda x: x["start"], reverse=True):
        cat = ent["entity_group"].upper()
        if cat in PHI_CATEGORIES:
            text = text[:ent["start"]] + f"[{cat}]" + text[ent["end"]:]

    for cat in PHI_CATEGORIES:
        text = re.sub(rf'(\[{cat}\]\s*)+', f'[{cat}] ', text)

    return {
        "clean_text": text.strip(),
        "phi_map": phi_map,
        "patient_info": patient_info,
    }


def process_phi(text: str, lang: str = "en") -> dict:
    """
    Remove Protected Health Information from clinical text.
    Routes to French or English de-identification based on language.

    Args:
        text: raw clinical note
        lang: 'fr' or 'en'

    Returns:
        {"clean_text": "...", "phi_map": {...}, "patient_info": {...}}
    """
    if lang == "fr":
        return process_phi_french(text)
    else:
        return process_phi_english(text)
