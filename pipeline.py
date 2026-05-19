"""
Full Pipeline — Orchestrates all 4 modules of the clinical pre-analysis system.
BILINGUAL: detects language (French/English) and routes accordingly.

Architecture (per mémoire Ch4):
  Module 1: Preprocessing & De-identification (PHI removal)
  Module 2: Semantic Extraction (ClinicalBERT / CamemBERT-bio GLiNER)
  Module 3: Rule-based Validation (NegEx, temporal, numeric, inconsistencies)
  Module 4: Ontological Normalization (Abbreviations → Exact → SapBERT → UMLS → ORDO)
  Output:   Phenopacket ISO 4454:2022

Usage:
    pipeline = FullPipeline()          # loads both EN + FR models
    result = pipeline.process("Le patient présente...", note_id="NOTE_FR_001")
    result = pipeline.process("Patient is a 55yo male...", note_id="NOTE_EN_001")
"""

import os
import json

from language_detector import detect_language
from module1_preprocessing.phi_remover import process_phi
from module2_extraction.clinical_ner import ClinicalNER
from module3_validation.negex import NegExDetector
from module3_validation.temporal import check_temporal_consistency
from module3_validation.numeric import extract_numeric_phenotypes
from module3_validation.inconsistency import detect_inconsistencies
from module4_normalization.pipeline import NormalizationPipeline
from output_builder.phenopacket_builder import build_phenopacket


class FullPipeline:
    """
    End-to-end clinical pre-analysis pipeline.
    Bilingual: auto-detects language and routes to FR or EN components.
    """

    def __init__(self, similarity_threshold: float = 0.80):
        print("Initializing Clinical Pre-Analysis Pipeline (Bilingual)...")

        print("  Loading Module 2: ClinicalBERT NER (English)...")
        self.ner_en = ClinicalNER(lang="en")

        print("  Loading Module 2: CamemBERT-bio GLiNER (French)...")
        self.ner_fr = ClinicalNER(lang="fr")

        print("  Loading Module 3: NegEx Detectors...")
        self.negex_en = NegExDetector(lang="en")
        self.negex_fr = NegExDetector(lang="fr")

        print("  Loading Module 4: Normalization Pipeline...")
        self.normalizer = NormalizationPipeline(
            similarity_threshold=similarity_threshold
        )

        print("Pipeline ready (FR + EN).\n")

    def process(self, clinical_text: str, note_id: str = "UNKNOWN",
                patient_info: dict = None, lang: str = None) -> dict:
        """
        Run the full 4-module pipeline on a clinical note.
        Auto-detects language if not specified.

        Args:
            clinical_text: raw clinical note text
            note_id: identifier for the note
            patient_info: optional patient metadata override
            lang: force language ('fr' or 'en'), or None for auto-detect

        Returns:
            Complete result dict with all module outputs + phenopacket
        """
        raw_text = clinical_text

        # ═══════════════════════════════════════════════════════════════
        # LANGUAGE DETECTION
        # ═══════════════════════════════════════════════════════════════
        if lang is None:
            lang = detect_language(raw_text)
        print(f"  [{note_id}] Language: {lang.upper()}")

        # ═══════════════════════════════════════════════════════════════
        # MODULE 1: Preprocessing & De-identification
        # ═══════════════════════════════════════════════════════════════
        preprocessed = process_phi(raw_text, lang=lang)
        clean_text = preprocessed["clean_text"]

        if patient_info is None:
            patient_info = preprocessed.get("patient_info", {})

        # ═══════════════════════════════════════════════════════════════
        # MODULE 2: Semantic Extraction (NER)
        # ═══════════════════════════════════════════════════════════════
        ner = self.ner_fr if lang == "fr" else self.ner_en
        entities = ner(clean_text)

        # ═══════════════════════════════════════════════════════════════
        # MODULE 3: Rule-based Validation
        # ═══════════════════════════════════════════════════════════════
        # 3.1 NegEx negation detection
        negex = self.negex_fr if lang == "fr" else self.negex_en
        entities = negex.detect_negation(clean_text, entities)

        # 3.2 Temporal consistency check
        temporal_warnings = check_temporal_consistency(raw_text)

        # 3.3 Numeric phenotype extraction
        numeric_phenotypes = extract_numeric_phenotypes(raw_text)

        # 3.4 Inconsistency detection
        inconsistencies = detect_inconsistencies(
            clean_text, entities, patient_info
        )

        validated = {
            "entities": entities,
            "warnings": {
                "temporal": temporal_warnings,
                "inconsistencies": inconsistencies,
            },
            "numeric_phenotypes": numeric_phenotypes,
        }

        # ═══════════════════════════════════════════════════════════════
        # MODULE 4: Ontological Normalization
        # ═══════════════════════════════════════════════════════════════
        normalized = self.normalizer.normalize_all(
            entities=entities,
            numeric_phenotypes=numeric_phenotypes,
            lang=lang,
        )

        # ═══════════════════════════════════════════════════════════════
        # OUTPUT: Phenopacket (ISO 4454:2022)
        # ═══════════════════════════════════════════════════════════════
        phenopacket = build_phenopacket(
            note_id=note_id,
            preprocessed=preprocessed,
            validated=validated,
            normalized=normalized,
            patient_info=patient_info,
        )

        return {
            "note_id": note_id,
            "language": lang,
            "module1": {
                "clean_text": clean_text,
                "phi_map": preprocessed["phi_map"],
                "patient_info": patient_info,
            },
            "module2": {"entities": entities},
            "module3": validated,
            "module4": normalized,
            "phenopacket": phenopacket,
            # Backward-compatible aliases
            "step1": {
                "clean_text": clean_text,
                "phi_map": preprocessed["phi_map"],
                "entities": entities,
            },
            "step2": normalized,
        }

    def process_and_save(self, clinical_text: str, note_id: str,
                         output_dir: str, patient_info: dict = None,
                         lang: str = None) -> dict:
        """Process a note and save outputs to JSON files."""
        result = self.process(clinical_text, note_id, patient_info, lang=lang)

        os.makedirs(output_dir, exist_ok=True)

        # Save phenopacket
        pp_path = os.path.join(output_dir, f"{note_id}_phenopacket.json")
        with open(pp_path, "w", encoding="utf-8") as f:
            json.dump(result["phenopacket"], f, indent=2, ensure_ascii=False)

        # Save full output
        full_path = os.path.join(output_dir, f"{note_id}_full_output.json")
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump({
                "note_id": note_id,
                "language": lang,
                "module1": result["module1"],
                "module3_warnings": result["module3"]["warnings"],
                "module4": result["module4"],
                "phenopacket": result["phenopacket"],
            }, f, indent=2, ensure_ascii=False)

        return result
