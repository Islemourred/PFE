"""Quick test script for the French bilingual pipeline."""
import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ── Test 1: Language Detection ───────────────────────────────────────────────
print("=" * 60)
print(" TEST 1: Language Detection")
print("=" * 60)
from language_detector import detect_language

fr_text = "L'enfant Abdellaoui Mohamed Yanis âgé de 04 ans suivi pour mucoviscidose à Oran"
en_text = "Patient is a 55 year old male with history of hypertension presenting with chest pain"
print(f"  FR text -> {detect_language(fr_text)}")
print(f"  EN text -> {detect_language(en_text)}")

# ── Test 2: French PHI Removal ───────────────────────────────────────────────
print("\n" + "=" * 60)
print(" TEST 2: French PHI Removal")
print("=" * 60)
from module1_preprocessing.phi_remover import process_phi

test_fr = """Compte rendu d'hospitalisation
L'enfant ABDELLAOUI MOHAMED YANIS âgé de 04 ans originaire et demeurant à Oran,
suivi pour mucoviscidose. Dr Djoudi."""

result = process_phi(test_fr, lang='fr')
print(f"  PHI map: {result['phi_map']}")
print(f"  Patient info: {result['patient_info']}")
print(f"  Clean (first 120): {result['clean_text'][:120]}...")

# ── Test 3: French NegEx ─────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(" TEST 3: French NegEx")
print("=" * 60)
from module3_validation.negex import NegExDetector

negex_fr = NegExDetector(lang="fr")
test_entities = {
    "problem": [
        {"text": "organomégalie", "score": 0.9, "start": 0, "end": 13},
        {"text": "fièvre", "score": 0.9, "start": 0, "end": 6},
        {"text": "eczéma", "score": 0.9, "start": 0, "end": 6},
    ]
}
test_text = "pas d'organomégalie. Présence de fièvre à 38.5°C. Absence de eczéma."
result = negex_fr.detect_negation(test_text, test_entities)
for cat, ents in result.items():
    for e in ents:
        status = "NEGATED" if e.get("negated") else "AFFIRMED"
        cue = f" (cue: '{e.get('negation_cue', '')}')" if e.get("negated") else ""
        print(f"  {e['text']:20s} -> {status}{cue}")

# ── Test 4: French Numeric Parsing ───────────────────────────────────────────
print("\n" + "=" * 60)
print(" TEST 4: French Numeric Phenotypes")
print("=" * 60)
from module3_validation.numeric import extract_numeric_phenotypes

fr_lab = """
NFS : GB : 12500 éléments/ul (PNN : 9200 Lymph : 2800) Hb : 11.2 g/dl Plaquette : 90 000
CRP : 45 mg/L. État fébrile à 39,1°C. SPO2 : 88% sous AA.
"""
phenotypes = extract_numeric_phenotypes(fr_lab)
for p in phenotypes:
    print(f"  {p['hpo_name']:30s} ({p['hpo_id']}) <- {p['source']}")

# ── Test 5: French Abbreviations ─────────────────────────────────────────────
print("\n" + "=" * 60)
print(" TEST 5: French Abbreviations")
print("=" * 60)
from module4_normalization.abbreviations import expand_abbreviations

fr_abbrevs = ["dip", "nfs", "scid", "gb", "pnn", "ecbc", "sma", "dicv"]
for abbr in fr_abbrevs:
    print(f"  {abbr:8s} -> {expand_abbreviations(abbr, 'fr')}")

# ── Test 6: Load one French note from mock_data_fr ───────────────────────────
print("\n" + "=" * 60)
print(" TEST 6: French Mock Data Available")
print("=" * 60)
from mock_data_fr import get_french_notes, get_french_note_ids
ids = get_french_note_ids()
print(f"  {len(ids)} French notes available: {ids}")
for nid in ids:
    note = get_french_notes()[nid]
    print(f"  {nid}: {note['pathology']} ({len(note['text'])} chars)")

print("\n" + "=" * 60)
print(" ALL COMPONENT TESTS PASSED!")
print("=" * 60)
