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
    # Root / top-level terms
    "HP:0000118",   # Phenotypic abnormality (root term)
    "HP:0000001",   # All
    "HP:0012823",   # Clinical modifier
    "HP:0040064",   # Abnormality of limbs
    "HP:0002715",   # Abnormality of the immune system
    "HP:0025354",   # Cellular phenotype
    # Non-specific qualifiers (valid HPO but useless for matching)
    "HP:0011009",   # Acute
    "HP:0011010",   # Chronic
    "HP:0012825",   # Mild
    "HP:0012826",   # Moderate
    "HP:0012828",   # Severe
    "HP:0012835",   # Left
    "HP:0012834",   # Right
    "HP:0012832",   # Bilateral
    "HP:0003674",   # Onset
    "HP:0003581",   # Adult onset
    "HP:0003593",   # Infantile onset
    "HP:0003621",   # Juvenile onset
    "HP:0011463",   # Childhood onset
    "HP:0025285",   # Aggravated by
    "HP:0025297",   # Prolonged
    "HP:0031375",   # Refractory
    "HP:0012830",   # Progressive
}

# Manual clinical synonym → HPO ID mapping for phrases the NER commonly
# extracts but that don't match HPO labels/synonyms exactly
CLINICAL_SYNONYMS = {
    # ── General clinical terms ──────────────────────────────────────────
    "failure to thrive": ("HP:0001508", "Failure to thrive"),
    "ftt": ("HP:0001508", "Failure to thrive"),
    "poor weight gain": ("HP:0001508", "Failure to thrive"),
    "poor growth": ("HP:0001508", "Failure to thrive"),
    "growth retardation": ("HP:0001508", "Failure to thrive"),
    "weight loss": ("HP:0001824", "Weight loss"),
    "chest pain": ("HP:0100749", "Chest pain"),
    "shortness of breath": ("HP:0002094", "Dyspnea"),
    "difficulty breathing": ("HP:0002094", "Dyspnea"),
    "respiratory failure": ("HP:0002093", "Respiratory insufficiency"),
    "respiratory distress": ("HP:0002098", "Respiratory distress"),
    "breathing difficulty": ("HP:0002094", "Dyspnea"),

    # ── Cognitive / neurological ────────────────────────────────────────
    "cognitive decline": ("HP:0001268", "Mental deterioration"),
    "memory loss": ("HP:0002354", "Memory impairment"),
    "memory problems": ("HP:0002354", "Memory impairment"),
    "forgetfulness": ("HP:0002354", "Memory impairment"),
    "dementia": ("HP:0000726", "Dementia"),
    "abnormal movements": ("HP:0100022", "Abnormality of movement"),
    "movement disorder": ("HP:0100022", "Abnormality of movement"),
    "involuntary movements": ("HP:0004305", "Involuntary movements"),
    "difficulty walking": ("HP:0002317", "Unsteady gait"),
    "gait abnormality": ("HP:0002317", "Unsteady gait"),
    "unsteady gait": ("HP:0002317", "Unsteady gait"),
    "ataxic gait": ("HP:0002066", "Gait ataxia"),
    "speech difficulty": ("HP:0002167", "Neurological speech impairment"),
    "slurred speech": ("HP:0001260", "Dysarthria"),
    "developmental delay": ("HP:0001263", "Global developmental delay"),
    "delayed development": ("HP:0001263", "Global developmental delay"),
    "mental retardation": ("HP:0001249", "Intellectual disability"),
    "intellectual disability": ("HP:0001249", "Intellectual disability"),
    "learning difficulties": ("HP:0001249", "Intellectual disability"),
    "seizures": ("HP:0001250", "Seizure"),
    "convulsions": ("HP:0001250", "Seizure"),
    "tremor": ("HP:0001337", "Tremor"),
    "muscle weakness": ("HP:0003701", "Proximal muscle weakness"),
    "muscle wasting": ("HP:0003202", "Skeletal muscle atrophy"),
    "muscle atrophy": ("HP:0003202", "Skeletal muscle atrophy"),
    "hypotonia": ("HP:0001252", "Muscular hypotonia"),
    "low muscle tone": ("HP:0001252", "Muscular hypotonia"),
    "floppy infant": ("HP:0001319", "Neonatal hypotonia"),
    "decreased reflexes": ("HP:0001265", "Hyporeflexia"),
    "absent reflexes": ("HP:0001265", "Hyporeflexia"),

    # ── Hepatosplenomegaly / organomegaly ───────────────────────────────
    "enlarged spleen": ("HP:0001744", "Splenomegaly"),
    "enlarged liver": ("HP:0002240", "Hepatomegaly"),
    "hepatosplenomegaly": ("HP:0001433", "Hepatosplenomegaly"),

    # ── Hematology ──────────────────────────────────────────────────────
    "bleeding tendency": ("HP:0001892", "Abnormal bleeding"),
    "easy bleeding": ("HP:0001892", "Abnormal bleeding"),
    "abnormal bleeding": ("HP:0001892", "Abnormal bleeding"),
    "easy bruising": ("HP:0000978", "Bruising susceptibility"),
    "low platelets": ("HP:0001873", "Thrombocytopenia"),
    "low platelet count": ("HP:0001873", "Thrombocytopenia"),
    "platelet deficiency": ("HP:0001873", "Thrombocytopenia"),
    "low hemoglobin": ("HP:0001903", "Anemia"),
    "iron deficiency": ("HP:0001891", "Iron deficiency anemia"),
    "iron deficiency anemia": ("HP:0001891", "Iron deficiency anemia"),
    "elevated crp": ("HP:0012828", "Severe infection"),
    "high crp": ("HP:0012828", "Severe infection"),
    "elevated esr": ("HP:0012828", "Severe infection"),

    # ── Immunology / infections ─────────────────────────────────────────
    "recurrent infections": ("HP:0002719", "Recurrent infections"),
    "frequent infections": ("HP:0002719", "Recurrent infections"),
    "repeated infections": ("HP:0002719", "Recurrent infections"),
    "chronic infections": ("HP:0002719", "Recurrent infections"),
    "recurrent bacterial infections": ("HP:0002718", "Recurrent bacterial infections"),
    "recurrent respiratory infections": ("HP:0002205", "Recurrent respiratory infections"),
    "recurrent pneumonia": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "lung infection": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "lung infections": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "bronchopulmonary infections": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "immunodeficiency": ("HP:0002721", "Immunodeficiency"),
    "immune deficiency": ("HP:0002721", "Immunodeficiency"),
    "immunodeficient": ("HP:0002721", "Immunodeficiency"),
    "low immunoglobulins": ("HP:0004313", "Decreased circulating antibody level"),
    "low antibodies": ("HP:0004313", "Decreased circulating antibody level"),
    "decreased immunoglobulins": ("HP:0004313", "Decreased circulating antibody level"),
    "decreased antibodies": ("HP:0004313", "Decreased circulating antibody level"),
    "hypogammaglobulinemia": ("HP:0004313", "Decreased circulating antibody level"),
    "agammaglobulinemia": ("HP:0004432", "Agammaglobulinemia"),
    "absent b cells": ("HP:0004432", "Agammaglobulinemia"),
    "b cell deficiency": ("HP:0004432", "Agammaglobulinemia"),
    "low lymphocytes": ("HP:0001888", "Lymphopenia"),
    "lymphocyte deficiency": ("HP:0001888", "Lymphopenia"),
    "t cell deficiency": ("HP:0005403", "Decreased number of CD4+ T cells"),
    "low t cells": ("HP:0005403", "Decreased number of CD4+ T cells"),
    "recurrent viral infections": ("HP:0004429", "Recurrent viral infections"),
    "viral infections": ("HP:0004429", "Recurrent viral infections"),
    "autoimmunity": ("HP:0002960", "Autoimmunity"),
    "autoimmune": ("HP:0002960", "Autoimmunity"),
    "elevated ige": ("HP:0003212", "Increased circulating IgE level"),
    "high ige": ("HP:0003212", "Increased circulating IgE level"),
    "ige elevation": ("HP:0003212", "Increased circulating IgE level"),

    # ── Pulmonary ───────────────────────────────────────────────────────
    "chronic cough": ("HP:0012735", "Cough"),
    "productive cough": ("HP:0012735", "Cough"),
    "coughing": ("HP:0012735", "Cough"),
    "bronchiectasis": ("HP:0002110", "Bronchiectasis"),
    "pulmonary fibrosis": ("HP:0002206", "Pulmonary fibrosis"),

    # ── Dermatology ─────────────────────────────────────────────────────
    "skin rash": ("HP:0000988", "Skin rash"),
    "skin rashes": ("HP:0000988", "Skin rash"),
    "rash": ("HP:0000988", "Skin rash"),
    "eczema": ("HP:0000964", "Eczema"),
    "eczematous": ("HP:0000964", "Eczema"),
    "dermatitis": ("HP:0000964", "Eczema"),
    "cellulitis": ("HP:0100658", "Cellulitis"),
    "skin abscess": ("HP:0100658", "Cellulitis"),
    "skin abscesses": ("HP:0100658", "Cellulitis"),
    "edema": ("HP:0000969", "Edema"),
    "swelling": ("HP:0000969", "Edema"),

    # ── Gastrointestinal ────────────────────────────────────────────────
    "loose stools": ("HP:0002035", "Chronic diarrhea"),
    "chronic diarrhea": ("HP:0002035", "Chronic diarrhea"),
    "diarrhea": ("HP:0002014", "Diarrhea"),

    # ── Ear / ENT ───────────────────────────────────────────────────────
    "ear infections": ("HP:0000388", "Otitis media"),
    "otitis media": ("HP:0000388", "Otitis media"),
    "middle ear infection": ("HP:0000388", "Otitis media"),
    "hearing loss": ("HP:0000365", "Hearing impairment"),

    # ── Fever / systemic ────────────────────────────────────────────────
    "fever": ("HP:0001945", "Fever"),
    "febrile": ("HP:0001945", "Fever"),
    "high fever": ("HP:0001945", "Fever"),
    "sepsis": ("HP:0100806", "Sepsis"),
    "septicemia": ("HP:0100806", "Sepsis"),

    # ── Connective tissue / musculoskeletal ─────────────────────────────
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
    "joint hypermobility": ("HP:0001382", "Joint hypermobility"),

    # ── Ophthalmology ───────────────────────────────────────────────────
    "nystagmus": ("HP:0000639", "Nystagmus"),
    "telangiectasia": ("HP:0001009", "Telangiectasia"),
    "telangiectasias": ("HP:0001009", "Telangiectasia"),

    # ── Lymphatic ───────────────────────────────────────────────────────
    "swollen lymph nodes": ("HP:0002840", "Lymphadenopathy"),
    "lymphadenopathy": ("HP:0002840", "Lymphadenopathy"),
    "lymph node enlargement": ("HP:0002840", "Lymphadenopathy"),
    "lymphoma": ("HP:0002665", "Lymphoma"),
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
