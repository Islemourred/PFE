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

        # ── English noise filter: generic single-word entities ──
        EN_NOISE_WORDS = {
            # Administrative / non-clinical
            "disease", "syndrome", "disorder", "condition", "diagnosis",
            "pathology", "abnormality", "examination", "assessment",
            "treatment", "therapy", "medication", "hospitalization",
            "monitoring", "surveillance", "management", "support",
            "evolution", "consultation", "admission", "discharge",
            # Generic body/noise words
            "noise", "damage", "drawing", "clinical", "medical",
            "normal", "correct", "negative", "positive", "presence",
            "absence", "concept", "notion", "history", "report",
            # Single anatomical fragments
            "respiratory", "cardiac", "hepatic", "renal", "digestive",
            "pulmonary", "thoracic", "abdominal", "cervical",
            # Qualifiers that are not phenotypes alone
            "severe", "moderate", "mild", "chronic", "acute",
            "bilateral", "left", "right", "proximal", "distal",
            "progressive", "recurrent", "intermittent",
        }

        # Minimum NER score threshold for English
        EN_MIN_NER_SCORE = 0.55

        for category, ents in entities.items():
            if not isinstance(ents, list):
                continue
            normalized[category] = []
            for ent in ents:
                text = ent["text"]
                total += 1

                # ── Fix 1+2: English noise filter (single words + low NER) ──
                if lang == "en":
                    text_lower = text.lower().strip()
                    words = text_lower.split()
                    ner_score = ent.get("score", 0)

                    # Skip single generic words
                    if len(words) == 1 and text_lower in EN_NOISE_WORDS:
                        entry = {
                            "text": text, "ner_score": ner_score,
                            "negated": ent.get("negated", False),
                            "negation_cue": ent.get("negation_cue", ""),
                            "hpo_id": None, "hpo_name": None,
                            "expanded_text": text,
                            "match_type": "skipped_en_noise",
                            "confidence": 0.0, "matched": False,
                            "umls_cui": None,
                        }
                        normalized[category].append(entry)
                        continue

                    # Skip very short entities (≤3 chars)
                    if len(text_lower) <= 3:
                        entry = {
                            "text": text, "ner_score": ner_score,
                            "negated": ent.get("negated", False),
                            "negation_cue": ent.get("negation_cue", ""),
                            "hpo_id": None, "hpo_name": None,
                            "expanded_text": text,
                            "match_type": "skipped_too_short",
                            "confidence": 0.0, "matched": False,
                            "umls_cui": None,
                        }
                        normalized[category].append(entry)
                        continue

                    # Skip low NER score entities (sub-word fragments)
                    if ner_score < EN_MIN_NER_SCORE:
                        entry = {
                            "text": text, "ner_score": ner_score,
                            "negated": ent.get("negated", False),
                            "negation_cue": ent.get("negation_cue", ""),
                            "hpo_id": None, "hpo_name": None,
                            "expanded_text": text,
                            "match_type": "skipped_low_ner_score",
                            "confidence": 0.0, "matched": False,
                            "umls_cui": None,
                        }
                        normalized[category].append(entry)
                        continue

                # ══════════════════════════════════════════════════════════
                # ARCHITECTURAL RULE: Only "problem" entities are HPO-relevant
                # ══════════════════════════════════════════════════════════
                # HPO = Human Phenotype Ontology = symptoms, signs, abnormalities
                # "treatment" = drugs, procedures → NOT phenotypes
                # "test"      = lab names, imaging, genes → NOT phenotypes
                # Only "problem" (symptoms/signs/diseases) should be normalized to HPO
                if category in ("treatment", "test"):
                    entry = {
                        "text": text,
                        "ner_score": ent.get("score", 0),
                        "negated": ent.get("negated", False),
                        "negation_cue": ent.get("negation_cue", ""),
                        "hpo_id": None,
                        "hpo_name": None,
                        "expanded_text": text,
                        "match_type": f"skipped_{category}",
                        "confidence": 0.0,
                        "matched": False,
                        "umls_cui": None,
                    }
                    normalized[category].append(entry)
                    continue

                # ── French problem-category noise filter ──
                # Some "problem" entities in French are actually qualifiers,
                # admin terms, or non-specific words — not phenotypes.
                if lang == "fr" and category == "problem":
                    text_lower = text.lower().strip()
                    fr_skip_qualifiers = {
                        # Non-specific qualifiers that produce noise HPOs
                        "chronique", "aigu", "aiguë", "sévère",
                        "modéré", "modérée", "léger", "légère",
                        "gauche", "droit", "droite", "bilatéral",
                        "proximal", "distal", "antérieur", "postérieur",
                        "progressif", "progressive", "récidivant",
                        # Administrative / non-clinical
                        "hospitalisé", "hospitalisation", "consultation",
                        "suivi", "contrôle", "évolution",
                        "bon état général", "beg", "état général conservé",
                        "vaccin", "vaccination", "bcg",
                    }
                    fr_skip_patterns = {
                        "bilan d", "bilan du", "bilan de",
                        "examen d", "examen du", "examen de",
                    }
                    if (text_lower in fr_skip_qualifiers
                            or any(p in text_lower for p in fr_skip_patterns)
                            or len(text) <= 2):
                        entry = {
                            "text": text,
                            "ner_score": ent.get("score", 0),
                            "negated": ent.get("negated", False),
                            "negation_cue": ent.get("negation_cue", ""),
                            "hpo_id": None, "hpo_name": None,
                            "expanded_text": text,
                            "match_type": "skipped_qualifier_fr",
                            "confidence": 0.0, "matched": False,
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

                # ── Fix 3: Skip low-confidence SapBERT for short EN terms ──
                if (lang == "en" and norm["match_type"] == "sapbert_similarity"
                        and len(text.split()) == 1 and norm["confidence"] < 0.80):
                    entry["hpo_id"] = None
                    entry["hpo_name"] = None
                    entry["match_type"] = "sapbert_rejected_low_conf"
                    entry["confidence"] = 0.0
                    entry["matched"] = False
                    entry["umls_cui"] = None
                elif norm["matched"]:
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

        # ── Fix 4: Deduplicate HPO IDs across all categories ──
        # Remove duplicate entities that map to the same HPO ID,
        # keeping only the highest-confidence match for each HPO.
        seen_hpo = {}  # hpo_id -> best entry
        for category in normalized:
            if not isinstance(normalized[category], list):
                continue
            deduped = []
            for entry in normalized[category]:
                hpo_id = entry.get("hpo_id")
                if hpo_id and entry.get("matched"):
                    if hpo_id in seen_hpo:
                        # Keep the one with higher confidence
                        prev = seen_hpo[hpo_id]
                        if entry["confidence"] > prev["confidence"]:
                            # Mark previous as duplicate
                            prev["match_type"] = "deduplicated"
                            prev["matched"] = False
                            prev["hpo_id"] = None
                            prev["hpo_name"] = None
                            seen_hpo[hpo_id] = entry
                            deduped.append(entry)
                        else:
                            # Mark current as duplicate
                            entry["match_type"] = "deduplicated"
                            entry["matched"] = False
                            entry["hpo_id"] = None
                            entry["hpo_name"] = None
                            deduped.append(entry)
                    else:
                        seen_hpo[hpo_id] = entry
                        deduped.append(entry)
                else:
                    deduped.append(entry)
            normalized[category] = deduped

        # Recount matched after dedup
        matched = sum(
            1 for cat in normalized.values()
            if isinstance(cat, list)
            for e in cat if e.get("matched")
        )
        all_hpo_ids = {
            e["hpo_id"] for cat in normalized.values()
            if isinstance(cat, list)
            for e in cat if e.get("matched") and e.get("hpo_id")
        }

        # ORDO disease matching (semantic similarity via HPO ontology)
        ordo_candidates = self.ordo_matcher.match_diseases(
            all_hpo_ids, top_k=10, source_text=source_text
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
