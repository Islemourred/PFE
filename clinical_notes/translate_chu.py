"""
Fast CHU French → English translator using Google Translate via deep-translator.
Much faster than MarianMT on CPU (~30 seconds for all 30 reports vs 20+ minutes).
"""

import os
import sys
import json
import time

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def translate_reports():
    """Translate CHU French reports to English using Google Translate."""
    from deep_translator import GoogleTranslator
    from clinical_notes.chu_reports import load_chu_reports

    translator = GoogleTranslator(source='fr', target='en')
    reports = load_chu_reports()

    print(f"\n{'='*70}")
    print(f"  FAST CHU TRANSLATOR (Google Translate via deep-translator)")
    print(f"  Reports: {len(reports)}")
    print(f"{'='*70}\n")

    translated = []
    total_start = time.time()

    for i, report in enumerate(reports, 1):
        note_id = report["note_id"]
        text = report["text"]
        disease = report.get("disease", report.get("filename", ""))

        start = time.time()

        # Google Translate has 5000 char limit per call, split if needed
        chunks = split_text(text, max_chars=4500)
        en_chunks = []

        for chunk in chunks:
            if not chunk.strip():
                continue
            try:
                result = translator.translate(chunk)
                en_chunks.append(result)
            except Exception as e:
                print(f"    [!] Chunk translation error: {e}")
                en_chunks.append(chunk)  # Keep original on failure
            time.sleep(0.3)  # Rate limit courtesy

        en_text = "\n".join(en_chunks)
        elapsed = time.time() - start

        print(f"  [{i:2d}/{len(reports)}] {note_id} — {disease[:40]:<40s} | "
              f"{len(text):5d} → {len(en_text):5d} chars | {elapsed:.1f}s")

        translated.append({
            "note_id": report["note_id"],
            "disease": disease,
            "text_fr": text,
            "text": en_text,
            "word_count": len(en_text.split()),
            "source": "CHU Oran (translated FR→EN via Google Translate)",
            "filename": report.get("filename", ""),
        })

    total_time = time.time() - total_start

    # Save
    out_dir = os.path.join(PROJECT_ROOT, "clinical_notes", "chu_translated")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "chu_reports_en.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(translated, f, indent=2, ensure_ascii=False)

    avg_words = sum(r["word_count"] for r in translated) / len(translated)
    print(f"\n{'='*70}")
    print(f"  DONE — {len(translated)} reports translated in {total_time:.1f}s")
    print(f"  Avg word count: {avg_words:.0f}")
    print(f"  Saved to: {out_path}")
    print(f"{'='*70}\n")

    return translated


def split_text(text: str, max_chars: int = 4500) -> list:
    """Split text into chunks under max_chars, preserving sentence boundaries."""
    import re
    sentences = re.split(r'(?<=[.!?;])\s+', text)
    chunks = []
    current = ""

    for sent in sentences:
        if len(current) + len(sent) + 1 > max_chars and current:
            chunks.append(current.strip())
            current = sent
        else:
            current = current + " " + sent if current else sent

    if current.strip():
        chunks.append(current.strip())

    return chunks


def load_translated_reports() -> list:
    """Load previously translated CHU reports."""
    path = os.path.join(PROJECT_ROOT, "clinical_notes", "chu_translated",
                        "chu_reports_en.json")
    if not os.path.exists(path):
        print("[!] No translated reports found. Run translate_reports() first.")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    translate_reports()
