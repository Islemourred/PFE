"""
Bulk import all .docx reports from clinical_notes/reports/ into Supabase.
Creates patient dossiers with extracted info and links reports to them.
"""

import os
import sys
import re
import json
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from docx import Document
from supabase import create_client

SUPABASE_URL = "https://erwwmxppovtuzikyfakf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVyd3dteHBwb3Z0dXppa3lmYWtmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE2MjY2MjUsImV4cCI6MjA5NzIwMjYyNX0.D4cW01s4uAPUUi7c5sWCgFmykQD4JMWEwhQy9uSLeJM"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Authenticate as admin for RLS
auth_result = supabase.auth.sign_in_with_password({
    "email": "admin@clinicalpfe.dz",
    "password": "ClinicalPFE2026!"
})
print(f"✅ Authenticated as {auth_result.user.email}\n")

REPORTS_DIR = os.path.join(PROJECT_ROOT, "clinical_notes", "reports")


def extract_docx_text(filepath):
    try:
        doc = Document(filepath)
        return "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
    except:
        return ""


def extract_patient_info(text):
    info = {}

    # Dossier number
    dossier_num = re.search(r'(?:Dossier\s+)?N[°0o]\s*(?:Dossier)?\s*[:：]\s*(\d{3,6})', text, re.IGNORECASE)
    if dossier_num:
        info["dossier_number"] = dossier_num.group(1).strip()
    
    name_age = re.search(
        r"(?:L['\u2019]enfant|Le\s+nourrisson|Le\s+patient|La\s+patiente|L['\u2019]adolescent)\s+"
        r"([A-Z\u00C0-\u0178a-z\u00e0-\u00ff\s\-]+?)(?:,|\s+)\s*(?:\u00e2g\u00e9e?|ag\u00e9e?|age)\s+(?:de\s+)?(\d+\s*(?:ans?|mois|jours?)(?:\s+et\s+(?:demi|\d+\s*mois))?)",
        text, re.IGNORECASE
    )
    if name_age:
        info["full_name"] = name_age.group(1).strip().title()
        info["age"] = name_age.group(2).strip()

    if re.search(r"\bfille\b|f\u00e9minin|La\s+patiente", text, re.IGNORECASE):
        info["gender"] = "F"
    elif re.search(r"\bgar\u00e7on\b|masculin|Le\s+patient|Sexe\s+masculin", text, re.IGNORECASE):
        info["gender"] = "M"

    origin = re.search(
        r"originaire\s+(?:et\s+demeurant\s+)?(?:de|d['\u2019]|\u00e0)\s+([A-Z\u00C0-\u0178a-z\u00e0-\u00ff\s\-]+?)(?:[,.]|\s+(?:suivi|issue|adress))",
        text, re.IGNORECASE
    )
    if origin:
        info["origin"] = origin.group(1).strip().title()
        info["residence"] = info["origin"]

    father = re.search(r"P\u00e8re\s*:\s*(\d+\s*ans?[^.\n]*)", text, re.IGNORECASE)
    if father: info["parent_father"] = father.group(1).strip()

    mother = re.search(r"M\u00e8re\s*:\s*(\d+\s*ans?[^.\n]*)", text, re.IGNORECASE)
    if mother: info["parent_mother"] = mother.group(1).strip()

    consang = re.search(r"[Cc]onsanguinit[\u00e9e]\s+(?:du?\s+)?([^.\n]+)", text)
    if consang: info["consanguinity"] = consang.group(1).strip()

    diag = re.search(r"[Dd]iagnostic\s+principal\s*[:]\s*([^\n.]+)", text)
    if diag: info["principal_diagnosis"] = diag.group(1).strip()

    assoc = re.search(r"[Dd]iagnostics?\s+associ[\u00e9e]s?\s*[:]\s*([^\n]+)", text)
    if assoc:
        val = assoc.group(1).strip()
        if val.lower() != "aucun": info["associated_diagnoses"] = val

    diag_date = re.search(r"[Dd]ate\s+d[ue]\s+diagnostic\s*[:]\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})", text)
    if diag_date:
        try:
            d = diag_date.group(1).replace("/", "-").split("-")
            info["date_of_diagnosis"] = f"{d[2]}-{d[1].zfill(2)}-{d[0].zfill(2)}"
        except: pass

    age_diag = re.search(r"[Aa]ge\s+(?:au|de)\s+diagnostic\s*[:]\s*([^\n.]+)", text)
    if age_diag: info["age_at_diagnosis"] = age_diag.group(1).strip()

    doctor = re.search(r"\b(?:Dr|DR)\s+([A-Z\u00C0-\u0178][a-z\u00e0-\u00ff]+)", text)
    if doctor: info["treating_doctor"] = doctor.group(1).strip().title()

    return info


def extract_from_filename(filename):
    name = filename.replace(".docx", "").replace("_", " ")
    info = {}

    doc_match = re.search(r"(?:DR|Dr|dr)[\s._]+([A-Za-z\u00C0-\u00ff]+)", name, re.IGNORECASE)
    if doc_match: info["treating_doctor"] = doc_match.group(1).strip().title()

    pathologies = [
        "Mucoviscidose", "Wiskott-Aldrich", "Wiskott Aldrich",
        "Agammaglobulin\u00e9mie", "SCID", "SKID",
        "DIP", "D\u00e9ficit", "Deficit", "SMA", "HIES", "HLA-DR", "HLA DR"
    ]
    for p in pathologies:
        if p.lower() in name.lower():
            info["principal_diagnosis"] = p
            break

    patient_name = name
    dr_pos = re.search(r"\b(?:DR|Dr|dr)\b", patient_name)
    if dr_pos: patient_name = patient_name[:dr_pos.start()].strip()
    for p in pathologies:
        patient_name = re.sub(re.escape(p), '', patient_name, flags=re.IGNORECASE).strip()
    patient_name = re.sub(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', '', patient_name).strip()
    patient_name = re.sub(r'\s+', ' ', patient_name).strip(' -_,.')
    patient_name = re.sub(r'^(RM|CERTIFICAT MEDICAL|Novembre|D\u00e9cembre|Janvier|F\u00e9vrier|Mars|Avril|Mai|Juin)\s*', '', patient_name, flags=re.IGNORECASE).strip()
    patient_name = re.sub(r'\s*(Novembre|D\u00e9cembre|Janvier|F\u00e9vrier|Mars|Avril|Mai|Juin|recu|Copie|HDJ|re\u00e7u)\s*\d*\s*$', '', patient_name, flags=re.IGNORECASE).strip()
    patient_name = patient_name.strip(' -_,.')

    if len(patient_name) >= 2:
        info["full_name"] = patient_name.title()

    return info


def main():
    files = sorted([
        f for f in os.listdir(REPORTS_DIR)
        if f.endswith(".docx") and not f.startswith("~$")
    ])
    print(f"Found {len(files)} .docx files\n")

    created_dossiers = 0
    created_reports = 0
    errors = 0

    for i, filename in enumerate(files):
        filepath = os.path.join(REPORTS_DIR, filename)
        print(f"[{i+1}/{len(files)}] {filename}")

        text = extract_docx_text(filepath)
        if len(text) < 30:
            print(f"  ⚠️ Skipped (too short: {len(text)} chars)")
            errors += 1
            continue

        # Extract info from content + filename
        info = extract_patient_info(text)
        fallback = extract_from_filename(filename)

        if not info.get("full_name"):
            info["full_name"] = fallback.get("full_name", "Inconnu")
        if not info.get("treating_doctor"):
            info["treating_doctor"] = fallback.get("treating_doctor")
        if not info.get("principal_diagnosis"):
            info["principal_diagnosis"] = fallback.get("principal_diagnosis")
        if not info.get("gender"):
            info["gender"] = "Inconnu"

        patient_name = info.get("full_name", "Inconnu")
        print(f"  👤 {patient_name} | {info.get('age', '?')} | {info.get('principal_diagnosis', '?')}")

        # Check if dossier already exists (by dossier_number or name)
        dossier_number = info.get("dossier_number")
        existing = None
        if dossier_number:
            existing = supabase.table("patient_dossiers") \
                .select("id") \
                .eq("dossier_number", dossier_number) \
                .execute()
            print(f"  🔢 Dossier N°{dossier_number}")
        
        if not existing or not existing.data:
            existing = supabase.table("patient_dossiers") \
                .select("id") \
                .ilike("full_name", f"%{patient_name}%") \
                .execute()

        if existing.data and len(existing.data) > 0:
            dossier_id = existing.data[0]["id"]
            print(f"  📁 Existing dossier found")
        else:
            # Create dossier
            dossier_data = {k: v for k, v in info.items() if v and k in (
                "full_name", "age", "gender", "origin", "residence",
                "parent_father", "parent_mother", "consanguinity", "siblings_info",
                "principal_diagnosis", "associated_diagnoses", "date_of_diagnosis",
                "age_at_diagnosis", "treating_doctor", "current_treatment", "dossier_number"
            )}
            try:
                result = supabase.table("patient_dossiers").insert(dossier_data).execute()
                dossier_id = result.data[0]["id"]
                created_dossiers += 1
                print(f"  ✅ Dossier created ({len(dossier_data)} fields)")
            except Exception as e:
                print(f"  ❌ Dossier error: {e}")
                errors += 1
                continue

        # Check if report already exists
        existing_report = supabase.table("medical_reports") \
            .select("id") \
            .eq("filename", filename) \
            .execute()

        if existing_report.data and len(existing_report.data) > 0:
            # Update existing report to link to dossier
            supabase.table("medical_reports") \
                .update({"dossier_id": dossier_id}) \
                .eq("id", existing_report.data[0]["id"]) \
                .execute()
            print(f"  🔗 Existing report linked to dossier")
        else:
            # Create report linked to dossier
            try:
                supabase.table("medical_reports").insert({
                    "filename": filename,
                    "patient_name": patient_name,
                    "doctor_name": info.get("treating_doctor"),
                    "pathology": info.get("principal_diagnosis"),
                    "file_size_bytes": os.path.getsize(filepath),
                    "char_count": len(text),
                    "content_text": text[:50000],
                    "dossier_id": dossier_id,
                }).execute()
                created_reports += 1
                print(f"  📄 Report created & linked")
            except Exception as e:
                print(f"  ❌ Report error: {e}")
                errors += 1

    print(f"\n{'='*50}")
    print(f"✅ {created_dossiers} dossiers created")
    print(f"📄 {created_reports} reports created")
    print(f"❌ {errors} errors")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
