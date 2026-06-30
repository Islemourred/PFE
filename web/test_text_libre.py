"""Test text libre with different content types."""
import requests

text = (
    "Le patient presente une hypotonie axiale un retard psychomoteur "
    "et des crises epileptiques depuis age de 3 mois. "
    "Temperature 39.2 degres Celsius frequence cardiaque 118 battements par minute. "
    "Hemoglobine 8.2 g dL normale 11.5 a 15.5. CRP 145 mg L. "
    "Immunoglobulines IgG 0.12 g L. "
    "Diagnostic principal Agammaglobulinemie liee a l X maladie de Bruton."
)

# Test 1: form-urlencoded
print("=== Test 1: form-urlencoded ===")
try:
    r = requests.post("http://localhost:5000/api/pipeline/run",
        data={"text": text}, timeout=10)
    print(f"Status: {r.status_code}, Response: {r.text[:300]}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: JSON
print("\n=== Test 2: JSON ===")
try:
    r = requests.post("http://localhost:5000/api/pipeline/run",
        json={"text": text}, timeout=10)
    print(f"Status: {r.status_code}, Response: {r.text[:300]}")
except Exception as e:
    print(f"Error: {e}")
