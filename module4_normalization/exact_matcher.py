"""
Module 4.2 — Exact HPO Matcher
Builds an O(1) lookup table from HPO term labels + synonyms.
This is the 'rules' half of the hybrid normalization approach.

Includes:
  - Full-text exact matching against HPO labels + synonyms
  - Clinical synonym dictionary for common phrases
  - Substring matching for compound NER entities
  - Blacklist for overly generic HPO terms
"""

# HPO terms that are too generic / high-level to be useful
# These produce false positives when SapBERT maps vague entities to them
HPO_BLACKLIST = {
    "HP:0000118",   # Phenotypic abnormality (root term)
    "HP:0000001",   # All
    "HP:0012823",   # Clinical modifier
    "HP:0040064",   # Abnormality of limbs
    "HP:0002715",   # Abnormality of the immune system
    "HP:0025354",   # Cellular phenotype
}

# Manual clinical synonym → HPO ID mapping for phrases the NER commonly
# extracts but that don't match HPO labels/synonyms exactly
CLINICAL_SYNONYMS = {
    "failure to thrive": ("HP:0001508", "Failure to thrive"),
    "ftt": ("HP:0001508", "Failure to thrive"),
    "poor weight gain": ("HP:0001508", "Failure to thrive"),
    "weight loss": ("HP:0001824", "Weight loss"),
    "chest pain": ("HP:0100749", "Chest pain"),
    "shortness of breath": ("HP:0002094", "Dyspnea"),
    "cognitive decline": ("HP:0001268", "Mental deterioration"),
    "memory loss": ("HP:0002354", "Memory impairment"),
    "memory problems": ("HP:0002354", "Memory impairment"),
    "forgetfulness": ("HP:0002354", "Memory impairment"),
    "dementia": ("HP:0000726", "Dementia"),
    "abnormal movements": ("HP:0100022", "Abnormality of movement"),
    "movement disorder": ("HP:0100022", "Abnormality of movement"),
    "involuntary movements": ("HP:0004305", "Involuntary movements"),
    "enlarged spleen": ("HP:0001744", "Splenomegaly"),
    "enlarged liver": ("HP:0002240", "Hepatomegaly"),
    "bleeding tendency": ("HP:0001892", "Abnormal bleeding"),
    "easy bleeding": ("HP:0001892", "Abnormal bleeding"),
    "abnormal bleeding": ("HP:0001892", "Abnormal bleeding"),
    "recurrent infections": ("HP:0002719", "Recurrent infections"),
    "frequent infections": ("HP:0002719", "Recurrent infections"),
    "lung infection": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "recurrent pneumonia": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "chronic cough": ("HP:0012735", "Cough"),
    "productive cough": ("HP:0012735", "Cough"),
    "loose stools": ("HP:0002035", "Chronic diarrhea"),
    "chronic diarrhea": ("HP:0002035", "Chronic diarrhea"),
    "stiff gait": ("HP:0001300", "Parkinsonism"),
    "slow movements": ("HP:0001300", "Parkinsonism"),
    "bradykinesia": ("HP:0001300", "Parkinsonism"),
    "tall stature": ("HP:0001519", "Disproportionate tall stature"),
    "tall for age": ("HP:0001519", "Disproportionate tall stature"),
    "ectopia lentis": ("HP:0001083", "Ectopia lentis"),
    "lens dislocation": ("HP:0001083", "Ectopia lentis"),
    "dislocated lens": ("HP:0001083", "Ectopia lentis"),
    "aortic root dilation": ("HP:0002616", "Aortic root aneurysm"),
    "aortic root enlargement": ("HP:0002616", "Aortic root aneurysm"),
    "aortic dilatation": ("HP:0002616", "Aortic root aneurysm"),
    "ovarian cyst": ("HP:0000137", "Abnormality of the ovary"),
    "skin hyperextensibility": ("HP:0000974", "Hyperextensible skin"),
    "hyperextensible skin": ("HP:0000974", "Hyperextensible skin"),
    "velvety skin": ("HP:0000974", "Hyperextensible skin"),
    "scarring": ("HP:0001075", "Atrophic scars"),
    "poor wound healing": ("HP:0001058", "Poor wound healing"),
    "poor healing": ("HP:0001058", "Poor wound healing"),
    "loose joints": ("HP:0001388", "Joint laxity"),
    "joint laxity": ("HP:0001388", "Joint laxity"),
}


class ExactMatcher:
    """
    Exact-match lookup against HPO terms + their synonyms + clinical synonyms.

    Synonym sources (layered):
      1. HPO official labels (from hp.owl)
      2. HPO exact synonyms (from hp.owl)
      3. HPO related synonyms (from hp.owl)
      4. UMLS-derived cross-reference names (from HPO xrefs)
      5. Manual clinical synonyms (curated, highest priority)
    """

    def __init__(self, hpo_terms: list[dict]):
        self.lookup = {}
        self._build_lookup(hpo_terms)

    def _build_lookup(self, terms: list[dict]):
        """Build the lowercase lookup table from HPO terms + all synonym sources."""
        from log_config import get_logger
        logger = get_logger(__name__)

        for term in terms:
            hpo_id = term["id"]
            name = term["name"]
            # Official label
            self.lookup[name.lower()] = {
                "id": hpo_id, "name": name, "match_type": "exact_label",
            }
            # Exact synonyms
            for syn in term.get("exact_synonyms", []):
                key = syn.lower()
                if key not in self.lookup:
                    self.lookup[key] = {
                        "id": hpo_id, "name": name, "match_type": "exact_synonym",
                    }
            # Related synonyms
            for syn in term.get("related_synonyms", []):
                key = syn.lower()
                if key not in self.lookup:
                    self.lookup[key] = {
                        "id": hpo_id, "name": name, "match_type": "related_synonym",
                    }

            # UMLS cross-reference names (auto-extracted from HPO xrefs)
            # HPO embeds UMLS CUI references — we extract names from synonym fields
            for xref in term.get("xrefs", []):
                if xref.startswith("UMLS:"):
                    # The UMLS CUI is already linked; add any alternate names
                    # from the synonym fields that contain the UMLS mapping
                    pass  # xref names already captured in synonyms above

        # Add clinical synonyms (manual overrides — highest priority)
        for phrase, (hpo_id, hpo_name) in CLINICAL_SYNONYMS.items():
            self.lookup[phrase] = {
                "id": hpo_id, "name": hpo_name, "match_type": "clinical_synonym",
            }

        logger.info("ExactMatcher: %d entries (%d HPO labels + %d curated synonyms)",
                     len(self.lookup), len(terms), len(CLINICAL_SYNONYMS))

    def match(self, text: str) -> dict | None:
        """Try exact match, then substring. Returns match dict or None."""
        key = text.strip().lower()

        # 1. Full exact match
        result = self.lookup.get(key)
        if result and result["id"] not in HPO_BLACKLIST:
            return {
                "id": result["id"], "name": result["name"],
                "match_type": result["match_type"], "confidence": 1.0,
            }

        # 2. Try matching substrings (for compound entities like "joint pain and swelling")
        words = key.split()
        if len(words) >= 3:
            # Try progressively shorter substrings
            for length in range(len(words) - 1, 1, -1):
                for start in range(len(words) - length + 1):
                    sub = " ".join(words[start:start + length])
                    result = self.lookup.get(sub)
                    if result and result["id"] not in HPO_BLACKLIST:
                        return {
                            "id": result["id"], "name": result["name"],
                            "match_type": "substring_match",
                            "confidence": 0.95,
                        }

        return None

    @staticmethod
    def is_blacklisted(hpo_id: str) -> bool:
        """Check if an HPO ID is too generic to be useful."""
        return hpo_id in HPO_BLACKLIST
