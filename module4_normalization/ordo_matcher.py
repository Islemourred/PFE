"""
Module 4.4 — ORDO Rare Disease Matcher (Extended)
Matches a patient's phenotype profile (set of HPO terms) against
known rare disease profiles from the Orphanet Rare Disease Ontology.

Supports two modes:
  - Full database: 4,000+ diseases from phenotype.hpoa (downloaded once)
  - Curated only: 18 profiles from CHU Oran pediatric data (always available)
"""

from log_config import get_logger

logger = get_logger(__name__)

# ── Curated rare disease phenotype profiles ──────────────────────────────────
# Source: HPO annotations database (phenotype.hpoa) + CHU Oran clinical data
RARE_DISEASE_PROFILES = {
    # ── Original profiles ────────────────────────────────────────────────
    "ORPHA:98249": {
        "name": "Ehlers-Danlos syndrome, hypermobility type",
        "hpo": {"HP:0001382", "HP:0002829", "HP:0000978", "HP:0000974",
                "HP:0001075", "HP:0012532", "HP:0001388", "HP:0001058",
                "HP:0010485", "HP:0010499", "HP:0001252"},
    },
    "ORPHA:399": {
        "name": "Huntington disease",
        "hpo": {"HP:0002072", "HP:0000716", "HP:0002354", "HP:0000726",
                "HP:0001300", "HP:0100022", "HP:0002345", "HP:0002527"},
    },
    "ORPHA:232": {
        "name": "Sickle cell disease",
        "hpo": {"HP:0001903", "HP:0001945", "HP:0001974", "HP:0100749",
                "HP:0002829", "HP:0001744", "HP:0002090", "HP:0001878"},
    },
    "ORPHA:558": {
        "name": "Marfan syndrome",
        "hpo": {"HP:0001166", "HP:0001083", "HP:0002616", "HP:0001519",
                "HP:0000768", "HP:0001763", "HP:0000545", "HP:0001634"},
    },
    "ORPHA:94065": {
        "name": "Gaucher disease type 1",
        "hpo": {"HP:0001433", "HP:0001744", "HP:0001903", "HP:0001873",
                "HP:0001882", "HP:0002797"},
    },
    "ORPHA:791": {
        "name": "Retinitis pigmentosa",
        "hpo": {"HP:0000510", "HP:0007737", "HP:0000662", "HP:0000556"},
    },
    "ORPHA:803": {
        "name": "Tuberous sclerosis",
        "hpo": {"HP:0001250", "HP:0002104", "HP:0009721", "HP:0001263"},
    },
    "ORPHA:636": {
        "name": "Neurofibromatosis type 1",
        "hpo": {"HP:0007565", "HP:0000957", "HP:0001067", "HP:0009732"},
    },
    "ORPHA:166": {
        "name": "Charcot-Marie-Tooth disease",
        "hpo": {"HP:0003376", "HP:0001265", "HP:0002460", "HP:0003202"},
    },
    "ORPHA:2478": {
        "name": "Klinefelter syndrome",
        "hpo": {"HP:0000054", "HP:0000823", "HP:0003251", "HP:0000786"},
    },

    # ── NEW: CHU Oran pediatric immunology profiles ──────────────────────

    "ORPHA:586": {
        "name": "Cystic fibrosis",
        "name_fr": "Mucoviscidose",
        "hpo": {"HP:0006538", "HP:0002110", "HP:0002205", "HP:0001508",
                "HP:0001738", "HP:0002035", "HP:0001945", "HP:0002099",
                "HP:0002240", "HP:0001903", "HP:0002719", "HP:0011227"},
    },
    "ORPHA:183660": {
        "name": "Severe combined immunodeficiency",
        "name_fr": "Déficit immunitaire combiné sévère (DICS)",
        "hpo": {"HP:0004430", "HP:0001888", "HP:0001945", "HP:0001508",
                "HP:0002090", "HP:0001880", "HP:0005403", "HP:0002719",
                "HP:0002035", "HP:0004315", "HP:0002205", "HP:0000980",
                "HP:0002098", "HP:0001903", "HP:0002014", "HP:0002028"},
    },
    "ORPHA:906": {
        "name": "Wiskott-Aldrich syndrome",
        "name_fr": "Syndrome de Wiskott-Aldrich",
        "hpo": {"HP:0001873", "HP:0000978", "HP:0001888", "HP:0000388",
                "HP:0002719", "HP:0001903", "HP:0000988", "HP:0001744",
                "HP:0002665", "HP:0000964", "HP:0002205", "HP:0002093",
                "HP:0002110", "HP:0003212"},
    },
    "ORPHA:47": {
        "name": "X-linked agammaglobulinemia",
        "name_fr": "Agammaglobulinémie congénitale (maladie de Bruton)",
        "hpo": {"HP:0004430", "HP:0002719", "HP:0004313", "HP:0002205",
                "HP:0006538", "HP:0000388", "HP:0002840", "HP:0001888",
                "HP:0004315", "HP:0001369", "HP:0002099"},
    },
    "ORPHA:100": {
        "name": "Ataxia-telangiectasia",
        "name_fr": "Ataxie-Télangiectasie (syndrome de Louis-Bar)",
        "hpo": {"HP:0001251", "HP:0001009", "HP:0002719", "HP:0002073",
                "HP:0001263", "HP:0001888", "HP:0001250", "HP:0002059",
                "HP:0004430"},
    },
    "ORPHA:572": {
        "name": "MHC class II deficiency",
        "name_fr": "Déficit en molécules HLA de classe II",
        "hpo": {"HP:0004430", "HP:0002719", "HP:0001888", "HP:0002090",
                "HP:0001508", "HP:0002035", "HP:0002205", "HP:0001903",
                "HP:0000980", "HP:0002028", "HP:0004395"},
    },
    "ORPHA:70": {
        "name": "Spinal muscular atrophy",
        "name_fr": "Amyotrophie spinale (SMA)",
        "hpo": {"HP:0001252", "HP:0001319", "HP:0003202", "HP:0001558",
                "HP:0002093", "HP:0003323", "HP:0001371"},
    },
    "ORPHA:2314": {
        "name": "Hyper-IgE syndrome",
        "name_fr": "Syndrome d'Hyper-IgE (syndrome de Job)",
        "hpo": {"HP:0000988", "HP:0002205", "HP:0001945", "HP:0002719",
                "HP:0000718", "HP:0100806", "HP:0011123", "HP:0006538"},
    },
    "ORPHA:1572": {
        "name": "Common variable immunodeficiency",
        "name_fr": "Déficit immunitaire commun variable (DICV)",
        "hpo": {"HP:0002719", "HP:0004313", "HP:0001888", "HP:0002090",
                "HP:0001744", "HP:0002240", "HP:0006538"},
    },
}


class ORDOMatcher:
    """
    Matches patient HPO profiles to candidate rare diseases.
    
    Loads 4,000+ ORPHA diseases from the official HPO annotations database,
    then overlays curated CHU Oran profiles (which may have French names
    and locally-relevant HPO refinements).
    """

    def __init__(self, use_full_database: bool = True):
        # Start with curated profiles (always available, have name_fr)
        self.diseases = dict(RARE_DISEASE_PROFILES)

        # Load full ORDO database if available
        if use_full_database:
            try:
                from module4_normalization.ordo_loader import load_ordo_profiles
                full_profiles = load_ordo_profiles()
                if full_profiles:
                    # Merge: full database as base, curated profiles override
                    merged = dict(full_profiles)
                    merged.update(self.diseases)  # curated takes priority
                    self.diseases = merged
                    logger.info("ORDOMatcher: %d diseases loaded (%d curated + %d from HPOA)",
                                len(self.diseases), len(RARE_DISEASE_PROFILES), len(full_profiles))
            except Exception as e:
                logger.warning("Could not load full ORDO database: %s", e)
                logger.info("ORDOMatcher: using %d curated profiles only", len(self.diseases))

    def match_diseases(self, patient_hpo_ids: set, top_k: int = 5,
                        source_text: str = "") -> list:
        """
        Score rare diseases by phenotype overlap with patient profile.
        If source_text is provided, also tries direct disease name matching
        and boosts diseases mentioned by name.

        Args:
            patient_hpo_ids: set of HPO IDs from the patient
            top_k: number of top candidates to return
            source_text: optional clinical text to scan for disease names

        Returns:
            Ranked list of candidate diseases with scores
        """
        if not patient_hpo_ids:
            return []

        # ── Phase 1: Text-based disease name detection ──
        # Scan source text for explicit disease mentions → strong signal
        text_matched_orpha = None
        if source_text:
            text_matched_orpha = self._detect_disease_in_text(source_text)

        scores = []
        for ordo_id, disease in self.diseases.items():
            disease_hpo = disease["hpo"]
            overlap = patient_hpo_ids & disease_hpo
            if not overlap:
                continue

            union = patient_hpo_ids | disease_hpo
            score = len(overlap) / len(union) if union else 0
            coverage = len(overlap) / len(disease_hpo) if disease_hpo else 0
            combined = 0.6 * coverage + 0.4 * score

            # Boost score if disease name was found in text
            if text_matched_orpha and ordo_id == text_matched_orpha:
                combined = max(combined, 0.85)  # Ensure it ranks high

            scores.append({
                "ordo_id": ordo_id,
                "name": disease["name"],
                "name_fr": disease.get("name_fr", ""),
                "score": round(combined, 4),
                "jaccard": round(score, 4),
                "coverage": round(coverage, 4),
                "matched_hpo": sorted(overlap),
                "matched_count": len(overlap),
                "total_disease_hpo": len(disease_hpo),
            })

        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:top_k]

    # Disease name patterns → ORPHA ID (for text-based detection)
    _DISEASE_NAME_MAP = {
        "cystic fibrosis": "ORPHA:586",
        "mucoviscidose": "ORPHA:586",
        "wiskott-aldrich": "ORPHA:906",
        "wiskott aldrich": "ORPHA:906",
        "agammaglobulinemia": "ORPHA:47",
        "agammaglobulinémie": "ORPHA:47",
        "bruton": "ORPHA:47",
        "severe combined immunodeficiency": "ORPHA:183660",
        "déficit immunitaire combiné sévère": "ORPHA:183660",
        "scid": "ORPHA:183660",
        "dics": "ORPHA:183660",
        "ataxia-telangiectasia": "ORPHA:100",
        "ataxia telangiectasia": "ORPHA:100",
        "ataxie télangiectasie": "ORPHA:100",
        "louis-bar": "ORPHA:100",
        "mhc class ii deficiency": "ORPHA:572",
        "bare lymphocyte syndrome": "ORPHA:572",
        "déficit en hla": "ORPHA:572",
        "spinal muscular atrophy": "ORPHA:70",
        "amyotrophie spinale": "ORPHA:70",
        "hyper-ige syndrome": "ORPHA:2314",
        "hyper ige syndrome": "ORPHA:2314",
        "job syndrome": "ORPHA:2314",
        "syndrome d'hyper-ige": "ORPHA:2314",
        "common variable immunodeficiency": "ORPHA:1572",
        "ehlers-danlos": "ORPHA:98249",
        "marfan syndrome": "ORPHA:558",
        "huntington disease": "ORPHA:399",
        "sickle cell": "ORPHA:232",
        "gaucher disease": "ORPHA:94065",
        "retinitis pigmentosa": "ORPHA:791",
        "tuberous sclerosis": "ORPHA:803",
        "neurofibromatosis": "ORPHA:636",
        "charcot-marie-tooth": "ORPHA:166",
    }

    def _detect_disease_in_text(self, text: str) -> str | None:
        """Scan clinical text for explicit disease name mentions."""
        text_lower = text.lower()
        for pattern, orpha_id in self._DISEASE_NAME_MAP.items():
            if pattern in text_lower:
                logger.info("  ORDO: Disease name '%s' detected in text → %s",
                           pattern, orpha_id)
                return orpha_id
        return None
