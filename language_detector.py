"""
Language Detector — Identifies clinical note language (French vs English).
Uses keyword-based heuristics for fast, reliable detection.

Used by the pipeline to route to the correct NER model, NegEx lexicon,
and abbreviation dictionary.
"""

import re


# French clinical keywords (high-confidence indicators)
FRENCH_MARKERS = {
    # Section headers
    "antécédents", "antecedents", "examen clinique", "examen de la peau",
    "état général", "etat general", "prise en charge",
    "compte rendu", "hospitalisation", "motif d'admission",
    "histoire de la maladie", "traitement en cours",
    "mesures anthropométriques", "bilan paraclinique",
    # Common French clinical terms
    "originaire et demeurant", "issu d'un couple",
    "bon état de santé", "consanguinité", "fratrie",
    "grossesse", "accouchement", "allaitement",
    "voie basse", "voie haute",
    # French negation patterns
    "pas de", "absence de", "pas d'", "aucun", "aucune",
    # Common French abbreviations
    "déficit immunitaire", "mucoviscidose", "kinésithérapie",
    # Articles and prepositions
    "l'enfant", "le patient", "la patiente", "le nourrisson",
    "âgé de", "âgée de", "suivi depuis", "suivie depuis",
    "admis à", "admise à",
}

ENGLISH_MARKERS = {
    # Section headers
    "chief complaint", "history of present illness",
    "assessment and plan", "review of systems",
    "past medical history", "family history",
    # Common English clinical terms
    "presents with", "year old", "denies",
    "no evidence of", "unremarkable",
    # English patterns
    "patient is a", "referred by",
    "status post", "follow up",
}


def detect_language(text: str) -> str:
    """
    Detect if a clinical note is in French or English.

    Args:
        text: raw clinical note text

    Returns:
        'fr' for French, 'en' for English
    """
    text_lower = text.lower()

    fr_score = 0
    en_score = 0

    for marker in FRENCH_MARKERS:
        if marker in text_lower:
            fr_score += 1

    for marker in ENGLISH_MARKERS:
        if marker in text_lower:
            en_score += 1

    # Additional heuristic: French-specific characters
    fr_chars = len(re.findall(r'[éèêëàâäùûüïîôçœæ]', text_lower))
    if fr_chars > 5:
        fr_score += 3

    # Check for French articles
    fr_articles = len(re.findall(r"\b(le |la |les |un |une |des |du |au |aux )\b", text_lower))
    if fr_articles > 5:
        fr_score += 2

    return "fr" if fr_score >= en_score else "en"
