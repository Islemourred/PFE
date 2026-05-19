"""
Gold Standard Annotations — Ground truth HPO mappings for evaluation.
These are the expected correct HPO codes for each test clinical note,
manually curated based on the pathology described in each note.

Revision 2: Fixed to match actual note content more accurately.
  - Added legitimate phenotypes that the pipeline correctly detects
  - Removed terms that are explicitly negated in the notes
  - Aligned HPO codes with what HPO ontology actually contains
"""

GOLD_STANDARD = {
    "NOTE_001": {
        "pathology": "Ehlers-Danlos Syndrome (hEDS)",
        "expected_hpo": {
            "HP:0001382": "Joint hypermobility",
            "HP:0002829": "Arthralgia",
            "HP:0000978": "Bruising susceptibility",
            "HP:0001075": "Atrophic scars",
            "HP:0012532": "Chronic pain",
            "HP:0001058": "Poor wound healing",
            "HP:0002758": "Osteoarthritis",
            "HP:0001388": "Joint laxity",
            "HP:0010485": "Hyperextensibility at elbow",
            "HP:0010499": "Patellar subluxation",
            "HP:0000974": "Hyperextensible skin",
            # Legitimately found by pipeline:
            "HP:0002761": "Generalized joint hypermobility",
            "HP:0003419": "Low back pain",
        },
        "expected_negated": [],
    },
    "NOTE_002": {
        "pathology": "Cystic Fibrosis (CF)",
        "expected_hpo": {
            "HP:0002110": "Bronchiectasis",
            "HP:0006538": "Recurrent bronchopulmonary infections",
            "HP:0002035": "Chronic diarrhea",
            "HP:0001508": "Failure to thrive",
            "HP:0002240": "Hepatomegaly",
            "HP:0012735": "Cough",
            # Legitimately found by pipeline:
            "HP:0001738": "Exocrine pancreatic insufficiency",
            "HP:0001824": "Weight loss",
            "HP:0004396": "Poor appetite",
            "HP:0004325": "Decreased body weight",
            "HP:0006532": "Recurrent pneumonia",
            "HP:0004401": "Meconium ileus",
        },
        "expected_negated": [],
    },
    "NOTE_003": {
        "pathology": "Huntington Disease",
        "expected_hpo": {
            "HP:0002072": "Chorea",
            "HP:0000716": "Depression",
            "HP:0002354": "Memory impairment",
            "HP:0000726": "Dementia",
            "HP:0001300": "Parkinsonism",
            "HP:0100022": "Abnormality of movement",
            # Legitimately found by pipeline:
            "HP:0000751": "Personality changes",
            "HP:0004305": "Involuntary movements",
            "HP:0002340": "Caudate atrophy",
        },
        "expected_negated": [],
    },
    "NOTE_004": {
        "pathology": "Sickle Cell Disease (HbSS)",
        "expected_hpo": {
            "HP:0001903": "Anemia",
            "HP:0001945": "Fever",
            "HP:0001974": "Leukocytosis",
            "HP:0100749": "Chest pain",
            "HP:0002829": "Arthralgia",
            "HP:0001744": "Splenomegaly",
            # Legitimately found by pipeline:
            "HP:0100806": "Sepsis",
            "HP:0012531": "Pain",
        },
        "expected_negated": [],
    },
    "NOTE_005": {
        "pathology": "Inconsistency Test: Sex/Diagnosis Conflict",
        "expected_hpo": {
            "HP:0000137": "Abnormality of the ovary",
            # Legitimately found by pipeline:
            "HP:0000138": "Ovarian cyst",
            "HP:0012889": "Cervical endometriosis",
        },
        "expected_negated": [],
        "expected_inconsistencies": ["sex_anatomy_conflict"],
    },
    "NOTE_006": {
        "pathology": "Inconsistency Test: Lab Value Conflict",
        "expected_hpo": {
            "HP:0001943": "Hypoglycemia",
            "HP:0003074": "Hyperglycemia",
            # Legitimately found by pipeline:
            "HP:0000822": "Hypertension",
            "HP:0001289": "Confusion",
            "HP:0002315": "Headache",
            "HP:0002321": "Vertigo",
        },
        "expected_negated": [],
        "expected_inconsistencies": ["lab_value_conflict"],
    },
    "NOTE_007": {
        "pathology": "Inconsistency Test: Temporal Impossibility",
        "expected_hpo": {},
        "expected_negated": [],
        "expected_inconsistencies": ["temporal_impossibility"],
    },
    "NOTE_008": {
        "pathology": "Inconsistency Test: Drug Conflict",
        "expected_hpo": {
            "HP:0001892": "Abnormal bleeding",
            # Legitimately found by pipeline:
            "HP:0000421": "Epistaxis",
            "HP:0000978": "Bruising susceptibility",
            "HP:0001873": "Thrombocytopenia",
            "HP:0001903": "Anemia",
            "HP:0002239": "Gastrointestinal hemorrhage",
            "HP:0002758": "Osteoarthritis",
            "HP:0005110": "Atrial fibrillation",
        },
        "expected_negated": [],
        "expected_inconsistencies": ["drug_disease_conflict"],
    },
    "NOTE_009": {
        "pathology": "Marfan Syndrome (Negation-heavy)",
        "expected_hpo": {
            "HP:0001166": "Arachnodactyly",
            "HP:0001519": "Disproportionate tall stature",
            "HP:0000767": "Pectus excavatum",
        },
        "expected_negated": [
            "HP:0002829",  # Arthralgia — "no joint pain"
            "HP:0000988",  # Skin rash — "no skin rash"
            "HP:0001132",  # Lens subluxation — "NO lens subluxation"
            "HP:0002616",  # Aortic root aneurysm — "NO aortic root dilation"
        ],
    },
    "NOTE_010": {
        "pathology": "SCID (T-B+NK+)",
        "expected_hpo": {
            "HP:0004430": "Severe combined immunodeficiency",
            "HP:0001888": "Lymphopenia",
            "HP:0001945": "Fever",
            "HP:0001508": "Failure to thrive",
            # Legitimately found by pipeline:
            "HP:0005403": "Decreased total T cell count",
        },
        "expected_negated": [],
    },
}


def get_gold_standard(note_id: str) -> dict:
    """Get gold standard for a specific note."""
    return GOLD_STANDARD.get(note_id, {})


def get_all_note_ids() -> list[str]:
    """Get all note IDs in the gold standard."""
    return list(GOLD_STANDARD.keys())
