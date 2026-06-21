"""
Update all medical_reports in Supabase to use HTML content from mammoth.
Converts each .docx file to formatted HTML preserving tables, bold, headers, etc.
"""

import os
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import mammoth
from supabase import create_client

SUPABASE_URL = "https://erwwmxppovtuzikyfakf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVyd3dteHBwb3Z0dXppa3lmYWtmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE2MjY2MjUsImV4cCI6MjA5NzIwMjYyNX0.D4cW01s4uAPUUi7c5sWCgFmykQD4JMWEwhQy9uSLeJM"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "clinical_notes", "reports")


def convert_docx_to_html(filepath):
    """Convert .docx to HTML using mammoth, preserving formatting."""
    with open(filepath, "rb") as f:
        result = mammoth.convert_to_html(f)
    return result.value


def main():
    files = sorted([
        f for f in os.listdir(REPORTS_DIR)
        if f.endswith(".docx") and not f.startswith("~$")
    ])
    print(f"Found {len(files)} .docx files in {REPORTS_DIR}\n")

    updated = 0
    created = 0
    skipped = 0
    errors = 0

    for i, filename in enumerate(files):
        filepath = os.path.join(REPORTS_DIR, filename)
        print(f"[{i+1}/{len(files)}] {filename}")

        try:
            html = convert_docx_to_html(filepath)
        except Exception as e:
            print(f"  ❌ Conversion error: {e}")
            errors += 1
            continue

        if len(html) < 50:
            print(f"  ⚠️ Skipped (too short: {len(html)} chars)")
            skipped += 1
            continue

        html_truncated = html[:50000]

        # Find existing report by filename
        existing = supabase.table("medical_reports") \
            .select("id,filename") \
            .eq("filename", filename) \
            .execute()

        if existing.data and len(existing.data) > 0:
            # Update existing report with HTML content
            report_id = existing.data[0]["id"]
            try:
                supabase.table("medical_reports") \
                    .update({
                        "content_text": html_truncated,
                        "char_count": len(html),
                    }) \
                    .eq("id", report_id) \
                    .execute()
                updated += 1
                print(f"  ✅ Updated with HTML ({len(html)} chars)")
            except Exception as e:
                print(f"  ❌ Update error: {e}")
                errors += 1
        else:
            print(f"  ⚠️ No matching report found in DB (skipped)")
            skipped += 1

    print(f"\n{'='*50}")
    print(f"✅ {updated} reports updated with HTML")
    print(f"⚠️ {skipped} skipped")
    print(f"❌ {errors} errors")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
