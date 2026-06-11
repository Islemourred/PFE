"""
Entity Merger — Post-NER fragment reassembly.

Problem: NER models often fragment compound clinical terms:
  "Wiskott-Aldrich syndrome" → ["wis", "kot", "aldrich", "syndrome"]
  "Cystic fibrosis"          → ["cystic", "fibrosis"]

Solution: Scan NER output for adjacent/nearby entities, merge them into
candidate phrases, validate against HPO ontology (exact match or high
SapBERT score). If merged phrase maps better → replace fragments.

This is fully dynamic — no curated data, uses the ontology as validation.
"""

import re
from log_config import get_logger

logger = get_logger(__name__)


class EntityMerger:
    """Merge fragmented NER entities back into complete clinical phrases."""

    # Maximum gap (in characters) between two entities to consider merging
    MAX_GAP = 5

    # Minimum SapBERT score to validate a merged phrase
    MERGE_VALIDATION_THRESHOLD = 0.72

    # Minimum word count for a fragment to be considered "too short"
    SHORT_FRAGMENT_MAXLEN = 3

    def __init__(self, exact_matcher=None, sapbert_linker=None):
        """
        Args:
            exact_matcher: ExactMatcher instance for ontology validation
            sapbert_linker: SapBERTLinker instance for semantic validation
        """
        self.exact_matcher = exact_matcher
        self.sapbert_linker = sapbert_linker

    def merge_entities(self, entities: dict, source_text: str) -> dict:
        """
        Merge fragmented entities across all categories.

        Args:
            entities:    NER output dict {"problem": [...], "treatment": [...], ...}
            source_text: original text for extracting spans between fragments

        Returns:
            Updated entities dict with fragments merged where beneficial
        """
        merged = {}
        total_merges = 0

        for category, ents in entities.items():
            if not isinstance(ents, list) or not ents:
                merged[category] = ents
                continue

            # Sort by position in text
            sorted_ents = sorted(ents, key=lambda e: e.get("start", 0))
            result = self._merge_category(sorted_ents, source_text)
            merges = len(sorted_ents) - len(result)
            total_merges += max(0, merges)
            merged[category] = result

        if total_merges > 0:
            logger.info("  EntityMerger: %d fragments merged into complete terms",
                        total_merges)

        return merged

    def _merge_category(self, entities: list[dict], source_text: str) -> list[dict]:
        """Merge fragments within a single category.
        
        Strategy: Only merge fragments that are individually short/unresolvable.
        Never break an entity that already has a good individual match.
        """
        if len(entities) <= 1:
            return entities

        # First pass: identify which entities are "short fragments" that
        # are unlikely to match on their own (e.g., "wis", "kot", "gene")
        fragment_flags = []
        for ent in entities:
            text = ent["text"].strip()
            words = text.split()
            is_fragment = (
                len(words) == 1 and len(text) <= self.SHORT_FRAGMENT_MAXLEN * 3
                and not self._validate_individual(text)
            )
            fragment_flags.append(is_fragment)

        result = []
        i = 0

        while i < len(entities):
            # Only try to merge if current entity is a fragment
            if not fragment_flags[i]:
                result.append(entities[i])
                i += 1
                continue

            # Try to build the longest valid merged phrase from consecutive fragments
            best_merged = None
            best_end_idx = i

            for j in range(i + 1, min(i + 6, len(entities))):
                # Only merge with other fragments or adjacent entities
                gap = entities[j].get("start", 0) - entities[j - 1].get("end", 0)
                if gap > self.MAX_GAP:
                    break

                # Build the merged phrase from the source text
                merge_start = entities[i].get("start", 0)
                merge_end = entities[j].get("end", 0)

                if merge_start >= 0 and merge_end > merge_start and merge_end <= len(source_text):
                    merged_text = source_text[merge_start:merge_end].strip()
                else:
                    merged_text = " ".join(
                        e["text"] for e in entities[i:j + 1]
                    )

                merged_text = re.sub(r'\s+', ' ', merged_text).strip()
                if len(merged_text) < 4:
                    continue

                # Validate against ontology
                match = self._validate_merged(merged_text)
                if match:
                    best_merged = {
                        "text": merged_text,
                        "score": max(e.get("score", 0) for e in entities[i:j + 1]),
                        "start": merge_start,
                        "end": merge_end,
                        "source": "merged",
                        "merge_match": match,
                    }
                    best_end_idx = j

            if best_merged:
                result.append(best_merged)
                i = best_end_idx + 1
            else:
                result.append(entities[i])
                i += 1

        return result

    def _validate_individual(self, text: str) -> bool:
        """Check if a single entity text can match HPO on its own."""
        if self.exact_matcher:
            exact = self.exact_matcher.match(text)
            if exact:
                return True
        if self.sapbert_linker:
            result = self.sapbert_linker.link(text, top_k=1)
            if result and result["confidence"] >= 0.70:
                return True
        return False

    def _validate_merged(self, text: str) -> dict | None:
        """
        Check if a merged phrase maps to HPO better than individual fragments.

        Returns match dict if valid, None if not worth merging.
        """
        # Try exact match first (fastest)
        if self.exact_matcher:
            exact = self.exact_matcher.match(text)
            if exact:
                return exact

        # Try SapBERT semantic match
        if self.sapbert_linker:
            result = self.sapbert_linker.link(text, top_k=3)
            if result and result["confidence"] >= self.MERGE_VALIDATION_THRESHOLD:
                return result

        return None
