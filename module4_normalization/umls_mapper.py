"""
Module 4.3 — UMLS CUI Mapper
Maps HPO terms to UMLS Concept Unique Identifiers using cross-references
extracted from the HPO OWL ontology file.

Architecture role (per mémoire Ch4):
  Entity → UMLS CUI → HPO → ORDO
  UMLS serves as the terminological pivot between systems.
"""

from log_config import get_logger

logger = get_logger(__name__)


class UMLSMapper:
    """Maps between HPO IDs and UMLS CUIs using HPO cross-references."""

    def __init__(self, hpo_terms: list[dict]):
        # HPO ID → list of UMLS CUIs
        self.hpo_to_umls = {}
        # UMLS CUI → HPO ID (reverse lookup)
        self.umls_to_hpo = {}
        self._build_mappings(hpo_terms)

    def _build_mappings(self, terms: list[dict]):
        """Build bidirectional HPO ↔ UMLS mappings from xrefs."""
        for term in terms:
            hpo_id = term["id"]
            umls_cuis = []
            for xref in term.get("xrefs", []):
                if xref.startswith("UMLS:"):
                    cui = xref.replace("UMLS:", "").strip()
                    umls_cuis.append(cui)
                    if cui not in self.umls_to_hpo:
                        self.umls_to_hpo[cui] = hpo_id
            if umls_cuis:
                self.hpo_to_umls[hpo_id] = umls_cuis

        logger.info("UMLSMapper: %d HPO->UMLS, %d UMLS->HPO mappings",
                    len(self.hpo_to_umls), len(self.umls_to_hpo))

    def get_umls_cuis(self, hpo_id: str) -> list[str]:
        """Get UMLS CUIs for a given HPO ID."""
        return self.hpo_to_umls.get(hpo_id, [])

    def get_hpo_from_cui(self, cui: str) -> str | None:
        """Get HPO ID from a UMLS CUI."""
        return self.umls_to_hpo.get(cui)

    def enrich_entity(self, entity: dict) -> dict:
        """Add UMLS CUI(s) to a normalized entity dict."""
        hpo_id = entity.get("hpo_id")
        if hpo_id:
            cuis = self.get_umls_cuis(hpo_id)
            entity["umls_cui"] = cuis[0] if cuis else None
            entity["umls_all"] = cuis
        else:
            entity["umls_cui"] = None
            entity["umls_all"] = []
        return entity
