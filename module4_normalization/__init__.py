# Module 4: Ontological Normalization
# Hybrid normalization: Abbreviation expansion → Exact HPO match → SapBERT
# Plus UMLS CUI mapping and ORDO rare disease matching.

from .normalizer import NormalizationPipeline
from .ordo_matcher import ORDOMatcher
