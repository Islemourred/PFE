"""
Module 4 Pipeline — Hybrid Ontological Normalization (Bilingual)
Combines rules (abbreviations + exact match + French HPO) with AI (SapBERT)
then enriches with UMLS CUIs and ORDO disease matching.

Architecture (per mémoire Ch4, extended for FR):
  1. Expand abbreviations (rule-based, bilingual)
  2. [FR] Try French→HPO direct dictionary (rule-based)
  3. Try exact match against HPO labels + synonyms (rule-based)
  4. If no match → SapBERT semantic similarity (AI-based)
  5. Enrich with UMLS CUI (cross-reference lookup)
  6. Match patient profile against ORDO disease database
"""

import os
from module4_normalization.hpo_parser import get_hpo_terms
from module4_normalization.abbreviations import expand_abbreviations
from module4_normalization.french_hpo import lookup_french_hpo, translate_to_english
from module4_normalization.exact_matcher import ExactMatcher
from module4_normalization.sapbert_linker import SapBERTLinker
from module4_normalization.umls_mapper import UMLSMapper
from module4_normalization.ordo_matcher import ORDOMatcher
from module4_normalization.hpo_text_scanner import HPOTextScanner


class NormalizationPipeline:
    """Module 4: Hybrid normalization with UMLS + ORDO enrichment."""

    def __init__(self, owl_path: str = None, similarity_threshold: float = 0.70):
        if owl_path is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            owl_path = os.path.join(project_root, "hp.owl")

        # Load HPO terms
        self.hpo_terms = get_hpo_terms(owl_path)

        # Build components
        self.exact_matcher = ExactMatcher(self.hpo_terms)
        self.sapbert = SapBERTLinker(self.hpo_terms, similarity_threshold=similarity_threshold)
        self.umls_mapper = UMLSMapper(self.hpo_terms)
        self.ordo_matcher = ORDOMatcher()
        self.text_scanner = HPOTextScanner(self.exact_matcher)

    def normalize_entity(self, entity_text: str, lang: str = "en",
                          context: str = None) -> dict:
        """Normalize a single entity to HPO + UMLS."""
        raw = entity_text.strip()
        expanded = expand_abbreviations(raw, lang=lang)

        result = {
            "raw_text": raw, "expanded_text": expanded,
            "hpo_id": None, "hpo_name": None,
            "match_type": "no_match", "confidence": 0.0,
            "matched": False, "umls_cui": None, "alternatives": [],
        }

        # Phase 1: French HPO dictionary (for French text)
        if lang == "fr":
            fr_match = lookup_french_hpo(raw)
            if not fr_match:
                fr_match = lookup_french_hpo(expanded)
            if fr_match:
                result.update({
                    "hpo_id": fr_match["hpo_id"],
                    "hpo_name": fr_match["hpo_name"],
                    "match_type": fr_match["match_type"],
                    "confidence": fr_match["confidence"],
                    "matched": True,
                })
                self.umls_mapper.enrich_entity(result)
                return result

        # Phase 2: Exact match against HPO labels + synonyms (rules)
        # For French: translate to English first, then try exact match
        search_term = translate_to_english(expanded) if lang == "fr" else expanded
        exact = self.exact_matcher.match(search_term)
        if not exact and search_term != expanded:
            exact = self.exact_matcher.match(expanded)
        if exact:
            result.update({
                "hpo_id": exact["id"], "hpo_name": exact["name"],
                "match_type": exact["match_type"],
                "confidence": exact["confidence"], "matched": True,
            })
        else:
            # Phase 3: SapBERT semantic matching (AI fallback)
            # For French: use translated English term for better SapBERT results
            # Pass context for short entities to enable disambiguation
            sapbert_input = search_term if lang == "fr" else expanded
            sapbert_result = self.sapbert.link(
                sapbert_input, context=context
            )
            if sapbert_result and not ExactMatcher.is_blacklisted(sapbert_result["id"]):
                result.update({
                    "hpo_id": sapbert_result["id"],
                    "hpo_name": sapbert_result["name"],
                    "match_type": sapbert_result["match_type"],
                    "confidence": sapbert_result["confidence"],
                    "matched": True,
                    "alternatives": sapbert_result.get("alternatives", []),
                })

        # Phase 4: UMLS CUI enrichment
        self.umls_mapper.enrich_entity(result)

        return result

    def normalize_all(self, entities: dict, numeric_phenotypes: list = None,
                       lang: str = "en", source_text: str = "") -> dict:
        """
        Normalize all entities from Module 2/3 output.

        Args:
            entities: NER entities dict with negation flags
            numeric_phenotypes: additional phenotypes from numeric parser
            lang: language code ('en' or 'fr')
            source_text: original text for extracting context around entities

        Returns:
            Normalized dict with HPO/UMLS enrichment + ORDO candidates + stats
        """
        normalized = {}
        total, matched = 0, 0
        all_hpo_ids = set()

        for category, ents in entities.items():
            if not isinstance(ents, list):
                continue
            normalized[category] = []
            for ent in ents:
                text = ent["text"]
                total += 1

                # ── Selective skip for English treatment/test entities ──
                # Only skip entities that are clearly NOT phenotypes:
                # drugs, procedures, lab names, genes, imaging modalities.
                # Let phenotype-like entities through (they'll be no_match if wrong).
                if lang == "en" and category in ("treatment", "test"):
                    text_lower = text.lower()
                    skip_patterns = {
                        "therapy", "transplant", "transplantation", "medication",
                        "drug", "dose", "dosage", "infusion", "injection",
                        "biopsy", "scan", "imaging", "mri", "ct scan",
                        "x-ray", "xray", "ultrasound", "echocardiography",
                        "gene", "mutation", "allele", "genotype", "chromosome",
                        "protein", "receptor", "kinase", "inhibitor",
                        "assay", "pcr", "elisa", "electrophoresis",
                        "surgery", "surgical", "resection", "excision",
                        "antibiotic", "antifungal", "antiviral", "steroid",
                        "ibuprofen", "acetaminophen", "prednisone",
                        "chemotherapy", "radiation", "ventilator", "intubat",
                        "sedated", "anesthesia", "catheter",
                    }
                    if any(p in text_lower for p in skip_patterns) or len(text) <= 3:
                        entry = {
                            "text": text,
                            "ner_score": ent.get("score", 0),
                            "negated": ent.get("negated", False),
                            "negation_cue": ent.get("negation_cue", ""),
                            "hpo_id": None,
                            "hpo_name": None,
                            "expanded_text": text,
                            "match_type": "skipped_non_phenotype",
                            "confidence": 0.0,
                            "matched": False,
                            "umls_cui": None,
                        }
                        normalized[category].append(entry)
                        continue

                # Extract surrounding context for SapBERT disambiguation
                context = None
                if source_text:
                    start = ent.get("start", -1)
                    if start >= 0:
                        ctx_start = max(0, start - 80)
                        ctx_end = min(len(source_text), start + len(text) + 80)
                        context = source_text[ctx_start:ctx_end]

                norm = self.normalize_entity(text, lang=lang, context=context)

                entry = {
                    "text": text,
                    "ner_score": ent.get("score", 0),
                    "negated": ent.get("negated", False),
                    "negation_cue": ent.get("negation_cue", ""),
                    "hpo_id": norm["hpo_id"],
                    "hpo_name": norm["hpo_name"],
                    "expanded_text": norm["expanded_text"],
                    "match_type": norm["match_type"],
                    "confidence": norm["confidence"],
                    "matched": norm["matched"],
                    "umls_cui": norm["umls_cui"],
                }
                normalized[category].append(entry)

                if norm["matched"]:
                    matched += 1
                    if norm["hpo_id"]:
                        all_hpo_ids.add(norm["hpo_id"])

        # Add numeric phenotypes
        if numeric_phenotypes:
            normalized["numeric_phenotypes"] = numeric_phenotypes
            for np_item in numeric_phenotypes:
                if np_item.get("hpo_id"):
                    all_hpo_ids.add(np_item["hpo_id"])

        # ── Text Scanner: find HPO terms NER missed ──
        # Scans source text directly for known HPO labels/synonyms
        if source_text:
            scanned = self.text_scanner.scan(source_text, existing_hpo_ids=set(all_hpo_ids))
            if scanned:
                if "problem" not in normalized:
                    normalized["problem"] = []
                for s in scanned:
                    entry = {
                        "text": s["text"],
                        "ner_score": s["score"],
                        "negated": False,
                        "negation_cue": "",
                        "hpo_id": s["hpo_id"],
                        "hpo_name": s["hpo_name"],
                        "expanded_text": s["text"],
                        "match_type": s["match_type"],
                        "confidence": s["confidence"],
                        "matched": True,
                        "umls_cui": None,
                    }
                    self.umls_mapper.enrich_entity(entry)
                    normalized["problem"].append(entry)
                    matched += 1
                    total += 1
                    all_hpo_ids.add(s["hpo_id"])

        # ORDO disease matching (with text-based disease name detection)
        ordo_candidates = self.ordo_matcher.match_diseases(
            all_hpo_ids, top_k=5, source_text=source_text
        )
        normalized["ordo_candidates"] = ordo_candidates

        # Stats
        normalized["stats"] = {
            "total": total, "matched": matched,
            "unmatched": total - matched,
            "match_rate": round(matched / total * 100, 1) if total > 0 else 0,
            "unique_hpo": len(all_hpo_ids),
            "ordo_matches": len(ordo_candidates),
        }

        return normalized
