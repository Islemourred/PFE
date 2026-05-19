"""
Module 3.3 — Numeric Phenotype Parser (Bilingual)
Interprets numeric values in clinical text and maps them to HPO phenotypes.
Supports both English and French lab value patterns.
Reference: Tanwar et al. (2022)
"""

import re

# ── Common rules (work for both EN and FR) ───────────────────────────────────
NUMERIC_RULES = [
    # Temperature
    {"pattern": r'(?:temp|temperature|T)\s*[:\s]*(\d{2,3}(?:[.,]\d)?)\s*°?\s*F',
     "unit": "°F", "check": lambda v: v >= 100.4,
     "hpo_id": "HP:0001945", "hpo_name": "Fever",
     "description": "Temperature >= 100.4°F"},
    {"pattern": r'(?:temp|temperature|T|T°)\s*[:\s]*(\d{2}(?:[.,]\d)?)\s*°?\s*[Cc]',
     "unit": "°C", "check": lambda v: v >= 38.0,
     "hpo_id": "HP:0001945", "hpo_name": "Fever",
     "description": "Temperature >= 38.0°C"},
    # French: "fébrile à 39.1°C" or "T : 40,1° C"
    {"pattern": r'(?:fébrile|fébril)\s+(?:à\s+)?(\d{2}(?:[.,]\d)?)\s*°?\s*[Cc]?',
     "unit": "°C", "check": lambda v: v >= 38.0,
     "hpo_id": "HP:0001945", "hpo_name": "Fever",
     "description": "Température >= 38.0°C (fébrile)"},

    # Glucose
    {"pattern": r'(?:glucose|gluc|fasting glucose|dextro|glyc[ée]mie)\s*[:\s]*(\d{1,3}(?:[.,]\d)?)\s*(?:mg/dL|g/l)?',
     "unit": "mg/dL", "check": lambda v: v < 70,
     "hpo_id": "HP:0001943", "hpo_name": "Hypoglycemia",
     "description": "Glucose < 70 mg/dL"},
    {"pattern": r'(?:glucose|gluc|fasting glucose|dextro|glyc[ée]mie)\s*[:\s]*(\d{2,3}(?:[.,]\d)?)\s*(?:mg/dL|g/l)?',
     "unit": "mg/dL", "check": lambda v: v > 200,
     "hpo_id": "HP:0003074", "hpo_name": "Hyperglycemia",
     "description": "Glucose > 200 mg/dL"},

    # HbA1c
    {"pattern": r'(?:HbA1c|A1c)\s*[:\s]*(\d{1,2}(?:[.,]\d)?)\s*%',
     "unit": "%", "check": lambda v: v > 6.5,
     "hpo_id": "HP:0003074", "hpo_name": "Hyperglycemia",
     "description": "HbA1c > 6.5% (chronic hyperglycemia)"},

    # Hemoglobin (EN: Hgb, Hb | FR: Hb, HB, hémoglobine)
    {"pattern": r'(?:Hgb|Hb|[Hh][eé]moglobin[e]?)\s*[:\s]*(\d{1,2}(?:[.,]\d)?)\s*(?:g/d[Ll])?',
     "unit": "g/dL", "check": lambda v: v < 12.0,
     "hpo_id": "HP:0001903", "hpo_name": "Anemia",
     "description": "Hemoglobin < 12.0 g/dL"},

    # WBC (EN: WBC | FR: GB = Globules Blancs)
    {"pattern": r'(?:WBC|GB)\s*[:\s]*(\d{1,6}(?:[.,]\d)?)\s*(?:K/[uμ]L|[eé]l[eé]ments?/?[uμ]?l)?',
     "unit": "elements/uL", "check": lambda v: v > 11000 if v > 100 else v > 11.0,
     "hpo_id": "HP:0001974", "hpo_name": "Leukocytosis",
     "description": "WBC/GB > 11,000 elements/uL"},

    # Platelets (EN: Plt | FR: PLQT, plaquettes)
    {"pattern": r'(?:Plt|PLQT|plaquette[s]?)\s*[:\s]*(\d{2,6})(?:\s*(?:K|000|éléments))?',
     "unit": "K/uL", "check": lambda v: (v < 150 if v < 1000 else v < 150000),
     "hpo_id": "HP:0001873", "hpo_name": "Thrombocytopenia",
     "description": "Platelets < 150K"},

    # Lymphocytes (EN: ALC | FR: Lymph)
    {"pattern": r'(?:ALC|[Ll]ymph(?:ocyte[s]?)?)\s*[:\s]*(\d{1,5})\s*/?(?:mcL|[uμ]L|éléments)?',
     "unit": "/uL", "check": lambda v: v < 1500 if v > 100 else v < 1.5,
     "hpo_id": "HP:0001888", "hpo_name": "Lymphopenia",
     "description": "ALC/Lymphocytes < 1500/uL"},

    # SpO2
    {"pattern": r'(?:SpO2|SPO2|O2\s*sat|SaO2)\s*[:\s]*(\d{2,3})\s*%',
     "unit": "%", "check": lambda v: v < 92,
     "hpo_id": "HP:0012418", "hpo_name": "Hypoxemia",
     "description": "SpO2 < 92%"},

    # CRP (French lab value - common in reports)
    {"pattern": r'CRP\s*[:\s]*(\d{1,3}(?:[.,]\d)?)\s*(?:mg/[lL])?',
     "unit": "mg/L", "check": lambda v: v > 10,
     "hpo_id": "HP:0011227", "hpo_name": "Elevated C-reactive protein",
     "description": "CRP > 10 mg/L (inflammation)"},
]


def extract_numeric_phenotypes(text: str) -> list:
    """Extract phenotypes from numeric values in clinical text (EN + FR)."""
    # Normalize French decimal comma to dot for parsing
    phenotypes = []
    seen = set()
    for rule in NUMERIC_RULES:
        for match in re.finditer(rule["pattern"], text, re.IGNORECASE):
            try:
                raw_value = match.group(1).replace(",", ".")
                value = float(raw_value)
            except (ValueError, IndexError):
                continue
            if rule["check"](value) and rule["hpo_id"] not in seen:
                seen.add(rule["hpo_id"])
                phenotypes.append({
                    "hpo_id": rule["hpo_id"], "hpo_name": rule["hpo_name"],
                    "value": value, "unit": rule["unit"],
                    "description": rule["description"],
                    "source": match.group(0).strip(),
                    "match_type": "numeric_inference", "confidence": 1.0,
                })
    return phenotypes
