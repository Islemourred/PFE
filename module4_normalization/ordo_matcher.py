"""
Module 4.4 — ORDO Rare Disease Matcher (Extended)
Matches a patient's phenotype profile (set of HPO terms) against
known rare disease profiles from the Orphanet Rare Disease Ontology.

Extended with 9 additional disease profiles from CHU Oran pediatric data.
"""


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
    "ORPHA:586": {
        "name": "Cystic fibrosis",
        "name_fr": "Mucoviscidose",
        "hpo": {"HP:0002110", "HP:0006538", "HP:0002035", "HP:0001508",
                "HP:0002240", "HP:0012735", "HP:0002099", "HP:0001738",
                "HP:0001945", "HP:0004401"},
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
    """Matches patient HPO profiles to candidate rare diseases."""

    def __init__(self):
        self.diseases = RARE_DISEASE_PROFILES

    def match_diseases(self, patient_hpo_ids: set, top_k: int = 5) -> list:
        """
        Score rare diseases by phenotype overlap with patient profile.

        Args:
            patient_hpo_ids: set of HPO IDs from the patient
            top_k: number of top candidates to return

        Returns:
            Ranked list of candidate diseases with scores
        """
        if not patient_hpo_ids:
            return []

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
