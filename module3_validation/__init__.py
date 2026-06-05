# Module 3: Rule-based Validation
# NegEx negation detection, temporal reasoning, numeric phenotype parsing,
# and inconsistency detection — all deterministic, all explainable.

from .negex import NegExDetector
from .temporal import check_temporal_consistency
from .numeric import extract_numeric_phenotypes
from .inconsistency import detect_inconsistencies
