"""
Language Detector — Identifies clinical note language (French vs English).

Hybrid approach (model + heuristics):
  1. Primary:  langdetect (Google's n-gram model, 55 languages, 99%+ accuracy)
  2. Fallback: Clinical keyword heuristics (for very short texts)

Used by the pipeline to route to the correct NER model, NegEx lexicon,
and abbreviation dictionary.
"""

import re
from log_config import get_logger

logger = get_logger(__name__)

# ── Model-based detection (primary) ─────────────────────────────────────────
try:
    from langdetect import detect as _langdetect_detect
    from langdetect import DetectorFactory
    # Make detection deterministic (removes randomness in n-gram sampling)
    DetectorFactory.seed = 0
    _HAS_LANGDETECT = True
    logger.debug("langdetect loaded successfully (model-based detection enabled)")
except ImportError:
    _HAS_LANGDETECT = False
    logger.warning("langdetect not installed — falling back to heuristic detection")


# ── Clinical keyword heuristics (fallback for short texts) ──────────────────
FRENCH_MARKERS = {
    "antécédents", "antecedents", "examen clinique", "examen de la peau",
    "état général", "etat general", "prise en charge",
    "compte rendu", "hospitalisation", "motif d'admission",
    "histoire de la maladie", "traitement en cours",
    "mesures anthropométriques", "bilan paraclinique",
    "originaire et demeurant", "issu d'un couple",
    "bon état de santé", "consanguinité", "fratrie",
    "grossesse", "accouchement", "allaitement",
    "voie basse", "voie haute",
    "pas de", "absence de", "pas d'", "aucun", "aucune",
    "déficit immunitaire", "mucoviscidose", "kinésithérapie",
    "l'enfant", "le patient", "la patiente", "le nourrisson",
    "âgé de", "âgée de", "suivi depuis", "suivie depuis",
    "admis à", "admise à",
}

ENGLISH_MARKERS = {
    "chief complaint", "history of present illness",
    "assessment and plan", "review of systems",
    "past medical history", "family history",
    "presents with", "year old", "denies",
    "no evidence of", "unremarkable",
    "patient is a", "referred by",
    "status post", "follow up",
}


def _heuristic_detect(text: str) -> str:
    """Keyword-based language detection (fallback for short texts)."""
    text_lower = text.lower()

    fr_score = 0
    en_score = 0

    for marker in FRENCH_MARKERS:
        if marker in text_lower:
            fr_score += 1

    for marker in ENGLISH_MARKERS:
        if marker in text_lower:
            en_score += 1

    # French-specific characters
    fr_chars = len(re.findall(r'[éèêëàâäùûüïîôçœæ]', text_lower))
    if fr_chars > 5:
        fr_score += 3

    # French articles
    fr_articles = len(re.findall(r"\b(le |la |les |un |une |des |du |au |aux )\b", text_lower))
    if fr_articles > 5:
        fr_score += 2

    return "fr" if fr_score >= en_score else "en"


def detect_language(text: str) -> str:
    """
    Detect if a clinical note is in French or English.

    Strategy:
      1. If text is long enough (>50 chars), use langdetect (model-based)
      2. For short texts or when langdetect is unavailable, use clinical heuristics
      3. Only 'fr' and 'en' are returned (other languages default to 'en')

    Args:
        text: raw clinical note text

    Returns:
        'fr' for French, 'en' for English
    """
    # Model-based detection (primary)
    if _HAS_LANGDETECT and len(text.strip()) > 50:
        try:
            detected = _langdetect_detect(text)
            lang = "fr" if detected == "fr" else "en"
            logger.debug("Language detected (model): %s (raw: %s)", lang, detected)
            return lang
        except Exception:
            logger.debug("langdetect failed, falling back to heuristics")

    # Heuristic fallback (short texts or model failure)
    lang = _heuristic_detect(text)
    logger.debug("Language detected (heuristic): %s", lang)
    return lang
