"""
CHU Oran Clinical Reports Loader

Dynamically loads all .docx reports from clinical_notes/reports/
Returns a list of (note_id, text) tuples ready for pipeline processing.

Reports: 39 real clinical cases from CHU Oran (Nov 2025 — May 2026)
Pathologies: Wiskott-Aldrich, Mucoviscidose, Agammaglobulinémie,
             SCID, Ataxie-télangiectasie, SMA, HIES, HLA-DR deficiency, etc.
"""

import os
from docx import Document

REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")


def extract_docx_text(filepath: str) -> str:
    """Extract all text from a .docx file."""
    try:
        doc = Document(filepath)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        print(f"  [!] Error reading {os.path.basename(filepath)}: {e}")
        return ""


def load_chu_reports(reports_dir: str = REPORTS_DIR) -> list:
    """
    Load all .docx reports from the reports directory.

    Returns:
        List of dicts: [{"note_id": "CHU_FR_001", "filename": "...", "text": "..."}]
    """
    if not os.path.isdir(reports_dir):
        print(f"Reports directory not found: {reports_dir}")
        return []

    docx_files = sorted([
        f for f in os.listdir(reports_dir)
        if f.endswith(".docx") and not f.startswith("~$")
    ])

    reports = []
    for i, filename in enumerate(docx_files, start=1):
        filepath = os.path.join(reports_dir, filename)
        text = extract_docx_text(filepath)

        if len(text) < 50:
            print(f"  [!] Skipping {filename} (too short: {len(text)} chars)")
            continue

        note_id = f"CHU_FR_{i:03d}"
        reports.append({
            "note_id": note_id,
            "filename": filename,
            "text": text,
        })

    print(f"[OK] Loaded {len(reports)} CHU reports from {reports_dir}")
    return reports


def get_report_ids() -> list:
    """Return list of all note_ids."""
    return [r["note_id"] for r in load_chu_reports()]


# ── Quick test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    reports = load_chu_reports()
    for r in reports:
        print(f"  {r['note_id']}  |  {len(r['text']):>5} chars  |  {r['filename'][:60]}")
