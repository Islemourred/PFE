"""
French Medical Term → HPO Mapping (Hybrid: Official Database + Curated)

Mapping sources (priority order):
  1. Curated CHU Oran mappings (160+ entries, highest precision)
  2. Official HPO French translations (25,000+ from Orphanet/INSERM)

For deployment: any clinical term in any French medical note will be matched
against the full Orphanet French ontology, not just CHU-specific templates.
"""

from log_config import get_logger

logger = get_logger(__name__)

# ── Curated high-precision mappings (overrides) ─────────────────────────────
# These are hand-verified for CHU Oran reports and always take priority
CURATED_FR_HPO = {
    # ══════════════════════════════════════════════════════════════════════
    # Immunology / DIP
    # ══════════════════════════════════════════════════════════════════════
    "déficit immunitaire": ("HP:0004430", "Immunodeficiency"),
    "déficit immunitaire primitif": ("HP:0004430", "Immunodeficiency"),
    "déficit immunitaire combiné": ("HP:0004430", "Severe combined immunodeficiency"),
    "déficit immunitaire combiné sévère": ("HP:0004430", "Severe combined immunodeficiency"),
    "déficit immunitaire commun variable": ("HP:0004430", "Immunodeficiency"),
    "dicv": ("HP:0004430", "Immunodeficiency"),
    "dics": ("HP:0004430", "Severe combined immunodeficiency"),
    "scid": ("HP:0004430", "Severe combined immunodeficiency"),
    "dip": ("HP:0004430", "Immunodeficiency"),
    "agammaglobulinémie": ("HP:0004432", "Agammaglobulinemia"),
    "hypogammaglobulinémie": ("HP:0004313", "Decreased circulating antibody level"),
    "immunodéficience": ("HP:0004430", "Immunodeficiency"),
    "immunodéficience cellulaire": ("HP:0005374", "Cellular immunodeficiency"),

    # ══════════════════════════════════════════════════════════════════════
    # Infections
    # ══════════════════════════════════════════════════════════════════════
    "infections respiratoires à répétition": ("HP:0002205", "Recurrent respiratory infections"),
    "infections pulmonaires récurrentes": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "infections pulmonaires récidivantes": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "broncho-pneumopathies à répétition": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "surinfection bronchique": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "surinfection pulmonaire": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "exacerbation pulmonaire": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "exacerbation respiratoire": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "exacerbation de sa maladie": ("HP:0006538", "Recurrent bronchopulmonary infections"),
    "pneumopathie": ("HP:0002090", "Pneumonia"),
    "pneumonie": ("HP:0002090", "Pneumonia"),
    "bronchopneumopathie": ("HP:0002090", "Pneumonia"),
    "foyer pulmonaire": ("HP:0002090", "Pneumonia"),
    "dilatation des bronches": ("HP:0002110", "Bronchiectasis"),
    "bronchectasie": ("HP:0002110", "Bronchiectasis"),
    "bronchiectasie": ("HP:0002110", "Bronchiectasis"),
    "ddb": ("HP:0002110", "Bronchiectasis"),
    "encombrement bronchique": ("HP:0002104", "Apnea"),
    "toux grasse": ("HP:0012735", "Cough"),
    "toux productive": ("HP:0012735", "Cough"),
    "toux": ("HP:0012735", "Cough"),
    "expectoration": ("HP:0012735", "Cough"),
    "crachats": ("HP:0012735", "Cough"),
    "crachats verdâtres": ("HP:0012735", "Cough"),
    "otite": ("HP:0000388", "Otitis media"),
    "otites purulentes": ("HP:0000388", "Otitis media"),
    "otite moyenne": ("HP:0000388", "Otitis media"),
    "candidose buccale": ("HP:0002719", "Recurrent infections"),
    "candidose": ("HP:0002719", "Recurrent infections"),
    "bcgite": ("HP:0002719", "Recurrent infections"),
    "infections à répétition": ("HP:0002719", "Recurrent infections"),
    "infections récurrentes": ("HP:0002719", "Recurrent infections"),
    "infections récidivantes": ("HP:0002719", "Recurrent infections"),
    "fièvre prolongée": ("HP:0001945", "Fever"),
    "méningite": ("HP:0001287", "Meningitis"),
    "sepsis": ("HP:0100806", "Sepsis"),
    "abcès": ("HP:0025615", "Abscess"),
    "abcès pulmonaire": ("HP:0025615", "Abscess"),
    "sinusite": ("HP:0000246", "Sinusitis"),

    # ══════════════════════════════════════════════════════════════════════
    # Respiratory
    # ══════════════════════════════════════════════════════════════════════
    "insuffisance respiratoire": ("HP:0002093", "Respiratory insufficiency"),
    "insuffisance respiratoire chronique": ("HP:0002093", "Respiratory insufficiency"),
    "irc": ("HP:0002093", "Respiratory insufficiency"),
    "détresse respiratoire": ("HP:0002098", "Respiratory distress"),
    "dyspnée": ("HP:0002094", "Dyspnea"),
    "dyspnée sifflante": ("HP:0002094", "Dyspnea"),
    "tirage": ("HP:0002098", "Respiratory distress"),
    "wheezing": ("HP:0030828", "Wheezing"),
    "sibilants": ("HP:0030828", "Wheezing"),
    "râles crépitants": ("HP:0030829", "Crackles"),
    "crépitants": ("HP:0030829", "Crackles"),
    "rhinite allergique": ("HP:0003193", "Allergic rhinitis"),
    "rhinite": ("HP:0003193", "Allergic rhinitis"),
    "asthme": ("HP:0002099", "Asthma"),
    "syndrome obstructif": ("HP:0006510", "Chronic obstructive pulmonary disease"),
    "bpco": ("HP:0006510", "Chronic obstructive pulmonary disease"),
    "syndrome bronchique": ("HP:0002110", "Bronchiectasis"),
    "épaississement des parois bronchiques": ("HP:0002110", "Bronchiectasis"),
    "épaississement bronchique": ("HP:0002110", "Bronchiectasis"),
    "verre dépoli": ("HP:0006530", "Abnormal pulmonary interstitial morphology"),
    "aspect en verre dépoli": ("HP:0006530", "Abnormal pulmonary interstitial morphology"),
    "condensation pulmonaire": ("HP:0002090", "Pneumonia"),
    "hippocratisme digital": ("HP:0100759", "Clubbing of fingers"),
    "clubbing": ("HP:0100759", "Clubbing of fingers"),
    "déformation thoracique": ("HP:0000767", "Pectus excavatum"),
    "thorax en carène": ("HP:0000768", "Pectus carinatum"),
    "thorax en entonnoir": ("HP:0000767", "Pectus excavatum"),
    "adénomégalie médiastinale": ("HP:0100721", "Mediastinal lymphadenopathy"),
    "adénopathie médiastinale": ("HP:0100721", "Mediastinal lymphadenopathy"),
    "adénopathie": ("HP:0002716", "Lymphadenopathy"),
    "adp cervicale": ("HP:0002716", "Lymphadenopathy"),
    "hémoptysie": ("HP:0002105", "Hemoptysis"),
    "emphysème": ("HP:0002097", "Emphysema"),

    # ══════════════════════════════════════════════════════════════════════
    # Dermatology
    # ══════════════════════════════════════════════════════════════════════
    "eczéma": ("HP:0000964", "Eczema"),
    "dermatite": ("HP:0000964", "Eczema"),
    "ecchymoses": ("HP:0000978", "Bruising susceptibility"),
    "pétéchies": ("HP:0000967", "Petechiae"),
    "pâleur cutanéo-muqueuse": ("HP:0000980", "Pallor"),
    "pâleur cutanée": ("HP:0000980", "Pallor"),
    "pâleur": ("HP:0000980", "Pallor"),
    "ictère": ("HP:0000952", "Jaundice"),
    "télangiectasie": ("HP:0001009", "Telangiectasia"),
    "télangiectasies": ("HP:0001009", "Telangiectasia"),
    "éruption cutanée": ("HP:0000988", "Skin rash"),
    "purpura": ("HP:0000979", "Purpura"),
    "hirsutisme": ("HP:0001007", "Hirsutism"),

    # ══════════════════════════════════════════════════════════════════════
    # Growth / Nutrition
    # ══════════════════════════════════════════════════════════════════════
    "retard staturo-pondéral": ("HP:0001508", "Failure to thrive"),
    "retard pondéral": ("HP:0001508", "Failure to thrive"),
    "cassure de la courbe de poids": ("HP:0001508", "Failure to thrive"),
    "rsp": ("HP:0001508", "Failure to thrive"),
    "retard de croissance": ("HP:0001508", "Failure to thrive"),
    "retard de croissance staturo-pondéral": ("HP:0001508", "Failure to thrive"),
    "malnutrition": ("HP:0004395", "Malnutrition"),
    "dénutrition": ("HP:0004395", "Malnutrition"),
    "amaigrissement": ("HP:0001824", "Weight loss"),
    "perte de poids": ("HP:0001824", "Weight loss"),
    "déshydratation": ("HP:0001944", "Dehydration"),
    "retard statural": ("HP:0004322", "Short stature"),
    "petite taille": ("HP:0004322", "Short stature"),
    "nanisme": ("HP:0004322", "Short stature"),
    "obésité": ("HP:0001513", "Obesity"),
    "surpoids": ("HP:0001513", "Obesity"),

    # ══════════════════════════════════════════════════════════════════════
    # Gastrointestinal
    # ══════════════════════════════════════════════════════════════════════
    "diarrhée chronique": ("HP:0002035", "Chronic diarrhea"),
    "diarrhée": ("HP:0002014", "Diarrhea"),
    "stéatorrhée": ("HP:0002570", "Steatorrhea"),
    "selles grasses": ("HP:0002570", "Steatorrhea"),
    "hépatomégalie": ("HP:0002240", "Hepatomegaly"),
    "splénomégalie": ("HP:0001744", "Splenomegaly"),
    "hépatosplénomégalie": ("HP:0001433", "Hepatosplenomegaly"),
    "insuffisance pancréatique": ("HP:0001738", "Exocrine pancreatic insufficiency"),
    "insuffisance pancréatique exocrine": ("HP:0001738", "Exocrine pancreatic insufficiency"),
    "ipe": ("HP:0001738", "Exocrine pancreatic insufficiency"),
    "prolapsus rectal": ("HP:0002035", "Chronic diarrhea"),
    "reflux gastro-oesophagien": ("HP:0002020", "Gastroesophageal reflux"),
    "rgo": ("HP:0002020", "Gastroesophageal reflux"),
    "distension abdominale": ("HP:0003270", "Abdominal distention"),
    "ballonnement abdominal": ("HP:0003270", "Abdominal distention"),
    "constipation": ("HP:0002019", "Constipation"),
    "iléus méconial": ("HP:0004397", "Meconium ileus"),
    "malabsorption": ("HP:0002024", "Malabsorption"),
    "vomissements": ("HP:0002013", "Vomiting"),

    # ══════════════════════════════════════════════════════════════════════
    # Hematology
    # ══════════════════════════════════════════════════════════════════════
    "anémie": ("HP:0001903", "Anemia"),
    "anémie hémolytique": ("HP:0001878", "Hemolytic anemia"),
    "thrombopénie": ("HP:0001873", "Thrombocytopenia"),
    "thrombocytopénie": ("HP:0001873", "Thrombocytopenia"),
    "lymphopénie": ("HP:0001888", "Lymphopenia"),
    "neutropénie": ("HP:0001875", "Neutropenia"),
    "pancytopénie": ("HP:0001876", "Pancytopenia"),
    "hyperleucocytose": ("HP:0001974", "Leukocytosis"),
    "leucocytose": ("HP:0001974", "Leukocytosis"),
    "syndrome hémorragique": ("HP:0001892", "Abnormal bleeding"),
    "saignement": ("HP:0001892", "Abnormal bleeding"),
    "épistaxis": ("HP:0000421", "Epistaxis"),

    # ══════════════════════════════════════════════════════════════════════
    # Fever / General
    # ══════════════════════════════════════════════════════════════════════
    "fièvre": ("HP:0001945", "Fever"),
    "hyperthermie": ("HP:0001945", "Fever"),
    "fièvre prolongée": ("HP:0001945", "Fever"),
    "sueurs nocturnes": ("HP:0030166", "Night sweats"),
    "asthénie": ("HP:0012378", "Fatigue"),
    "fatigue": ("HP:0012378", "Fatigue"),
    "altération de l'état général": ("HP:0012378", "Fatigue"),
    "aeg": ("HP:0012378", "Fatigue"),
    "apyrétique": None,  # Negation — explicitly exclude

    # ══════════════════════════════════════════════════════════════════════
    # Neurology
    # ══════════════════════════════════════════════════════════════════════
    "ataxie": ("HP:0001251", "Ataxia"),
    "ataxie cérébelleuse": ("HP:0001251", "Cerebellar ataxia"),
    "hypotonie": ("HP:0001252", "Muscular hypotonia"),
    "hypotonie axiale": ("HP:0001252", "Muscular hypotonia"),
    "retard psychomoteur": ("HP:0001263", "Global developmental delay"),
    "retard du développement psychomoteur": ("HP:0001263", "Global developmental delay"),
    "retard de développement": ("HP:0001263", "Global developmental delay"),
    "convulsions": ("HP:0001250", "Seizure"),
    "crises convulsives": ("HP:0001250", "Seizure"),
    "épilepsie": ("HP:0001250", "Seizure"),
    "nystagmus": ("HP:0000639", "Nystagmus"),
    "dysarthrie": ("HP:0001260", "Dysarthria"),
    "spasticité": ("HP:0001257", "Spasticity"),
    "amyotrophie": ("HP:0003202", "Skeletal muscle atrophy"),
    "atrophie musculaire": ("HP:0003202", "Skeletal muscle atrophy"),

    # ══════════════════════════════════════════════════════════════════════
    # Ophthalmology
    # ══════════════════════════════════════════════════════════════════════
    "conjonctivite": ("HP:0000509", "Conjunctivitis"),
    "kératite": ("HP:0000491", "Keratitis"),
    "strabisme": ("HP:0000486", "Strabismus"),

    # ══════════════════════════════════════════════════════════════════════
    # Cardiology
    # ══════════════════════════════════════════════════════════════════════
    "souffle cardiaque": ("HP:0030148", "Heart murmur"),
    "cardiomyopathie": ("HP:0001638", "Cardiomyopathy"),
    "hypertension artérielle pulmonaire": ("HP:0002092", "Pulmonary arterial hypertension"),
    "htap": ("HP:0002092", "Pulmonary arterial hypertension"),
    "htp": ("HP:0002092", "Pulmonary arterial hypertension"),
    "cœur pulmonaire": ("HP:0001648", "Cor pulmonale"),

    # ══════════════════════════════════════════════════════════════════════
    # Genetics
    # ══════════════════════════════════════════════════════════════════════
    "consanguinité": ("HP:0000031", "Consanguinity"),
    "consanguin": ("HP:0000031", "Consanguinity"),
    "mucoviscidose": ("HP:0006538", "Recurrent bronchopulmonary infections"),

    # ══════════════════════════════════════════════════════════════════════
    # Immunoglobulins
    # ══════════════════════════════════════════════════════════════════════
    "hyper-ige": ("HP:0003212", "Increased circulating IgE level"),
    "hyper ige": ("HP:0003212", "Increased circulating IgE level"),
    "ige élevé": ("HP:0003212", "Increased circulating IgE level"),
    "augmentation des ige": ("HP:0003212", "Increased circulating IgE level"),
    "déficit en igg": ("HP:0004315", "Decreased circulating IgG level"),
    "déficit en iga": ("HP:0002720", "Decreased circulating IgA level"),
    "déficit en igm": ("HP:0002850", "Decreased circulating IgM level"),
    "diminution des igg": ("HP:0004315", "Decreased circulating IgG level"),
    "diminution des iga": ("HP:0002720", "Decreased circulating IgA level"),
    "diminution des igm": ("HP:0002850", "Decreased circulating IgM level"),

    # ══════════════════════════════════════════════════════════════════════
    # Lab findings (sweat test etc.)
    # ══════════════════════════════════════════════════════════════════════
    "test de la sueur positif": ("HP:0031956", "Elevated sweat chloride"),
    "test de sueur positif": ("HP:0031956", "Elevated sweat chloride"),
    "chlore sudoral élevé": ("HP:0031956", "Elevated sweat chloride"),
    "taux du chlore": ("HP:0031956", "Elevated sweat chloride"),
    "diabète": ("HP:0000819", "Diabetes mellitus"),
    "did": ("HP:0000819", "Diabetes mellitus"),

    # ══════════════════════════════════════════════════════════════════════
    # ENT / Dental
    # ══════════════════════════════════════════════════════════════════════
    "surdité": ("HP:0000365", "Hearing impairment"),
    "polypes nasaux": ("HP:0100582", "Nasal polyposis"),
    "polypose nasale": ("HP:0100582", "Nasal polyposis"),
    "caries dentaires": ("HP:0000670", "Carious teeth"),
    "arthrite": ("HP:0001369", "Arthritis"),
    "arthralgie": ("HP:0002829", "Arthralgia"),
    "douleur articulaire": ("HP:0002829", "Arthralgia"),

    # ══════════════════════════════════════════════════════════════════════
    # Skeletal
    # ══════════════════════════════════════════════════════════════════════
    "ostéoporose": ("HP:0000939", "Osteoporosis"),
    "fracture pathologique": ("HP:0002757", "Recurrent fractures"),
    "scoliose": ("HP:0002650", "Scoliosis"),
    "phimosis": ("HP:0001741", "Phimosis"),
}

# ── Curated French→English translations (for SapBERT fallback) ──────────
CURATED_FR_EN = {
    "kinésithérapie": "physiotherapy",
    "kinésithérapie respiratoire": "respiratory physiotherapy",
    "nébulisation": "nebulization",
    "antibiothérapie": "antibiotic therapy",
    "cure d'immunoglobuline": "immunoglobulin therapy",
    "bilan immunologique": "immunological workup",
    "examen clinique": "clinical examination",
    "numération formule sanguine": "complete blood count",
    "protéine c réactive": "C-reactive protein",
    "saturation en oxygène": "oxygen saturation",
    "apyrétique": "afebrile",
    # Additional clinical translations
    "encombrement bronchique": "bronchial congestion",
    "syndrome bronchique": "bronchial syndrome",
    "exacerbation": "exacerbation",
    "surinfection": "superinfection",
    "hippocratisme digital": "digital clubbing",
    "déformation thoracique": "thoracic deformity",
    "épaississement des parois bronchiques": "bronchial wall thickening",
    "bronchectasie": "bronchiectasis",
    "dilatation des bronches": "bronchiectasis",
    "stéatorrhée": "steatorrhea",
    "retard staturo-pondéral": "failure to thrive",
    "insuffisance pancréatique exocrine": "exocrine pancreatic insufficiency",
    "reflux gastro-oesophagien": "gastroesophageal reflux",
    "hémoptysie": "hemoptysis",
    "hyperleucocytose": "leukocytosis",
    "thrombocytopénie": "thrombocytopenia",
    "hépatosplénomégalie": "hepatosplenomegaly",
    "amyotrophie": "muscle atrophy",
    "télangiectasie": "telangiectasia",
    "polypose nasale": "nasal polyposis",
}

# ── Dynamic mappings (loaded from official HPO French database) ──────────
_dynamic_fr_hpo = None
_dynamic_fr_en = None
_loaded = False


def _ensure_loaded():
    """Lazy-load the official HPO French database (25,000+ terms)."""
    global _dynamic_fr_hpo, _dynamic_fr_en, _loaded
    if _loaded:
        return

    try:
        from module4_normalization.french_hpo_loader import load_french_hpo
        _dynamic_fr_hpo, _dynamic_fr_en = load_french_hpo()
        logger.info("  French HPO: %d curated + %d official Orphanet labels",
                     len(CURATED_FR_HPO), len(_dynamic_fr_hpo) if _dynamic_fr_hpo else 0)
    except Exception as e:
        logger.warning("  Official French HPO database not available: %s", e)
        _dynamic_fr_hpo = {}
        _dynamic_fr_en = {}

    _loaded = True


def lookup_french_hpo(term: str):
    """
    Look up a French clinical term → HPO ID.

    Priority:
      1. Curated CHU Oran mappings (hand-verified, highest precision)
      2. Official HPO French labels (25,000+ from Orphanet/INSERM)
      3. Substring matching in both dictionaries
    """
    lower = term.strip().lower()

    # Priority 1: Curated exact match
    if lower in CURATED_FR_HPO:
        mapping = CURATED_FR_HPO[lower]
        if mapping is None:
            return None
        return {
            "hpo_id": mapping[0], "hpo_name": mapping[1],
            "match_type": "french_curated", "confidence": 0.95,
        }

    # Priority 2: Official HPO French database
    _ensure_loaded()
    if _dynamic_fr_hpo and lower in _dynamic_fr_hpo:
        mapping = _dynamic_fr_hpo[lower]
        return {
            "hpo_id": mapping[0], "hpo_name": mapping[1],
            "match_type": "french_orphanet", "confidence": 0.92,
        }

    # Priority 3: Substring matching (curated first, then official)
    best_match = None
    best_len = 0

    for key, mapping in CURATED_FR_HPO.items():
        if mapping is None:
            continue
        if key in lower and len(key) > best_len:
            best_match = mapping
            best_len = len(key)

    if _dynamic_fr_hpo:
        for key, mapping in _dynamic_fr_hpo.items():
            if key in lower and len(key) > best_len:
                best_match = mapping
                best_len = len(key)

    if best_match and best_len >= 4:
        return {
            "hpo_id": best_match[0], "hpo_name": best_match[1],
            "match_type": "french_partial", "confidence": 0.85,
        }

    return None


def translate_to_english(term: str) -> str:
    """
    Translate French clinical term to English for SapBERT fallback.

    Sources:
      1. Curated translations (highest precision)
      2. Official HPO French→English mappings (25,000+)
    """
    lower = term.strip().lower()

    # Priority 1: Curated
    if lower in CURATED_FR_EN:
        return CURATED_FR_EN[lower]

    # Priority 2: Official HPO database
    _ensure_loaded()
    if _dynamic_fr_en and lower in _dynamic_fr_en:
        return _dynamic_fr_en[lower]

    return term
