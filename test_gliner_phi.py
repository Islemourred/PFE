"""
Test: GLiNER Zero-Shot for French PHI De-identification
Compares GLiNER (AI-based) vs Regex (rule-based) approaches.

Uses the same CamemBERT-bio GLiNER model already loaded in Module 2,
but with PHI-specific labels instead of clinical entity labels.
"""

import re
import time
from gliner import GLiNER

# ═══════════════════════════════════════════════════════════════════════════
# TEST DATA — 3 French clinical notes with known PHI
# ═══════════════════════════════════════════════════════════════════════════

TEST_NOTES = {
    "NOTE_FR_001": {
        "text": """Compte rendu d'hospitalisation
      L'enfant ABDELLAOUI MOHAMED YANIS âgé de 04 ans et demi originaire et demeurant à Oran, suivi depuis l'âge de 03 mois pour une mucoviscidose.
ANTECEDENTS :
Familiaux :
- Père : 41ans ; BES.
- Mère : 27 ans, BES.
- Consanguinité de 2eme degré.
EXAMEN CLINIQUE À L'ADMISSION : Date : 24/03/2026
Mesures anthropométriques :
Poids : 13,600 kg (-1,79 DS). Taille : 100 cm (-1,43 DS).
État général moyen, fébrile : T : 38,7° C.
NFS : GB : 12500 éléments/ul Hb : 11.2 g/dl
CRP : 45 mg/L
ECBC : Pseudomonas Aeruginosa sensible à la Colistine.""",
        "expected_phi": {
            "PATIENT": "ABDELLAOUI MOHAMED YANIS",
            "LOCATION": "Oran",
            "DATE": "24/03/2026",
        },
    },

    "NOTE_FR_003": {
        "text": """Fiche de Ré hospitalisation :
C'est l'enfant AZZEMMOU MAHDI né le 23/04/2016, âgé actuellement de 9 ans et 7 mois, originaire et demeurant à MOSTAGANEM, issu d'un couple non consanguin, suivi à l'EPH BOUGUIRAT MOSTAGANEM depuis 2022 pour un déficit immunitaire primitif type agammaglobulinémie congénitale, hospitalisé à notre niveau ce jour pour la cure d'immunoglobulines N : 43.
EXAMEN CLINIQUE À L'ADMISSION : 25/03/2026
État général conservé, apyrétique : T° 36.7 C.""",
        "expected_phi": {
            "PATIENT": "AZZEMMOU MAHDI",
            "LOCATION": "MOSTAGANEM",
            "DATE": ["23/04/2016", "25/03/2026"],
            "HOSPITAL": "EPH BOUGUIRAT MOSTAGANEM",
        },
    },

    "NOTE_FR_004": {
        "text": """FICHE D'HOSPITALISATION:
Il s'agit du nourrisson Tazi Mimoun Abderrahmane, âgé de 14 mois originaire et demeurant à Saida, issu d'un couple consanguin de 2ème degré, suivi depuis l'âge de 05 mois pour déficit immunitaire combiné sévère atypique, orienté depuis l'EPH de Saida pour complément de suivi.
ANTÉCÉDENTS :
Familiaux :
Père : 41ans, bon état de santé.
Mère : 33ans, bon état de santé.
Diagnostic principal : Déficit immunitaire combiné sévère atypique
Date de diagnostic : 04/2025
EXAMEN CLINIQUE À L'ADMISSION :
Poids: 06kg600 (-3.67DS) Taille: 67cm (-4.7DS)
NFS : GB: 8200 Hb: 9.8 g/dl Plaquettes: 340000
CRP: 12 mg/L""",
        "expected_phi": {
            "PATIENT": "Tazi Mimoun Abderrahmane",
            "LOCATION": "Saida",
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# METHOD 1: GLiNER Zero-Shot PHI Detection
# ═══════════════════════════════════════════════════════════════════════════

def gliner_phi_detection(model, text: str) -> dict:
    """
    Use GLiNER zero-shot NER to detect PHI in French clinical text.
    Define PHI-specific labels at inference time.
    """
    # PHI labels for zero-shot detection
    phi_labels = [
        "nom de personne",          # patient/doctor names
        "date",                     # dates
        "lieu",                     # location/city
        "hôpital",                  # hospital name
        "numéro de téléphone",      # phone number
        "numéro de dossier",        # medical record number
    ]

    entities = model.predict_entities(
        text,
        phi_labels,
        threshold=0.3,       # lower threshold to catch more PHI
        flat_ner=True,
    )

    # Group by category
    phi_map = {}
    for ent in entities:
        label = ent["label"]
        value = ent["text"].strip()
        score = round(float(ent["score"]), 3)

        if label not in phi_map:
            phi_map[label] = []
        phi_map[label].append({"value": value, "score": score})

    return phi_map


# ═══════════════════════════════════════════════════════════════════════════
# METHOD 2: Regex PHI Detection (current approach)
# ═══════════════════════════════════════════════════════════════════════════

FR_PHI_PATTERNS = {
    "PATIENT": [
        r"(?:Patient|Pt|L'enfant|Le nourrisson|La patiente|Il s'agit (?:de l'enfant|du (?:nourrisson|patient))|C'est (?:l'enfant|le patient|la patiente))\s*[:\s]*([A-ZÀÂÉÈÊËÏÎÔÙÛÜÇ][a-zàâéèêëïîôùûüç]+(?:\s+[A-ZÀÂÉÈÊËÏÎÔÙÛÜÇ][a-zàâéèêëïîôùûüç]+){1,4})",
        r"(?:Nom et prénom)\s*[:\s]*([A-ZÀÂÉÈÊËÏÎÔÙÛÜÇ][A-ZÀÂÉÈÊËÏÎÔÙÛÜÇa-zàâéèêëïîôùûüç]+(?:\s+[A-ZÀÂÉÈÊËÏÎÔÙÛÜÇa-zàâéèêëïîôùûüç]+){1,4})",
    ],
    "DATE": [
        r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b",
        r"\b(\d{1,2}-\d{1,2}-\d{4})\b",
        r"\b(\d{4}-\d{1,2}-\d{1,2})\b",
    ],
    "LOCATION": [
        r"(?:originaire et demeurant à|demeurant à|originaire de)\s+([A-ZÀÂÉÈÊËÏÎÔÙÛÜÇ][A-ZÀÂÉÈÊËÏÎÔÙÛÜÇa-zàâéèêëïîôùûüç\s\-']+?)(?:\s*[,.\n])",
    ],
    "HOSPITAL": [
        r"(?:EPH|CHU|EHU|Hôpital)\s+([A-ZÀÂÉÈÊËÏÎÔÙÛÜÇ][^\n,]{2,30}?)(?:\s*[,.\n])",
    ],
    "PHONE": [
        r"(?:Tél|Tel|Téléphone)\s*[:\s]*([\d\s./-]{8,20})",
        r"\b(0[567]\.\d{2}\.\d{2}\.\d{2}\.\d{2})\b",
    ],
}


def regex_phi_detection(text: str) -> dict:
    """Detect PHI using regex patterns (current Module 1 approach)."""
    phi_map = {}
    for category, patterns in FR_PHI_PATTERNS.items():
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                value = match.group(1).strip()
                if not value or len(value) < 2:
                    continue
                if category not in phi_map:
                    phi_map[category] = []
                # Avoid duplicates
                if not any(v["value"] == value for v in phi_map[category]):
                    phi_map[category].append({"value": value, "score": 1.0})
    return phi_map


# ═══════════════════════════════════════════════════════════════════════════
# COMPARISON
# ═══════════════════════════════════════════════════════════════════════════

def print_results(note_id, expected, gliner_results, regex_results):
    """Pretty-print comparison results."""
    print(f"\n{'='*80}")
    print(f"  {note_id}")
    print(f"{'='*80}")

    print(f"\n  [EXPECTED PHI]:")
    for cat, val in expected.items():
        if isinstance(val, list):
            for v in val:
                print(f"     [{cat}] {v}")
        else:
            print(f"     [{cat}] {val}")

    print(f"\n  [GLINER RESULTS]:")
    if gliner_results:
        for cat, entities in gliner_results.items():
            for e in entities:
                print(f"     [{cat}] {e['value']}  (score: {e['score']})")
    else:
        print(f"     (no entities detected)")

    print(f"\n  [REGEX RESULTS]:")
    if regex_results:
        for cat, entities in regex_results.items():
            for e in entities:
                print(f"     [{cat}] {e['value']}  (score: {e['score']})")
    else:
        print(f"     (no entities detected)")


def main():
    print("=" * 80)
    print("  GLiNER vs Regex — French PHI De-identification Comparison")
    print("=" * 80)

    # Load GLiNER model
    print("\n>> Loading GLiNER model (almanach/camembert-bio-gliner-v0.1)...")
    t0 = time.time()
    model = GLiNER.from_pretrained("almanach/camembert-bio-gliner-v0.1")
    print(f"[OK] Model loaded in {time.time() - t0:.1f}s\n")

    gliner_total_time = 0
    regex_total_time = 0

    for note_id, note_data in TEST_NOTES.items():
        text = note_data["text"]
        expected = note_data["expected_phi"]

        # GLiNER
        t1 = time.time()
        gliner_results = gliner_phi_detection(model, text)
        gliner_time = time.time() - t1
        gliner_total_time += gliner_time

        # Regex
        t2 = time.time()
        regex_results = regex_phi_detection(text)
        regex_time = time.time() - t2
        regex_total_time += regex_time

        print_results(note_id, expected, gliner_results, regex_results)

        print(f"\n  TIME >>  GLiNER: {gliner_time:.3f}s  |  Regex: {regex_time:.6f}s")

    # Summary
    print(f"\n{'='*80}")
    print(f"  SUMMARY")
    print(f"{'='*80}")
    print(f"  Total GLiNER time : {gliner_total_time:.3f}s")
    print(f"  Total Regex time  : {regex_total_time:.6f}s")
    print(f"  Speed ratio       : Regex is {gliner_total_time/max(regex_total_time, 0.0001):.0f}x faster")
    print()


if __name__ == "__main__":
    main()
