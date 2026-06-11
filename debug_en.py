"""Debug script: Compare French vs English pipeline behavior."""
import json, os, glob, sys
sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

def analyze_lang(subdir, label):
    path = os.path.join(OUTPUT_DIR, subdir)
    files = sorted(glob.glob(os.path.join(path, "*_full_output.json")))
    
    total_problem, total_treatment, total_test = 0, 0, 0
    total_matched, total_unmatched = 0, 0
    match_type_counts = {}
    unmatched_examples = []
    skipped_count = 0
    fragment_examples = []
    
    for f in files:
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        m4 = d.get("module4", {})
        
        for cat in ["problem", "treatment", "test"]:
            ents = m4.get(cat, [])
            if cat == "problem": total_problem += len(ents)
            elif cat == "treatment": total_treatment += len(ents)
            else: total_test += len(ents)
            
            for e in ents:
                mt = e.get("match_type", "none")
                match_type_counts[mt] = match_type_counts.get(mt, 0) + 1
                
                if e.get("matched"):
                    total_matched += 1
                else:
                    total_unmatched += 1
                    if mt == "skipped_non_phenotype":
                        skipped_count += 1
                    if len(unmatched_examples) < 40:
                        unmatched_examples.append(f"[{cat}] {e['text'][:60]} (type={mt})")
                    
                    # Check for fragments
                    txt = e["text"]
                    if len(txt) <= 5 or (len(txt.split()) == 1 and txt[0].islower()):
                        fragment_examples.append(f"[{cat}] '{txt}'")
    
    print(f"\n{'='*70}")
    print(f"  {label} — {len(files)} reports")
    print(f"{'='*70}")
    print(f"  Entities: problem={total_problem}, treatment={total_treatment}, test={total_test}")
    print(f"  Total: {total_problem+total_treatment+total_test}")
    print(f"  Matched: {total_matched}, Unmatched: {total_unmatched}")
    print(f"  Skipped (non_phenotype): {skipped_count}")
    print(f"\n  Match type distribution:")
    for mt, cnt in sorted(match_type_counts.items(), key=lambda x: -x[1]):
        print(f"    {mt:35s} {cnt:5d}")
    
    print(f"\n  Sample UNMATCHED entities (first 40):")
    for ex in unmatched_examples[:40]:
        print(f"    {ex}")
    
    if fragment_examples:
        print(f"\n  Possible FRAGMENTS ({len(fragment_examples)}):")
        for ex in fragment_examples[:20]:
            print(f"    {ex}")

# Run for first 3 English reports - detailed view
print("\n" + "="*70)
print("  DETAILED VIEW: First 3 English reports")
print("="*70)

en_path = os.path.join(OUTPUT_DIR, "pubmed_evaluation")
en_files = sorted(glob.glob(os.path.join(en_path, "*_full_output.json")))[:3]
for f in en_files:
    with open(f, encoding="utf-8") as fh:
        d = json.load(fh)
    nid = d.get("note_id", "?")
    m4 = d.get("module4", {})
    print(f"\n  --- {nid} ---")
    for cat in ["problem", "treatment", "test"]:
        ents = m4.get(cat, [])
        if not ents: continue
        print(f"  [{cat.upper()}]")
        for e in ents:
            status = "✓" if e.get("matched") else "✗"
            neg = " [NEG]" if e.get("negated") else ""
            hpo = e.get('hpo_id') or ''
            mt = e.get('match_type') or ''
            print(f"    {status} {e['text'][:45]:45s} → {hpo:15s} {mt:25s}{neg}")

# Compare FR vs EN
analyze_lang("chu_evaluation", "FRENCH (CHU)")
analyze_lang("pubmed_evaluation", "ENGLISH (PubMed)")
