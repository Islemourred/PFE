"""
Phenopacket Builder — Generates ISO 4454:2022 (GA4GH) compliant output.
Now correctly populates the 'excluded' field from NegEx negation results.
"""

import time


def build_phenopacket(
    note_id: str,
    preprocessed: dict,
    validated: dict,
    normalized: dict,
    patient_info: dict = None,
) -> dict:
    """
    Build a Phenopacket from the complete pipeline output.

    Args:
        note_id: clinical note identifier
        preprocessed: Module 1 output (clean_text, phi_map, patient_info)
        validated: Module 3 output (entities with negation, warnings)
        normalized: Module 4 output (HPO/UMLS/ORDO enriched entities)
        patient_info: optional override for patient metadata
    """
    if patient_info is None:
        patient_info = preprocessed.get("patient_info", {})

    # Build subject
    subject = {"id": note_id}
    if patient_info.get("sex"):
        sex_map = {"male": "MALE", "female": "FEMALE"}
        subject["sex"] = sex_map.get(patient_info["sex"], "UNKNOWN_SEX")
    if patient_info.get("age"):
        subject["timeAtLastEncounter"] = {"age": {"iso8601duration": f"P{patient_info['age']}Y"}}

    # Build phenotypic features from normalized entities
    features = []
    seen_hpo = set()

    for category in ["problem", "treatment", "test"]:
        for entity in normalized.get(category, []):
            if not entity.get("matched") or not entity.get("hpo_id"):
                continue
            hpo_id = entity["hpo_id"]
            if hpo_id in seen_hpo:
                continue
            seen_hpo.add(hpo_id)

            feature = {
                "type": {
                    "id": hpo_id,
                    "label": entity.get("hpo_name", ""),
                },
                "excluded": entity.get("negated", False),
            }

            # Add UMLS cross-reference if available
            if entity.get("umls_cui"):
                feature["type"]["umls_cui"] = entity["umls_cui"]

            # Evidence
            evidence_parts = [
                f"NER: {entity.get('text', '')} ({entity.get('ner_score', 0):.3f})",
                f"Match: {entity.get('match_type', 'unknown')} ({entity.get('confidence', 0):.3f})",
            ]
            if entity.get("negated"):
                evidence_parts.append(f"Negated by: \"{entity.get('negation_cue', '')}\"")

            feature["evidence"] = [{
                "evidenceCode": {
                    "id": "ECO:0000033",
                    "label": "author statement supported by traceable reference",
                },
                "reference": {
                    "id": note_id,
                    "description": " | ".join(evidence_parts),
                },
            }]

            features.append(feature)

    # Add numeric phenotypes
    for np_item in normalized.get("numeric_phenotypes", []):
        hpo_id = np_item.get("hpo_id")
        if hpo_id and hpo_id not in seen_hpo:
            seen_hpo.add(hpo_id)
            features.append({
                "type": {"id": hpo_id, "label": np_item.get("hpo_name", "")},
                "excluded": False,
                "evidence": [{
                    "evidenceCode": {"id": "ECO:0000033", "label": "author statement supported by traceable reference"},
                    "reference": {
                        "id": note_id,
                        "description": f"Numeric: {np_item.get('source', '')} → {np_item.get('description', '')}",
                    },
                }],
            })

    # Build phenopacket
    phenopacket = {
        "id": f"phenopacket-{note_id}",
        "subject": subject,
        "phenotypicFeatures": features,
        "metaData": {
            "created": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "createdBy": "clinical-preanalysis-pipeline-v2",
            "phenopacketSchemaVersion": "2.0",
            "resources": [
                {
                    "id": "hp",
                    "name": "Human Phenotype Ontology",
                    "url": "https://hpo.jax.org",
                    "version": "2024-04-26",
                    "namespacePrefix": "HP",
                    "iriPrefix": "http://purl.obolibrary.org/obo/HP_",
                },
            ],
        },
    }

    # Add ORDO candidates as interpretations
    ordo = normalized.get("ordo_candidates", [])
    if ordo:
        phenopacket["interpretations"] = [{
            "id": f"interpretation-{note_id}",
            "progressStatus": "IN_PROGRESS",
            "diagnosis": {
                "disease": {
                    "id": ordo[0]["ordo_id"],
                    "label": ordo[0]["name"],
                },
                "score": ordo[0]["score"],
                "allCandidates": [
                    {"id": c["ordo_id"], "label": c["name"], "score": c["score"]}
                    for c in ordo
                ],
            },
        }]

    # Add validation warnings
    warnings = validated.get("warnings", {})
    all_warnings = (
        warnings.get("temporal", []) +
        warnings.get("inconsistencies", [])
    )
    if all_warnings:
        phenopacket["_validationWarnings"] = all_warnings

    # Pipeline stats
    stats = normalized.get("stats", {})
    negated_count = sum(
        1 for f in features if f.get("excluded", False)
    )
    phenopacket["_pipelineStats"] = {
        "totalEntities": stats.get("total", 0),
        "matchedHPO": stats.get("matched", 0),
        "unmatchedEntities": stats.get("unmatched", 0),
        "phenopacketFeatures": len(features),
        "negatedFeatures": negated_count,
        "numericPhenotypes": len(normalized.get("numeric_phenotypes", [])),
        "ordoCandidates": stats.get("ordo_matches", 0),
    }

    return phenopacket
