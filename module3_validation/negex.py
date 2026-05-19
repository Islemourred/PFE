"""
Module 3.1 — NegEx: Negation Detection for Clinical Text (Bilingual)
Based on Chapman et al. (2001) — extended with French negation cues.

English: original NegEx lexicon (Chapman et al., 2001)
French:  adapted lexicon for French clinical negation patterns.

Algorithm:
  1. Identify negation cues in the text (pre-negation and post-negation)
  2. Determine scope of each cue (forward for pre-, backward for post-)
  3. Mark entities within scope as negated
  4. Filter out pseudo-negation patterns to avoid false positives
"""

import re
import pysbd

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
    Bilingual NegEx detector: detects negated clinical entities
    in both French and English clinical text.
    """

    def __init__(self, lang: str = "en"):
        self.lang = lang
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
                    entity["negated"] = True
                    entity["negation_cue"] = neg_cue
                    entity["negation_type"] = "pre"
                    continue

                neg_cue = self._check_post_negation(
                    sent_lower, local_ent_start, local_ent_end
                )
                if neg_cue:
                    entity["negated"] = True
                    entity["negation_cue"] = neg_cue
                    entity["negation_type"] = "post"
                    continue

                entity["negated"] = False

        return entities

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
