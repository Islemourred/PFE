"""
HPO Text Scanner — Direct dictionary-based phenotype detection.

Scans raw clinical text for known HPO term labels and synonyms,
bypassing NER entirely. This is the equivalent of what the French
pipeline does with french_hpo_loader (25K labels), but for English.

Why this works:
  - French pipeline: GLiNER extracts full phrases → french_partial matches 258 terms
  - English pipeline: DeBERTa fragments terms → NER output is broken → 0 matches
  - This scanner: looks for "recurrent infections", "thrombocytopenia" etc.
    directly in the text → catches what NER missed

Only scans for multi-word terms (≥2 words) or single words ≥6 chars
to avoid false positives from short common words like "pain" or "fever"
appearing in non-clinical context.
"""

import re
from log_config import get_logger

logger = get_logger(__name__)


class HPOTextScanner:
    """Scan raw text for HPO term labels/synonyms, independent of NER."""

    # Minimum character length for single-word matches
    MIN_SINGLE_WORD_LEN = 4

    # Words to skip even if they appear in HPO labels
    SKIP_WORDS = {
        "disease", "disorder", "syndrome", "abnormality", "abnormal",
        "increased", "decreased", "delayed", "absent", "reduced",
        "chronic", "acute", "severe", "mild", "moderate",
        "type", "form", "variant", "familial", "hereditary",
        "of", "the", "and", "in", "with", "or", "a", "an",
        "pain", "loss", "mass", "cell", "gene", "acid",
        "left", "right", "upper", "lower", "large", "small",
        "test", "sign", "male", "bone", "body", "blood",
        "drug", "dose", "case", "well", "also", "been",
        "were", "have", "that", "this", "from", "some",
    }

    def __init__(self, exact_matcher):
        """
        Args:
            exact_matcher: ExactMatcher instance with the HPO lookup table
        """
        self.lookup = exact_matcher.lookup
        self.blacklist = exact_matcher.is_blacklisted

        # Pre-filter: only keep terms worth scanning for
        self.scan_terms = {}
        for key, value in self.lookup.items():
            words = key.split()
            # Multi-word terms (≥2 words): include if ≥6 chars total
            if len(words) >= 2 and len(key) >= 6:
                self.scan_terms[key] = value
            # Single-word terms: only if long enough and not a skip word
            elif len(words) == 1 and len(key) >= self.MIN_SINGLE_WORD_LEN:
                if key not in self.SKIP_WORDS:
                    self.scan_terms[key] = value

        # Sort by length (longest first) for greedy matching
        self.sorted_terms = sorted(
            self.scan_terms.keys(), key=len, reverse=True
        )

        logger.info("HPOTextScanner: %d scannable terms (%d multi-word, %d single-word)",
                     len(self.scan_terms),
                     sum(1 for k in self.scan_terms if len(k.split()) >= 2),
                     sum(1 for k in self.scan_terms if len(k.split()) == 1))

    def scan(self, text: str, existing_hpo_ids: set = None) -> list[dict]:
        """
        Scan text for HPO terms not already found by NER.

        Args:
            text: raw clinical text to scan
            existing_hpo_ids: HPO IDs already found (to avoid duplicates)

        Returns:
            List of entity dicts compatible with NER output format
        """
        if existing_hpo_ids is None:
            existing_hpo_ids = set()

        text_lower = text.lower()
        found = []
        matched_spans = []  # Track matched character ranges to avoid overlaps

        for term in self.sorted_terms:
            # Skip if this HPO ID was already found
            match_info = self.scan_terms[term]
            if match_info["id"] in existing_hpo_ids:
                continue
            if self.blacklist(match_info["id"]):
                continue

            # Search for the term in text (word boundary matching)
            pattern = r'\b' + re.escape(term) + r'\b'
            for m in re.finditer(pattern, text_lower):
                start, end = m.start(), m.end()

                # Check for overlap with already-matched spans
                overlaps = False
                for ms, me in matched_spans:
                    if start < me and end > ms:
                        overlaps = True
                        break
                if overlaps:
                    continue

                # Found a new match!
                matched_spans.append((start, end))
                existing_hpo_ids.add(match_info["id"])

                found.append({
                    "text": text[start:end],  # Original case from text
                    "score": 0.90,
                    "start": start,
                    "end": end,
                    "source": "text_scanner",
                    "hpo_id": match_info["id"],
                    "hpo_name": match_info["name"],
                    "match_type": "text_scan_" + match_info["match_type"],
                    "confidence": 0.95,
                })
                break  # Only take first occurrence per term

        if found:
            logger.info("  HPOTextScanner: found %d additional terms in text", len(found))

        return found
