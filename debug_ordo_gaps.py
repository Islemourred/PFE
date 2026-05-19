"""Debug: what HPO IDs are needed vs extracted for each French note."""
import sys, json, os
sys.stdout.reconfigure(encoding='utf-8')

# ORDO profiles
ORDO = {
    "ORPHA:586": {
        "name": "Mucoviscidose",
        "hpo": {"HP:0002110","HP:0006538","HP:0002035","HP:0001508","HP:0002240",
                "HP:0012735","HP:0002099","HP:0001738","HP:0001945","HP:0004401"},
    },
    "ORPHA:906": {
        "name": "Wiskott-Aldrich",
        "hpo": {"HP:0001873","HP:0000978","HP:0001888","HP:0000389","HP:0002719",
                "HP:0001903","HP:0000988","HP:0001744","HP:0002665"},
    },
    "ORPHA:47": {
        "name": "Agammaglobulinémie (Bruton)",
        "hpo": {"HP:0004430","HP:0002719","HP:0004313","HP:0002205",
                "HP:0006538","HP:0000388","HP:0002840","HP:0001888"},
    },
    "ORPHA:183660": {
        "name": "SCID",
        "hpo": {"HP:0004430","HP:0001888","HP:0001945","HP:0001508",
                "HP:0002090","HP:0001880","HP:0005403","HP:0002719",
                "HP:0002035","HP:0004315"},
    },
    "ORPHA:572": {
        "name": "HLA-DR deficiency",
        "hpo": {"HP:0004430","HP:0002719","HP:0001888","HP:0002090",
                "HP:0001508","HP:0002035"},
    },
}

NOTE_DISEASE = {
    "NOTE_FR_001": "ORPHA:586",
    "NOTE_FR_002": "ORPHA:906",
    "NOTE_FR_003": "ORPHA:47",
    "NOTE_FR_004": "ORPHA:183660",
    "NOTE_FR_005": "ORPHA:572",
}

for fname in sorted(os.listdir('output')):
    if 'full_output' not in fname or 'FR' not in fname:
        continue
    with open(os.path.join('output', fname), encoding='utf-8') as f:
        data = json.load(f)
    
    note_id = data.get('note_id', '')
    target_orpha = NOTE_DISEASE.get(note_id, '')
    target = ORDO.get(target_orpha, {})
    target_hpo = target.get('hpo', set())
    
    # Collect all HPO IDs found
    m4 = data.get('module4', {})
    found_hpo = set()
    for cat in ['problem', 'treatment', 'test']:
        for e in m4.get(cat, []):
            if e.get('hpo_id') and not e.get('negated', False):
                found_hpo.add(e['hpo_id'])
    for p in m4.get('numeric_phenotypes', []):
        if p.get('hpo_id'):
            found_hpo.add(p['hpo_id'])
    
    overlap = found_hpo & target_hpo
    missing = target_hpo - found_hpo
    
    print(f"\n{'='*50}")
    print(f"  {note_id} -> {target.get('name', '?')} ({target_orpha})")
    print(f"  Found HPO: {len(found_hpo)} | Target: {len(target_hpo)} | Overlap: {len(overlap)} | Missing: {len(missing)}")
    
    if overlap:
        print(f"  MATCHED: {sorted(overlap)}")
    if missing:
        print(f"  MISSING: {sorted(missing)}")
    if found_hpo - target_hpo:
        print(f"  EXTRA (not in disease profile): {sorted(found_hpo - target_hpo)}")
