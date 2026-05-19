"""
Module 2 — Clinical NER Extraction (Bilingual)

English: samrawal/bert-base-uncased_clinical-ner (BERT fine-tuned on i2b2)
French:  almanach/camembert-bio-gliner-v0.1 (CamemBERT-bio + GLiNER zero-shot)

GLiNER enables zero-shot NER — we define custom French clinical labels
(problème, traitement, test) and extract entities without fine-tuning.
This is the state of the art for French biomedical NER (ALMAnaCH/Inria, 2024).
"""

import re
import pysbd
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline


class ClinicalNER:
    """Bilingual clinical NER: English (BERT i2b2) + French (CamemBERT-bio GLiNER)."""

    def __init__(self, lang: str = "en",
                 en_model: str = "samrawal/bert-base-uncased_clinical-ner",
                 fr_model: str = "almanach/camembert-bio-gliner-v0.1"):
        self.lang = lang

        if lang == "fr":
            print(f"  Loading French NER: {fr_model}")
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
            print(f"  Loading English NER: {en_model}")
            self.tokenizer = AutoTokenizer.from_pretrained(en_model)
            self.model = AutoModelForTokenClassification.from_pretrained(en_model)
            self.ner = pipeline(
                "ner",
                model=self.model,
                tokenizer=self.tokenizer,
                aggregation_strategy="first"
            )
            self.seg = pysbd.Segmenter(language="en", clean=False)

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

                # Find position in original text
                start = text.lower().find(word.lower())
                end = start + len(word) if start >= 0 else len(word)

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
        Extract English clinical entities using BERT i2b2 model.
        Original implementation.
        """
        chunks = self._chunk_text_en(text)

        merged = {}
        offset = 0
        for chunk in chunks:
            for ent in self.ner(chunk):
                word = self._fix_word(ent["word"])
                if not word:
                    continue
                label = ent["entity_group"]
                if label not in merged:
                    merged[label] = []

                start_in_text = text.lower().find(word.lower(), offset)
                if start_in_text == -1:
                    start_in_text = text.lower().find(word.lower())

                merged[label].append({
                    "text": word,
                    "score": round(float(ent["score"]), 3),
                    "start": start_in_text if start_in_text >= 0 else 0,
                    "end": (start_in_text + len(word)) if start_in_text >= 0 else len(word),
                })

        # Deduplicate
        for label in merged:
            seen = set()
            deduped = []
            for ent in merged[label]:
                if ent["text"] not in seen:
                    seen.add(ent["text"])
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
