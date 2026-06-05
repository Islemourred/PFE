"""
Module 3.1 — NegEx: Negation Detection for Clinical Text (Bilingual)
Based on Chapman et al. (2001) — extended with French negation cues.

Hybrid approach:
  1. Primary:  Rule-based NegEx (Chapman 2001) — fast, deterministic, explainable
  2. Enhanced: Distance-based confidence scoring (closer cue = higher confidence)
  3. Optional: Transformer-based verification for ambiguous cases

English: original NegEx lexicon (Chapman et al., 2001)
French:  adapted lexicon for French clinical negation patterns.

Algorithm:
  1. Identify negation cues in the text (pre-negation and post-negation)
  2. Determine scope of each cue (forward for pre-, backward for post-)
  3. Compute confidence based on cue-entity distance
  4. Mark entities within scope as negated with confidence scores
  5. Filter out pseudo-negation patterns to avoid false positives
"""

import re
import pysbd
from log_config import get_logger

logger = get_logger(__name__)

# ── English Negation cue lexicons ────────────────────────────────────────────

EN_PRE_NEGATION_CUES = [
    "no complaints of", "no evidence of", "no history of",
    "no sign of", "no signs of", "no significant",
    "no definite", "no obvious", "no apparent",
    "no acute", "no gross", "no focal",
    "fails to reveal", "failed to reveal",
    "not demonstrate", "does not demonstrate",
    "negative for", "neg for",
    "absence of", "free of", "free from",
    "ruled out", "rules out", "rule out",
    "did not", "does not", "do not",
    "cannot", "can not", "could not",
    "was not", "were not", "is not", "are not",
    "has not", "have not", "had not",
    "no longer",
    "without",
    "denies", "denied", "deny",
    "absent",
    "decline", "declined", "refuses",
    "resolved", "unremarkable",
    "neither", "never", "none",
    "not", "no",
]

EN_POST_NEGATION_CUES = [
    "has been ruled out", "have been ruled out",
    "has been excluded", "have been excluded",
    "was ruled out", "is ruled out",
    "was excluded", "is excluded",
    "was negative", "is negative",
    "was absent", "is absent",
    "not seen", "not found", "not identified",
    "not present", "not demonstrated",
    "unlikely",
]

EN_PSEUDO_NEGATION_CUES = [
    "no increase", "no decrease", "no change",
    "no longer needed", "no need",
    "not only", "not necessarily",
    "not certain", "not exclude",
    "no further", "no additional",
    "gram negative", "gram-negative",
    "not limited to",
]

# ── French Negation cue lexicons ─────────────────────────────────────────────

FR_PRE_NEGATION_CUES = [
    # Complex phrases first (longest match first)
    "pas de signe de", "pas de signes de",
    "pas d'argument pour", "pas d'arguments pour",
    "pas d'anomalie", "pas d'anomalies",
    "pas de notion de", "pas de plainte de",
    "pas de particularité", "pas de particularités",
    "aucun signe de", "aucune notion de",
    "aucun argument pour", "aucune anomalie",
    "absence totale de", "absence complète de",
    "il n'y a pas de", "il n'existe pas de",
    "on ne retrouve pas de", "on ne note pas de",
    "ne révèle pas de", "ne montre pas de",
    "ne retrouve pas de", "n'objective pas de",
    "n'a pas présenté de", "n'a pas présenté d'",
    "sans particularité", "sans anomalie",
    "sans anomalies", "sans signe de",
    # Medium phrases
    "pas de", "pas d'",
    "absence de", "absence d'",
    "aucun", "aucune",
    "sans", "ni",
    "négatif pour", "négative pour",
    "négatif", "négative",
    "éliminé", "éliminée",
    "exclu", "exclue",
    "non retrouvé", "non retrouvée",
    "non objectivé", "non objectivée",
    "non documenté", "non documentée",
    "non fait", "non faite",
    "non présent", "non présente",
    "non observé", "non observée",
    # Short negators
    "non", "jamais",
]

FR_POST_NEGATION_CUES = [
    "a été éliminé", "a été éliminée",
    "a été exclu", "a été exclue",
    "est négatif", "est négative",
    "est absent", "est absente",
    "non retrouvé", "non retrouvée",
    "non confirmé", "non confirmée",
    "non objectivé", "non objectivée",
]

FR_PSEUDO_NEGATION_CUES = [
    "pas d'amélioration", "pas d'aggravation",
    "pas de changement", "pas de modification",
    "non seulement", "pas nécessairement",
    "non exclu", "non exclue",
    "gram négatif", "gram-négatif",
    "pas encore", "pas uniquement",
]

# ── Scope terminators (bilingual) ────────────────────────────────────────────

EN_SCOPE_TERMINATORS = [
    "but", "however", "although", "though",
    "except", "apart from", "aside from",
    "nevertheless", "nonetheless",
    "yet", "still", "otherwise",
]

FR_SCOPE_TERMINATORS = [
    "mais", "cependant", "toutefois", "néanmoins",
    "pourtant", "sauf", "excepté", "hormis",
    "en revanche", "par contre", "malgré",
    "bien que", "quoique", "sinon",
]

# Maximum tokens in negation scope window
MAX_SCOPE_TOKENS = 6


class NegExDetector:
    """
    Bilingual NegEx detector with transformer verification.

    Architecture:
      Layer 1: Rule-based NegEx (Chapman 2001) — fast, deterministic
      Layer 2: Distance-based confidence scoring — dynamic
      Layer 3: Transformer verification — for ambiguous cases (optional)
               EN: bvanaken/clinical-assertion-negation-bert (i2b2 clinical)
               FR: MoritzLaurer/mDeBERTa-v3-base-mnli-xnli (multilingual NLI)
    """

    # Lazy-loaded shared models (one instance each, shared across detectors)
    _en_assertion_model = None
    _fr_nli_model = None
    _models_loaded = False

    def __init__(self, lang: str = "en", use_transformer: bool = True):
        self.lang = lang
        self.use_transformer = use_transformer
        self.segmenter = pysbd.Segmenter(
            language="fr" if lang == "fr" else "en",
            clean=False,
        )

        if lang == "fr":
            self._pre_patterns = self._compile_cues(FR_PRE_NEGATION_CUES)
            self._post_patterns = self._compile_cues(FR_POST_NEGATION_CUES)
            self._pseudo_patterns = self._compile_cues(FR_PSEUDO_NEGATION_CUES)
            self._term_patterns = self._compile_cues(FR_SCOPE_TERMINATORS)
        else:
            self._pre_patterns = self._compile_cues(EN_PRE_NEGATION_CUES)
            self._post_patterns = self._compile_cues(EN_POST_NEGATION_CUES)
            self._pseudo_patterns = self._compile_cues(EN_PSEUDO_NEGATION_CUES)
            self._term_patterns = self._compile_cues(EN_SCOPE_TERMINATORS)

        # Load transformer models (lazy, shared across instances)
        if use_transformer and not NegExDetector._models_loaded:
            self._load_models()

    @classmethod
    def _load_models(cls):
        """Load assertion/NLI models for negation verification (once, shared)."""
        from transformers import pipeline as hf_pipeline

        # ── English: Clinical Assertion model (i2b2 trained) ──
        try:
            en_model = "bvanaken/clinical-assertion-negation-bert"
            logger.info("  Loading EN assertion model: %s...", en_model)
            cls._en_assertion_model = hf_pipeline(
                "text-classification",
                model=en_model,
            )
            logger.info("  EN clinical assertion model ready (PRESENT/ABSENT/POSSIBLE)")
        except Exception as e:
            logger.warning("  EN assertion model not available: %s", e)
            cls._en_assertion_model = None

        # ── French: Multilingual NLI model (XNLI trained) ──
        try:
            fr_model = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
            logger.info("  Loading FR NLI model: %s...", fr_model)
            cls._fr_nli_model = hf_pipeline(
                "zero-shot-classification",
                model=fr_model,
            )
            logger.info("  FR multilingual NLI model ready")
        except Exception as e:
            logger.warning("  FR NLI model not available: %s", e)
            cls._fr_nli_model = None

        cls._models_loaded = True

    def _verify_with_transformer(self, sentence: str, entity_text: str) -> float:
        """
        Verify negation using the best available transformer model.

        EN: bvanaken/clinical-assertion-negation-bert
            → Classifies as PRESENT / ABSENT / POSSIBLE
            → Trained on i2b2 2010 clinical assertion data

        FR: MoritzLaurer/mDeBERTa-v3-base-mnli-xnli
            → Zero-shot NLI: "Le signe clinique est présent/absent"
            → Trained on XNLI (15 languages incl. French)

        Returns:
            Score 0.0 (affirmed/present) to 1.0 (negated/absent)
            -1.0 if model not available
        """
        if self.lang == "en":
            return self._verify_english(sentence, entity_text)
        else:
            return self._verify_french(sentence, entity_text)

    def _verify_english(self, sentence: str, entity_text: str) -> float:
        """Use clinical assertion model for English negation verification."""
        if not self._en_assertion_model:
            return -1.0

        try:
            # Format: include entity context in the sentence
            # The model expects clinical text and classifies the assertion
            input_text = f"{sentence} [entity: {entity_text}]"
            result = self._en_assertion_model(input_text)

            label = result[0]["label"].upper()
            score = result[0]["score"]

            if label == "ABSENT":
                return round(score, 3)         # High = entity is negated
            elif label == "PRESENT":
                return round(1.0 - score, 3)   # Low = entity is present
            elif label == "POSSIBLE":
                return 0.5                      # Uncertain
            else:
                return -1.0

        except Exception:
            return -1.0

    def _verify_french(self, sentence: str, entity_text: str) -> float:
        """Use multilingual NLI model for French negation verification."""
        if not self._fr_nli_model:
            return -1.0

        try:
            result = self._fr_nli_model(
                sentence,
                candidate_labels=["présent", "absent"],
                hypothesis_template="Le signe clinique est {}.",
            )

            result_labels = result["labels"]
            result_scores = result["scores"]
            absent_label = "absent"
            if absent_label in result_labels:
                absent_idx = result_labels.index(absent_label)
            else:
                absent_idx = 1
            return round(result_scores[absent_idx], 3)

        except Exception:
            return -1.0

    def _compile_cues(self, cues: list) -> list:
        """Compile cue phrases into regex patterns.
        Handles French contractions (pas d', absence d') where
        word boundaries don't work with apostrophes.
        """
        patterns = []
        for cue in cues:
            escaped = re.escape(cue)
            # For cues ending with apostrophe (pas d', absence d'), don't require word boundary at end
            if cue.endswith("'") or cue.endswith("'"):
                patterns.append(re.compile(r'(?:^|\b)' + escaped, re.IGNORECASE))
            else:
                patterns.append(re.compile(r'(?:^|\b)' + escaped + r'\b', re.IGNORECASE))
        return patterns

    def detect_negation(self, text: str, entities: dict) -> dict:
        """
        Detect negated entities in clinical text.

        Args:
            text: clean clinical text
            entities: dict from Module 2 NER with entity positions

        Returns:
            Same entities dict with "negated" field added
        """
        sentences = self.segmenter.segment(text)
        text_lower = text.lower()

        for category in entities:
            for entity in entities[category]:
                entity_text = entity["text"]
                entity_lower = entity_text.lower()

                ent_start = text_lower.find(entity_lower)
                if ent_start == -1:
                    entity["negated"] = False
                    continue

                ent_end = ent_start + len(entity_text)

                sentence = self._find_sentence(text, ent_start, sentences)
                if not sentence:
                    entity["negated"] = False
                    continue

                sent_lower = sentence.lower()
                sent_start = text_lower.find(sent_lower)
                if sent_start == -1:
                    sent_start = 0

                local_ent_start = ent_start - sent_start
                local_ent_end = ent_end - sent_start

                if self._is_pseudo_negation(sent_lower, local_ent_start):
                    entity["negated"] = False
                    continue

                neg_cue = self._check_pre_negation(
                    sent_lower, local_ent_start, local_ent_end
                )
                if neg_cue:
                    tokens_dist = len(neg_cue.split())
                    confidence = self._compute_confidence(tokens_dist, "pre")

                    # Transformer verification for ambiguous cases
                    if self.use_transformer and 0.5 <= confidence <= 0.85:
                        nli_score = self._verify_with_transformer(sentence, entity_text)
                        if nli_score >= 0:
                            # Blend rule-based and model-based confidence
                            confidence = round(0.4 * confidence + 0.6 * nli_score, 3)
                            entity["negation_method"] = "negex+nli"
                        else:
                            entity["negation_method"] = "negex"
                    else:
                        entity["negation_method"] = "negex"

                    entity["negated"] = True
                    entity["negation_cue"] = neg_cue
                    entity["negation_type"] = "pre"
                    entity["negation_confidence"] = confidence
                    continue

                neg_cue = self._check_post_negation(
                    sent_lower, local_ent_start, local_ent_end
                )
                if neg_cue:
                    tokens_dist = len(neg_cue.split())
                    confidence = self._compute_confidence(tokens_dist, "post")

                    # Transformer verification for ambiguous cases
                    if self.use_transformer and 0.5 <= confidence <= 0.85:
                        nli_score = self._verify_with_transformer(sentence, entity_text)
                        if nli_score >= 0:
                            confidence = round(0.4 * confidence + 0.6 * nli_score, 3)
                            entity["negation_method"] = "negex+nli"
                        else:
                            entity["negation_method"] = "negex"
                    else:
                        entity["negation_method"] = "negex"

                    entity["negated"] = True
                    entity["negation_cue"] = neg_cue
                    entity["negation_type"] = "post"
                    entity["negation_confidence"] = confidence
                    continue

                entity["negated"] = False
                entity["negation_confidence"] = 0.0

        return entities

    def _compute_confidence(self, cue_token_distance: int, neg_type: str) -> float:
        """
        Compute negation confidence based on cue-entity distance.

        Closer cues = higher confidence (dynamic scoring vs binary yes/no).
        Pre-negation cues are slightly more reliable than post-negation.

        Returns:
            Confidence score between 0.5 and 1.0
        """
        # Base confidence: 1.0 for adjacent, decays with distance
        distance_factor = max(0.5, 1.0 - (cue_token_distance * 0.08))

        # Pre-negation cues are more reliable than post-negation
        type_bonus = 1.0 if neg_type == "pre" else 0.92

        confidence = round(min(1.0, distance_factor * type_bonus), 3)
        return confidence

    def _find_sentence(self, text: str, position: int, sentences: list) -> str:
        """Find the sentence that contains the given character position."""
        current_pos = 0
        for sent in sentences:
            sent_start = text.find(sent, current_pos)
            if sent_start == -1:
                continue
            sent_end = sent_start + len(sent)
            if sent_start <= position < sent_end:
                return sent
            current_pos = sent_end
        start = max(0, position - 200)
        end = min(len(text), position + 200)
        return text[start:end]

    def _check_pre_negation(self, sentence: str, ent_start: int, ent_end: int) -> str:
        """Check if a pre-negation cue is within scope before the entity."""
        text_before = sentence[:ent_start]

        for pattern in self._pre_patterns:
            for match in pattern.finditer(text_before):
                cue_end = match.end()
                between = text_before[cue_end:].strip()
                tokens_between = between.split()

                if len(tokens_between) <= MAX_SCOPE_TOKENS:
                    if not self._has_terminator(between):
                        return match.group()

        return ""

    def _check_post_negation(self, sentence: str, ent_start: int, ent_end: int) -> str:
        """Check if a post-negation cue is within scope after the entity."""
        text_after = sentence[ent_end:]

        for pattern in self._post_patterns:
            match = pattern.search(text_after)
            if match:
                between = text_after[:match.start()].strip()
                tokens_between = between.split()

                if len(tokens_between) <= MAX_SCOPE_TOKENS:
                    if not self._has_terminator(between):
                        return match.group()

        return ""

    def _is_pseudo_negation(self, sentence: str, ent_start: int) -> bool:
        """Check if apparent negation is actually pseudo-negation."""
        text_before = sentence[:ent_start]
        for pattern in self._pseudo_patterns:
            if pattern.search(text_before):
                return True
        return False

    def _has_terminator(self, text: str) -> bool:
        """Check if text contains a scope terminator."""
        for pattern in self._term_patterns:
            if pattern.search(text):
                return True
        return False
