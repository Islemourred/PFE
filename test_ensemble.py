"""Quick test of the 3-model English NER ensemble."""
import sys
sys.stdout.reconfigure(encoding="utf-8")

from module2_extraction.clinical_ner import ClinicalNER

print("Loading 3-model ensemble (DeBERTa + d4data + ClinicalBERT)...")
ner = ClinicalNER(lang="en")
print("Models loaded!\n")

text = ("The patient presents with recurrent fever, eczema, thrombocytopenia, "
        "and bloody diarrhea. Laboratory tests showed severe anemia. "
        "Treatment includes immunoglobulin replacement therapy.")

print(f"Input: {text}\n")
result = ner(text)

for cat in ["problem", "treatment", "test"]:
    entities = result.get(cat, [])
    print(f"  {cat}: {len(entities)} entities")
    for e in entities:
        src = e.get("source", "?")
        print(f"    - '{e['text']}' (score={e['score']}, source={src})")
    print()
