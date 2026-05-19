"""Analyze French pipeline output to diagnose matching issues."""
import sys, json, os
sys.stdout.reconfigure(encoding='utf-8')

for fname in sorted(os.listdir('output')):
    if 'full_output' not in fname:
        continue
    with open(os.path.join('output', fname), encoding='utf-8') as f:
        data = json.load(f)
    
    note_id = data.get('note_id', fname)
    print(f"\n{'='*60}")
    print(f"  {note_id}")
    print(f"{'='*60}")
    
    m4 = data.get('module4', {})
    
    for cat in ['problem', 'treatment', 'test']:
        ents = m4.get(cat, [])
        if ents:
            print(f"\n  [{cat.upper()}] ({len(ents)} entities)")
            for e in ents:
                neg = " [NEG]" if e.get("negated") else ""
                hpo = e.get("hpo_id", "")
                mt = e.get("match_type", "no_match")
                conf = e.get("confidence", 0)
                expanded = e.get("expanded_text", "")
                extra = f" -> {expanded}" if expanded != e["text"] else ""
                print(f"    {e['text'][:40]:40s} | {mt:12s} | conf={conf:.2f} | {hpo}{neg}{extra}")
    
    # Numeric
    np_list = m4.get('numeric_phenotypes', [])
    if np_list:
        print(f"\n  [NUMERIC] ({len(np_list)} phenotypes)")
        for p in np_list:
            print(f"    {p['hpo_name']:30s} ({p['hpo_id']}) <- {p['source']}")
    
    # ORDO
    ordo = m4.get('ordo_candidates', [])
    if ordo:
        print(f"\n  [ORDO] Top candidates:")
        for o in ordo[:3]:
            name = o.get('name_fr') or o['name']
            print(f"    {name:40s} | score={o['score']:.4f} | matched={o['matched_count']}/{o['total_disease_hpo']}")
    
    stats = m4.get('stats', {})
    print(f"\n  STATS: {stats}")
