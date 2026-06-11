"""
Pre-Download All Models & Data

Downloads all 8 transformer models and 4 datasets required by the pipeline.
Run this ONCE with good internet, then everything works offline.

Usage:
    python download_all.py

Total download: ~4 GB (models) + ~42 MB (datasets)
"""

import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def download_models():
    """Download all 8 HuggingFace transformer models."""
    from transformers import AutoTokenizer, AutoModelForTokenClassification, AutoModelForSequenceClassification

    models = [
        # Module 1: De-identification
        ("obi/deid_roberta_i2b2", "EN De-ID (RoBERTa)", "token"),
        ("Jean-Baptiste/camembert-ner", "FR De-ID (CamemBERT)", "token"),

        # Module 2: NER
        ("Helios9/BioMed_NER", "EN NER Primary (DeBERTa-v3)", "token"),
        ("d4data/biomedical-ner-all", "EN NER Ensemble (BERT)", "token"),

        # Module 3: Negation
        ("bvanaken/clinical-assertion-negation-bert", "EN Negation (BioBERT)", "sequence"),
        ("MoritzLaurer/mDeBERTa-v3-base-mnli-xnli", "FR Negation (mDeBERTa)", "sequence"),

        # Module 4: Normalization
        ("cambridgeltl/SapBERT-from-PubMedBERT-fulltext", "SapBERT (PubMedBERT)", "token"),
    ]

    print("=" * 60)
    print("  DOWNLOADING TRANSFORMER MODELS (7 models)")
    print("=" * 60)

    for i, (model_name, description, model_type) in enumerate(models, 1):
        print(f"\n  [{i}/{len(models)}] {description}")
        print(f"  Model: {model_name}")
        start = time.time()

        try:
            print(f"    Downloading tokenizer...", end=" ", flush=True)
            AutoTokenizer.from_pretrained(model_name)
            print("OK")

            print(f"    Downloading model...", end=" ", flush=True)
            if model_type == "token":
                AutoModelForTokenClassification.from_pretrained(model_name)
            else:
                AutoModelForSequenceClassification.from_pretrained(model_name)
            print("OK")

            elapsed = round(time.time() - start, 1)
            print(f"    Done in {elapsed}s")

        except Exception as e:
            print(f"\n    [ERROR] {e}")

    # GLiNER (French NER) — separate download
    print(f"\n  [8/8] FR NER (CamemBERT-bio GLiNER)")
    print(f"  Model: almanach/camembert-bio-gliner-v0.1")
    try:
        start = time.time()
        from gliner import GLiNER
        print(f"    Downloading model...", end=" ", flush=True)
        GLiNER.from_pretrained("almanach/camembert-bio-gliner-v0.1")
        print(f"OK ({round(time.time() - start, 1)}s)")
    except Exception as e:
        print(f"\n    [ERROR] {e}")


def download_datasets():
    """Download all cached datasets (abbreviations, HPO, ORDO)."""
    print(f"\n{'='*60}")
    print("  DOWNLOADING DATASETS (4 datasets)")
    print("=" * 60)

    # 1. Medical abbreviations
    print("\n  [1/4] Medical abbreviations (3,911 entries)")
    try:
        from module4_normalization.abbreviation_loader import load_abbreviations
        abbrevs = load_abbreviations()
        print(f"    OK: {len(abbrevs)} entries")
    except Exception as e:
        print(f"    [ERROR] {e}")

    # 2. French HPO labels
    print("\n  [2/4] French HPO labels (25,054 entries)")
    try:
        from module4_normalization.french_hpo_loader import load_french_hpo
        fr_hpo = load_french_hpo()
        print(f"    OK: {len(fr_hpo)} entries")
    except Exception as e:
        print(f"    [ERROR] {e}")

    # 3. ORDO rare disease profiles
    print("\n  [3/4] ORDO rare disease profiles")
    try:
        from module4_normalization.ordo_loader import load_ordo_profiles
        ordo = load_ordo_profiles()
        print(f"    OK: {len(ordo)} entries")
    except Exception as e:
        print(f"    [ERROR] {e}")

    # 4. HPO terms (parsed from OWL)
    print("\n  [4/4] HPO terms cache")
    data_dir = os.path.join(PROJECT_ROOT, "data")
    hpo_path = os.path.join(data_dir, "hpo_terms.json")
    if os.path.exists(hpo_path):
        import json
        with open(hpo_path, "r", encoding="utf-8") as f:
            terms = json.load(f)
        print(f"    OK: {len(terms)} terms (cached)")
    else:
        print("    [!] hpo_terms.json not found — will be generated on first run")


def verify_all():
    """Quick verification that everything is accessible."""
    print(f"\n{'='*60}")
    print("  VERIFICATION")
    print("=" * 60)

    checks = [
        ("Transformers", "import transformers; print(f'    v{transformers.__version__}')"),
        ("PyTorch", "import torch; print(f'    v{torch.__version__}, CUDA: {torch.cuda.is_available()}')"),
        ("GLiNER", "import gliner; print('    OK')"),
        ("Streamlit", "import streamlit; print(f'    v{streamlit.__version__}')"),
        ("python-docx", "import docx; print('    OK')"),
        ("pysbd", "import pysbd; print('    OK')"),
        ("langdetect", "import langdetect; print('    OK')"),
        ("dateparser", "import dateparser; print('    OK')"),
    ]

    all_ok = True
    for name, check in checks:
        print(f"\n  {name}:", end="", flush=True)
        try:
            exec(check)
        except ImportError:
            print(f"    [MISSING] pip install {name.lower()}")
            all_ok = False

    # Check data files
    data_dir = os.path.join(PROJECT_ROOT, "data")
    print(f"\n  Data files:")
    data_files = [
        "medical_abbreviations.json",
        "hpo_french_labels.json",
        "hpo_fr_en_translations.json",
        "ordo_profiles.json",
        "hpo_terms.json",
    ]
    for f in data_files:
        path = os.path.join(data_dir, f)
        if os.path.exists(path):
            size = os.path.getsize(path) / 1024
            print(f"    {f:<35} {size:>8.0f} KB")
        else:
            print(f"    {f:<35} [MISSING]")
            all_ok = False

    # Check reports
    reports_dir = os.path.join(PROJECT_ROOT, "clinical_notes", "reports")
    if os.path.isdir(reports_dir):
        count = len([f for f in os.listdir(reports_dir) if f.endswith(".docx")])
        print(f"\n  CHU Reports: {count} files in clinical_notes/reports/")
    else:
        print(f"\n  CHU Reports: [MISSING] clinical_notes/reports/")

    return all_ok


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  CLINICAL PRE-ANALYSIS PIPELINE — FULL SETUP")
    print("  Downloading all models and datasets...")
    print("=" * 60)

    start = time.time()

    download_models()
    download_datasets()
    ok = verify_all()

    total = round(time.time() - start, 1)

    print(f"\n{'='*60}")
    if ok:
        print(f"  ALL DONE in {total}s — Pipeline ready to use!")
        print(f"\n  Next steps:")
        print(f"    streamlit run app.py              # Interactive UI")
        print(f"    python run_all_notes.py            # Batch processing")
        print(f"    python evaluation/evaluate_chu.py  # Compute metrics")
    else:
        print(f"  SETUP INCOMPLETE — Fix the [MISSING] items above")
    print("=" * 60 + "\n")
