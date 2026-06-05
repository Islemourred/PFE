"""
Module 2 — Clinical NER Extraction (Bilingual)

English: Ensemble of two models for maximum recall:
  1. Helios9/BioMed_NER (DeBERTa-v3-base, SOTA 2024: disease/symptom/medication/procedure)
  2. d4data/biomedical-ner-all (8 biomedical datasets: disease/chemical/gene/protein)
  Results are merged and deduplicated for comprehensive entity coverage.

  Why DeBERTa-v3? Disentangled attention mechanism separately encodes word content
  and position, providing superior contextual understanding for clinical NER vs BERT.

French:  almanach/camembert-bio-gliner-v0.1 (CamemBERT-bio + GLiNER zero-shot)

GLiNER enables zero-shot NER — we define custom French clinical labels
(problème, traitement, test) and extract entities without fine-tuning.
This is the state of the art for French biomedical NER (ALMAnaCH/Inria, 2024).
"""

import re
import pysbd
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from log_config import get_logger

logger = get_logger(__name__)


class ClinicalNER:
    """Bilingual clinical NER: English (DeBERTa-v3 ensemble) + French (CamemBERT-bio GLiNER)."""

    # Label mapping: Helios9/BioMed_NER entities → pipeline categories
    _BIOMED_LABEL_MAP = {
        "Disease_disorder": "problem",
        "Sign_symptom": "problem",
        "Medication": "treatment",
        "Therapeutic_procedure": "treatment",
        "Diagnostic_procedure": "test",
        "Biological_structure": "test",
        "Lab_value": "test",
        # Ignore other labels
    }

    # Label mapping: d4data biomedical entities → pipeline categories
    _BIO_LABEL_MAP = {
        "Disease": "problem",
        "Chemical": "treatment",
        "Gene": "test",
        "Protein": "test",
        # Ignore: Species, Cell_line, Cell_type, DNA, RNA
    }

    def __init__(self, lang: str = "en",
                 en_model: str = "Helios9/BioMed_NER",
                 fr_model: str = "almanach/camembert-bio-gliner-v0.1"):
        self.lang = lang

        if lang == "fr":
            logger.info("  Loading French NER: %s", fr_model)
            from gliner import GLiNER
            self.model = GLiNER.from_pretrained(fr_model)
            self.seg = pysbd.Segmenter(language="fr", clean=False)

            # French clinical entity labels for zero-shot NER
            # More specific labels improve GLiNER extraction accuracy
            self.fr_labels = [
                "maladie",            # disease/pathology → "problem"
                "symptôme",           # symptom/sign → "problem"
                "traitement",         # treatment/medication → "treatment"
                "médicament",         # drug → "treatment"
                "examen médical",     # medical test → "test"
            ]
            # Label mapping French → English (for pipeline compatibility)
            self._label_map = {
                "maladie": "problem",
                "symptôme": "problem",
                "traitement": "treatment",
                "médicament": "treatment",
                "examen médical": "test",
            }
        else:
            # ── Primary model: DeBERTa-v3 BioMed NER (SOTA 2024) ──
            logger.info("  Loading English NER (primary): %s", en_model)
            self.tokenizer = AutoTokenizer.from_pretrained(en_model)
            self.model = AutoModelForTokenClassification.from_pretrained(en_model)
            self.ner = pipeline(
                "ner",
                model=self.model,
                tokenizer=self.tokenizer,
                aggregation_strategy="simple"
            )
            self.seg = pysbd.Segmenter(language="en", clean=False)

            # ── Secondary model: biomedical NER (disease/chemical/gene) ──
            bio_model = "d4data/biomedical-ner-all"
            logger.info("  Loading English NER (ensemble): %s", bio_model)
            self.bio_tokenizer = AutoTokenizer.from_pretrained(bio_model)
            self.bio_model = AutoModelForTokenClassification.from_pretrained(bio_model)
            self.bio_ner = pipeline(
                "ner",
                model=self.bio_model,
                tokenizer=self.bio_tokenizer,
                aggregation_strategy="first"
            )

    def __call__(self, text: str) -> dict:
        """Extract entities from clinical text."""
        if self.lang == "fr":
            return self._extract_french(text)
        else:
            return self._extract_english(text)

    def _extract_french(self, text: str) -> dict:
        """
        Extract French clinical entities using CamemBERT-bio GLiNER.
        Zero-shot approach: labels are defined at inference time.
        """
        merged = {"problem": [], "treatment": [], "test": []}

        # Track search offsets per entity text to handle duplicates
        position_tracker = {}

        # Process by chunks to handle long texts
        chunks = self._chunk_text_fr(text)

        for chunk in chunks:
            try:
                entities = self.model.predict_entities(
                    chunk,
                    self.fr_labels,
                    threshold=0.4,
                    flat_ner=True,
                )
            except Exception:
                continue

            for ent in entities:
                word = ent["text"].strip()
                if not word or len(word) < 2:
                    continue

                label_fr = ent["label"]
                label_en = self._label_map.get(label_fr, "problem")
                score = round(float(ent["score"]), 3)

                # Find position in original text, tracking offset for duplicates
                search_key = word.lower()
                search_from = position_tracker.get(search_key, 0)
                start = text.lower().find(search_key, search_from)
                if start == -1:
                    # Fallback: search from beginning
                    start = text.lower().find(search_key)
                end = start + len(word) if start >= 0 else len(word)
                if start >= 0:
                    position_tracker[search_key] = start + len(word)

                merged[label_en].append({
                    "text": word,
                    "score": score,
                    "start": max(0, start),
                    "end": end,
                })

        # Deduplicate
        for label in merged:
            seen = set()
            deduped = []
            for ent in merged[label]:
                key = ent["text"].lower()
                if key not in seen:
                    seen.add(key)
                    deduped.append(ent)
            merged[label] = deduped

        return merged

    def _extract_english(self, text: str) -> dict:
        """
        Extract English clinical entities using ensemble of two models:
        1. Primary (DeBERTa-v3): catches clinical-style entities with richer labels
        2. Secondary (biomedical): catches biomedical-style entities
        Results are merged and deduplicated.
        """
        chunks = self._chunk_text_en(text)

        merged = {}
        offset = 0

        # ── Pass 1: Primary model (DeBERTa-v3 BioMed NER, SOTA 2024) ──
        for chunk in chunks:
            for ent in self.ner(chunk):
                word = self._fix_word(ent["word"])
                if not word:
                    continue

                # Map DeBERTa-v3 labels to pipeline categories
                raw_label = ent["entity_group"]
                mapped_label = self._BIOMED_LABEL_MAP.get(raw_label)
                if not mapped_label:
                    continue  # skip unmapped labels

                if mapped_label not in merged:
                    merged[mapped_label] = []

                start_in_text = text.lower().find(word.lower(), offset)
                if start_in_text == -1:
                    start_in_text = text.lower().find(word.lower())

                merged[mapped_label].append({
                    "text": word,
                    "score": round(float(ent["score"]), 3),
                    "start": start_in_text if start_in_text >= 0 else 0,
                    "end": (start_in_text + len(word)) if start_in_text >= 0 else len(word),
                    "source": "deberta-v3",
                })

        # ── Pass 2: Secondary model (biomedical NER) ──
        for chunk in chunks:
            for ent in self.bio_ner(chunk):
                word = self._fix_word(ent["word"])
                if not word or len(word) < 2:
                    continue

                bio_label = ent["entity_group"]
                mapped_label = self._BIO_LABEL_MAP.get(bio_label)
                if not mapped_label:
                    continue  # skip Species, Cell_line, etc.

                if mapped_label not in merged:
                    merged[mapped_label] = []

                start_in_text = text.lower().find(word.lower())

                merged[mapped_label].append({
                    "text": word,
                    "score": round(float(ent["score"]), 3),
                    "start": start_in_text if start_in_text >= 0 else 0,
                    "end": (start_in_text + len(word)) if start_in_text >= 0 else len(word),
                    "source": "biomedical",
                })

        # ── Deduplicate across both models ──
        for label in merged:
            seen = set()
            deduped = []
            for ent in merged[label]:
                key = ent["text"].lower().strip()
                if key not in seen:
                    seen.add(key)
                    deduped.append(ent)
            merged[label] = deduped

        return merged

    def _chunk_text_fr(self, text: str) -> list:
        """Split French text into manageable chunks using sentence boundaries."""
        chunks, current = [], []
        current_len = 0
        for sent in self.seg.segment(text):
            sent_len = len(sent.split())
            if current_len + sent_len > 300:
                if current:
                    chunks.append(" ".join(current))
                current, current_len = [], 0
            current.append(sent)
            current_len += sent_len
        if current:
            chunks.append(" ".join(current))
        return chunks

    def _chunk_text_en(self, text: str) -> list:
        """Split English text into chunks of ~480 tokens using sentence boundaries."""
        tokenizer = self.tokenizer
        chunks, current, count = [], [], 0
        for sent in self.seg.segment(text):
            n = tokenizer(sent, return_tensors="pt")["input_ids"].shape[1]
            if count + n > 480:
                chunks.append(" ".join(current))
                current, count = [], 0
            current.append(sent)
            count += n
        if current:
            chunks.append(" ".join(current))
        return chunks

    def _fix_word(self, word: str) -> str:
        """Clean up subword artifacts and noise."""
        word = word.strip()
        word = re.sub(r'\s*##', '', word)
        word = re.sub(r'\s+', ' ', word)
        return word if len(word) > 1 else ""
