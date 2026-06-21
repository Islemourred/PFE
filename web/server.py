"""
Flask API Server — Backend for the Clinical Pre-Analysis Web Interface.
Serves the pipeline execution and medical reports management endpoints.

Endpoints:
  POST /api/pipeline/run        — Run the full pipeline on uploaded/pasted text
  GET  /api/pipeline/status     — Check if pipeline models are loaded
  GET  /api/reports             — List all medical reports (from Supabase)
  GET  /api/reports/search      — Search reports by name/doctor/pathology
  POST /api/reports/upload      — Upload new .docx reports
  GET  /api/reports/<id>        — Get a specific report
  DELETE /api/reports/<id>      — Delete a report
  POST /api/reports/<id>/analyze — Send a report to the pipeline
  GET  /api/reports/sync        — Sync local .docx files to Supabase
"""

import os
import sys
import json
import time
import re
import tempfile
import traceback
from datetime import datetime

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from docx import Document
from supabase import create_client, Client

# ── Supabase Config ──────────────────────────────────────────
SUPABASE_URL = "https://erwwmxppovtuzikyfakf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVyd3dteHBwb3Z0dXppa3lmYWtmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE2MjY2MjUsImV4cCI6MjA5NzIwMjYyNX0.D4cW01s4uAPUUi7c5sWCgFmykQD4JMWEwhQy9uSLeJM"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── Reports Directory ────────────────────────────────────────
REPORTS_DIR = os.path.join(PROJECT_ROOT, "clinical_notes", "reports")

# ── Flask App ────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

# ── Pipeline (lazy-loaded) ───────────────────────────────────
pipeline_obj = None
pipeline_loading = False


def get_pipeline():
    """Lazy-load the pipeline (heavy ML models)."""
    global pipeline_obj, pipeline_loading
    if pipeline_obj is None and not pipeline_loading:
        pipeline_loading = True
        try:
            # Allow downloading models on first run
            # Once cached, they work offline automatically
            os.environ.pop("HF_HUB_OFFLINE", None)
            os.environ.pop("TRANSFORMERS_OFFLINE", None)
            os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
            os.environ["HF_DATASETS_OFFLINE"] = "1"
            print("[API] Loading FullPipeline (this may take a few minutes on first run)...")
            from pipeline import FullPipeline
            pipeline_obj = FullPipeline()
            print("[API] Pipeline loaded successfully!")
        except Exception as e:
            traceback.print_exc()
            pipeline_loading = False
            raise
        finally:
            pipeline_loading = False
    return pipeline_obj


# ── Helpers ──────────────────────────────────────────────────

def extract_docx_text(filepath: str) -> str:
    """Extract all text from a .docx file."""
    try:
        doc = Document(filepath)
        return "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        return ""


def extract_metadata_from_filename(filename: str) -> dict:
    """
    Parse patient name, doctor, date, pathology from filename.
    Examples:
      'BAGHDAD ISLEM 18-11-2025 DR TAMAZIRT.docx'
      'Azzemmou mahdi DIP Agammaglobulinémie Mars Djoudi.docx'
      'Amroune_Abdelaziz_DIP_Wiskott_Aldrich_Mars2026_Dr_Djoudi_recu_9.docx'
    """
    name = filename.replace(".docx", "").replace("_", " ")

    # Extract date patterns
    date_match = re.search(
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})', name
    )
    report_date = None
    if date_match:
        try:
            d = date_match.group(1).replace("/", "-")
            parts = d.split("-")
            if len(parts) == 3:
                report_date = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
        except:
            pass

    # Extract doctor name
    doctor_match = re.search(r'(?:DR|Dr|dr)[\s._]+([A-Za-zÀ-ÿ]+)', name, re.IGNORECASE)
    doctor = doctor_match.group(1).strip().title() if doctor_match else None

    # Known pathologies
    pathologies = [
        "Mucoviscidose", "Wiskott-Aldrich", "Wiskott Aldrich",
        "Agammaglobulinémie", "Agammaglobulinemie",
        "SCID", "SKID", "Ataxie-télangiectasie", "Ataxie télangiectasie",
        "Ataxie telangiectasie", "SMA", "HIES", "HLA-DR", "HLA DR",
        "DIP", "Déficit", "Deficit"
    ]
    pathology = None
    for p in pathologies:
        if p.lower() in name.lower():
            pathology = p
            break

    # Extract patient name (first part before date/DR/known pathology)
    patient_name = name
    # Remove date
    if date_match:
        patient_name = patient_name[:date_match.start()].strip()
    # Remove DR and everything after
    dr_pos = re.search(r'\b(?:DR|Dr|dr)\b', patient_name)
    if dr_pos:
        patient_name = patient_name[:dr_pos.start()].strip()
    # Remove pathology keywords
    for p in pathologies:
        patient_name = re.sub(re.escape(p), '', patient_name, flags=re.IGNORECASE).strip()
    # Clean up
    patient_name = re.sub(r'\s+', ' ', patient_name).strip(' -_,.')
    # Remove common prefixes
    patient_name = re.sub(r'^(RM|CERTIFICAT MEDICAL)\s*', '', patient_name, flags=re.IGNORECASE).strip()

    if len(patient_name) < 2:
        patient_name = name.split()[0] if name.split() else "Inconnu"

    return {
        "patient_name": patient_name.title(),
        "doctor_name": doctor,
        "report_date": report_date,
        "pathology": pathology,
    }


# ══════════════════════════════════════════════════════════════
# API ENDPOINTS
# ══════════════════════════════════════════════════════════════

# ── Pipeline Status ──────────────────────────────────────────
@app.route("/api/pipeline/status", methods=["GET"])
def pipeline_status():
    return jsonify({
        "loaded": pipeline_obj is not None,
        "loading": pipeline_loading,
    })


# ── Run Pipeline ─────────────────────────────────────────────
@app.route("/api/pipeline/run", methods=["POST"])
def run_pipeline():
    """Run the full 4-module pipeline on text or uploaded file."""
    print("[API] /api/pipeline/run called")
    start = time.time()

    # Get text from request
    raw_text = None
    source_name = "Texte collé"

    if "file" in request.files:
        file = request.files["file"]
        if file.filename:
            source_name = file.filename
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
                file.save(tmp.name)
                tmp_path = tmp.name
            try:
                if file.filename.endswith(".txt"):
                    with open(tmp_path, "r", encoding="utf-8", errors="replace") as f:
                        raw_text = f.read()
                else:
                    raw_text = extract_docx_text(tmp_path)
            finally:
                os.unlink(tmp_path)
    elif request.json and request.json.get("text"):
        raw_text = request.json["text"]
    elif request.form.get("text"):
        raw_text = request.form["text"]

    if not raw_text or len(raw_text.strip()) < 50:
        return jsonify({"error": "Le texte ne contient pas assez de contenu exploitable (minimum 50 caractères)."}), 400

    # Load pipeline
    try:
        print("[API] Loading pipeline...")
        pipe = get_pipeline()
        if pipe is None:
            return jsonify({"error": "Le pipeline est en cours de chargement. Réessayez dans quelques secondes."}), 503
        print("[API] Pipeline loaded successfully")
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Erreur de chargement du pipeline: {str(e)}"}), 500

    # Run pipeline
    try:
        output_dir = os.path.join(PROJECT_ROOT, "output", "web")
        os.makedirs(output_dir, exist_ok=True)

        result = pipe.process_and_save(
            clinical_text=raw_text,
            note_id="WEB_UPLOAD",
            output_dir=output_dir,
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Erreur lors de l'analyse: {str(e)}"}), 500

    elapsed = round(time.time() - start, 2)

    # Build response
    m2 = result.get("module2", {}).get("entities", {})
    m3 = result.get("module3", {})
    m4 = result.get("module4", {})
    stats = m4.get("stats", {})
    ordo = m4.get("ordo_candidates", [])
    numerics = m3.get("numeric_phenotypes", [])

    negated_count = sum(
        1 for cat in ["problem", "treatment", "test"]
        for e in m2.get(cat, []) if e.get("negated", False)
    )

    response = {
        "success": True,
        "source_name": source_name,
        "language": result.get("language", "unknown"),
        "processing_time": elapsed,
        "stats": {
            "total_entities": stats.get("total", 0),
            "matched_hpo": stats.get("matched", 0),
            "numeric_phenotypes": len(numerics),
            "negated_count": negated_count,
        },
        "entities": {
            "problem": m4.get("problem", []),
            "treatment": m4.get("treatment", []),
            "test": m4.get("test", []),
        },
        "numerics": numerics,
        "ordo_candidates": ordo,
        "phenopacket": result.get("phenopacket", {}),
        "source_text": raw_text[:5000],
        "char_count": len(raw_text),
    }

    # Save to Supabase
    try:
        supabase.table("pipeline_results").insert({
            "note_id": "WEB_UPLOAD",
            "language": result.get("language"),
            "source_text": raw_text[:10000],
            "total_entities": stats.get("total", 0),
            "matched_hpo": stats.get("matched", 0),
            "negated_count": negated_count,
            "numeric_phenotypes_count": len(numerics),
            "ordo_top_name": ordo[0]["name"] if ordo else None,
            "ordo_top_score": ordo[0]["score"] if ordo else 0,
            "processing_time_seconds": elapsed,
            "full_result": json.loads(json.dumps(response, default=str)),
            "phenopacket": result.get("phenopacket", {}),
        }).execute()
    except Exception as e:
        print(f"Warning: Could not save to Supabase: {e}")

    return jsonify(response)


# ── List Reports ─────────────────────────────────────────────
@app.route("/api/reports", methods=["GET"])
def list_reports():
    """List all medical reports from Supabase."""
    try:
        response = supabase.table("medical_reports") \
            .select("*") \
            .order("created_at", desc=True) \
            .execute()
        return jsonify({"reports": response.data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Search Reports ───────────────────────────────────────────
@app.route("/api/reports/search", methods=["GET"])
def search_reports():
    """Search reports by patient name, doctor, or pathology."""
    q = request.args.get("q", "").strip()
    if not q:
        return list_reports()

    try:
        response = supabase.table("medical_reports") \
            .select("*") \
            .or_(f"patient_name.ilike.%{q}%,doctor_name.ilike.%{q}%,pathology.ilike.%{q}%,filename.ilike.%{q}%,content_text.ilike.%{q}%") \
            .order("created_at", desc=True) \
            .execute()
        return jsonify({"reports": response.data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Get Single Report ────────────────────────────────────────
@app.route("/api/reports/<report_id>", methods=["GET"])
def get_report(report_id):
    """Get a specific report by ID."""
    try:
        response = supabase.table("medical_reports") \
            .select("*") \
            .eq("id", report_id) \
            .single() \
            .execute()
        return jsonify({"report": response.data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Upload Report ────────────────────────────────────────────
@app.route("/api/reports/upload", methods=["POST"])
def upload_report():
    """Upload new .docx reports."""
    if "files" not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist("files")
    uploaded = []

    for file in files:
        if not file.filename or not file.filename.endswith(".docx"):
            continue

        # Save to reports directory
        filepath = os.path.join(REPORTS_DIR, file.filename)
        file.save(filepath)

        # Extract text
        text = extract_docx_text(filepath)
        metadata = extract_metadata_from_filename(file.filename)

        # Save to Supabase
        try:
            result = supabase.table("medical_reports").insert({
                "filename": file.filename,
                "patient_name": metadata["patient_name"],
                "doctor_name": metadata["doctor_name"],
                "pathology": metadata["pathology"],
                "report_date": metadata["report_date"],
                "file_size_bytes": os.path.getsize(filepath),
                "char_count": len(text),
                "content_text": text[:50000],
            }).execute()
            uploaded.append(file.filename)
        except Exception as e:
            print(f"Error uploading {file.filename}: {e}")

    return jsonify({"uploaded": uploaded, "count": len(uploaded)})


# ── Delete Report ────────────────────────────────────────────
@app.route("/api/reports/<report_id>", methods=["DELETE"])
def delete_report(report_id):
    """Delete a report from Supabase and optionally from disk."""
    try:
        # Get report info first
        report = supabase.table("medical_reports") \
            .select("filename") \
            .eq("id", report_id) \
            .single() \
            .execute()

        # Delete from Supabase
        supabase.table("medical_reports") \
            .delete() \
            .eq("id", report_id) \
            .execute()

        # Optionally delete file from disk
        if report.data and report.data.get("filename"):
            filepath = os.path.join(REPORTS_DIR, report.data["filename"])
            if os.path.exists(filepath):
                os.remove(filepath)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Analyze Report ───────────────────────────────────────────
@app.route("/api/reports/<report_id>/analyze", methods=["POST"])
def analyze_report(report_id):
    """Send a stored report to the pipeline for analysis."""
    try:
        report = supabase.table("medical_reports") \
            .select("*") \
            .eq("id", report_id) \
            .single() \
            .execute()

        if not report.data or not report.data.get("content_text"):
            return jsonify({"error": "Report not found or empty"}), 404

        # Simulate a pipeline run request
        text = report.data["content_text"]
        source_name = report.data.get("filename", "Report")

        # Reuse the pipeline run logic
        pipe = get_pipeline()
        if pipe is None:
            return jsonify({"error": "Pipeline loading..."}), 503

        start = time.time()
        output_dir = os.path.join(PROJECT_ROOT, "output", "web")
        os.makedirs(output_dir, exist_ok=True)

        result = pipe.process_and_save(
            clinical_text=text,
            note_id=f"REPORT_{report_id[:8]}",
            output_dir=output_dir,
        )

        elapsed = round(time.time() - start, 2)
        m2 = result.get("module2", {}).get("entities", {})
        m3 = result.get("module3", {})
        m4 = result.get("module4", {})
        stats = m4.get("stats", {})
        ordo = m4.get("ordo_candidates", [])
        numerics = m3.get("numeric_phenotypes", [])
        negated_count = sum(
            1 for cat in ["problem", "treatment", "test"]
            for e in m2.get(cat, []) if e.get("negated", False)
        )

        response = {
            "success": True,
            "source_name": source_name,
            "language": result.get("language", "unknown"),
            "processing_time": elapsed,
            "stats": {
                "total_entities": stats.get("total", 0),
                "matched_hpo": stats.get("matched", 0),
                "numeric_phenotypes": len(numerics),
                "negated_count": negated_count,
            },
            "entities": {
                "problem": m4.get("problem", []),
                "treatment": m4.get("treatment", []),
                "test": m4.get("test", []),
            },
            "numerics": numerics,
            "ordo_candidates": ordo,
            "phenopacket": result.get("phenopacket", {}),
            "source_text": text[:5000],
            "char_count": len(text),
        }

        # Save to Supabase
        try:
            supabase.table("pipeline_results").insert({
                "report_id": report_id,
                "note_id": f"REPORT_{report_id[:8]}",
                "language": result.get("language"),
                "source_text": text[:10000],
                "total_entities": stats.get("total", 0),
                "matched_hpo": stats.get("matched", 0),
                "negated_count": negated_count,
                "numeric_phenotypes_count": len(numerics),
                "ordo_top_name": ordo[0]["name"] if ordo else None,
                "ordo_top_score": ordo[0]["score"] if ordo else 0,
                "processing_time_seconds": elapsed,
                "full_result": json.loads(json.dumps(response, default=str)),
                "phenopacket": result.get("phenopacket", {}),
            }).execute()
        except Exception as e:
            print(f"Warning: Could not save result to Supabase: {e}")

        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Download Original .docx File ───────────────────────────────────
@app.route("/api/reports/download/<path:filename>", methods=["GET"])
def download_docx(filename):
    """Download the original .docx file."""
    import urllib.parse
    filename = urllib.parse.unquote(filename)
    filepath = os.path.join(REPORTS_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


# ── Sync Local Reports to Supabase ───────────────────────────────
@app.route("/api/reports/sync", methods=["POST"])
def sync_reports():
    """Sync all local .docx files from clinical_notes/reports/ to Supabase."""
    if not os.path.isdir(REPORTS_DIR):
        return jsonify({"error": f"Reports directory not found: {REPORTS_DIR}"}), 404

    # Get existing filenames in Supabase
    try:
        existing = supabase.table("medical_reports") \
            .select("filename") \
            .execute()
        existing_names = {r["filename"] for r in existing.data}
    except:
        existing_names = set()

    docx_files = sorted([
        f for f in os.listdir(REPORTS_DIR)
        if f.endswith(".docx") and not f.startswith("~$")
    ])

    synced = []
    skipped = []

    for filename in docx_files:
        if filename in existing_names:
            skipped.append(filename)
            continue

        filepath = os.path.join(REPORTS_DIR, filename)
        text = extract_docx_text(filepath)

        if len(text) < 50:
            skipped.append(filename)
            continue

        metadata = extract_metadata_from_filename(filename)

        try:
            supabase.table("medical_reports").insert({
                "filename": filename,
                "patient_name": metadata["patient_name"],
                "doctor_name": metadata["doctor_name"],
                "pathology": metadata["pathology"],
                "report_date": metadata["report_date"],
                "file_size_bytes": os.path.getsize(filepath),
                "char_count": len(text),
                "content_text": text[:50000],
            }).execute()
            synced.append(filename)
        except Exception as e:
            print(f"Error syncing {filename}: {e}")
            skipped.append(filename)

    return jsonify({
        "synced": len(synced),
        "skipped": len(skipped),
        "total": len(docx_files),
        "synced_files": synced,
    })


# ══════════════════════════════════════════════════════════════
# DOSSIER ENDPOINTS
# ══════════════════════════════════════════════════════════════

def extract_patient_info_from_text(text: str) -> dict:
    """
    Extract personal info from a French clinical report text.
    Looks for patterns like:
      - "L'enfant BAGHDAD ISLEM âgé de 04 ans"
      - "Diagnostic principal : mucoviscidose"
      - "originaire et demeurant à Oran"
      - "Consanguinité de 2eme degré"
    """
    info = {}

    # ── Patient name + age ──
    # "L'enfant X Y, âgé(e) de N ans"
    name_age = re.search(
        r"(?:L[''']enfant|Le\s+nourrisson|Le\s+patient|La\s+patiente|L[''']adolescent)\s+"
        r"([A-ZÀ-Ÿa-zà-ÿ\s\-]+?)(?:,|\s+)\s*(?:âgée?|agée?|age)\s+(?:de\s+)?(\d+\s*(?:ans?|mois|jours?)(?:\s+et\s+(?:demi|\d+\s*mois))?)",
        text, re.IGNORECASE
    )
    if name_age:
        info["full_name"] = name_age.group(1).strip().title()
        info["age"] = name_age.group(2).strip()

    # ── Gender ──
    if re.search(r"\bfille\b|féminin|La\s+patiente|L[''']adolescente", text, re.IGNORECASE):
        info["gender"] = "F"
    elif re.search(r"\bgarçon\b|masculin|Le\s+patient|L[''']adolescent\b|Sexe\s+masculin", text, re.IGNORECASE):
        info["gender"] = "M"

    # ── Origin/Residence ──
    origin = re.search(
        r"originaire\s+(?:et\s+demeurant\s+)?(?:de|d[''']|à)\s+([A-ZÀ-Ÿa-zà-ÿ\s\-]+?)(?:[,.]|\s+(?:suivi|issue|adress))",
        text, re.IGNORECASE
    )
    if origin:
        city = origin.group(1).strip().title()
        info["origin"] = city
        info["residence"] = city

    residence_only = re.search(
        r"demeurant\s+à\s+([A-ZÀ-Ÿa-zà-ÿ\s\-]+?)(?:[,.]|\s+(?:suivi|issue))",
        text, re.IGNORECASE
    )
    if residence_only:
        info["residence"] = residence_only.group(1).strip().title()

    # ── Father / Mother ──
    father = re.search(r"Père\s*:\s*(\d+\s*ans?[^.\n]*)", text, re.IGNORECASE)
    if father:
        info["parent_father"] = father.group(1).strip()

    mother = re.search(r"Mère\s*:\s*(\d+\s*ans?[^.\n]*)", text, re.IGNORECASE)
    if mother:
        info["parent_mother"] = mother.group(1).strip()

    # ── Consanguinity ──
    consang = re.search(r"[Cc]onsanguinit[ée]\s+(?:du?\s+)?([^.\n]+)", text)
    if consang:
        info["consanguinity"] = consang.group(1).strip()

    # ── Siblings ──
    siblings = re.search(r"Fratrie\s*:\s*\n?((?:.*\n?){1,5})", text, re.IGNORECASE)
    if siblings:
        info["siblings_info"] = siblings.group(1).strip()[:300]

    # ── Diagnosis ──
    diag = re.search(
        r"[Dd]iagnostic\s+principal\s*[:：]\s*([^\n.]+)",
        text
    )
    if diag:
        info["principal_diagnosis"] = diag.group(1).strip()

    assoc_diag = re.search(
        r"[Dd]iagnostics?\s+associ[ée]s?\s*[:：]\s*([^\n]+)",
        text
    )
    if assoc_diag:
        val = assoc_diag.group(1).strip()
        if val.lower() != "aucun":
            info["associated_diagnoses"] = val

    # ── Date of diagnosis ──
    diag_date = re.search(
        r"[Dd]ate\s+d[ue]\s+diagnostic\s*[:：]\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})",
        text
    )
    if diag_date:
        try:
            d = diag_date.group(1).replace("/", "-").split("-")
            info["date_of_diagnosis"] = f"{d[2]}-{d[1].zfill(2)}-{d[0].zfill(2)}"
        except:
            pass

    # ── Age at diagnosis ──
    age_diag = re.search(
        r"[Aa]ge\s+(?:au|de)\s+diagnostic\s*[:：]\s*([^\n.]+)",
        text
    )
    if age_diag:
        info["age_at_diagnosis"] = age_diag.group(1).strip()

    # ── Treating doctor (from "Dr X" in text) ──
    doctor = re.search(r"\b(?:Dr|DR)\s+([A-ZÀ-Ÿ][a-zà-ÿ]+)", text)
    if doctor:
        info["treating_doctor"] = doctor.group(1).strip().title()

    # ── Current treatment ──
    treatment = re.search(
        r"[Tt]raitement\s+(?:en\s+cours|actuel)\s*[:：]\s*\n?((?:.*\n?){1,8}?)(?:\n\s*\n|Derni|Cure|Evolution|Suivi)",
        text
    )
    if treatment:
        info["current_treatment"] = treatment.group(1).strip()[:500]

    return info


# ── List Dossiers ────────────────────────────────────────────
@app.route("/api/dossiers", methods=["GET"])
def list_dossiers():
    """List all patient dossiers."""
    try:
        response = supabase.table("patient_dossiers") \
            .select("*") \
            .order("created_at", desc=True) \
            .execute()
        return jsonify({"dossiers": response.data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Search Dossiers ──────────────────────────────────────────
@app.route("/api/dossiers/search", methods=["GET"])
def search_dossiers():
    q = request.args.get("q", "").strip()
    if not q:
        return list_dossiers()
    try:
        response = supabase.table("patient_dossiers") \
            .select("*") \
            .or_(f"full_name.ilike.%{q}%,principal_diagnosis.ilike.%{q}%,treating_doctor.ilike.%{q}%,origin.ilike.%{q}%") \
            .order("created_at", desc=True) \
            .execute()
        return jsonify({"dossiers": response.data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Get Single Dossier + Reports ─────────────────────────────
@app.route("/api/dossiers/<dossier_id>", methods=["GET"])
def get_dossier(dossier_id):
    try:
        dossier = supabase.table("patient_dossiers") \
            .select("*") \
            .eq("id", dossier_id) \
            .single() \
            .execute()

        reports = supabase.table("medical_reports") \
            .select("id,filename,patient_name,report_date,pathology,file_size_bytes,char_count,created_at") \
            .eq("dossier_id", dossier_id) \
            .order("created_at", desc=True) \
            .execute()

        return jsonify({
            "dossier": dossier.data,
            "reports": reports.data,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Create Dossier (manual or from .docx) ────────────────────
@app.route("/api/dossiers", methods=["POST"])
def create_dossier():
    """Create a dossier. Can extract info from an uploaded .docx file."""
    extracted = {}

    # If a .docx file is uploaded, extract info from it
    if "file" in request.files:
        file = request.files["file"]
        if file.filename and file.filename.endswith(".docx"):
            # Save to reports dir
            filepath = os.path.join(REPORTS_DIR, file.filename)
            file.save(filepath)
            text = extract_docx_text(filepath)
            extracted = extract_patient_info_from_text(text)

            # Also get metadata from filename as fallback
            meta = extract_metadata_from_filename(file.filename)
            if not extracted.get("full_name") and meta.get("patient_name"):
                extracted["full_name"] = meta["patient_name"]
            if not extracted.get("treating_doctor") and meta.get("doctor_name"):
                extracted["treating_doctor"] = meta["doctor_name"]
            if not extracted.get("principal_diagnosis") and meta.get("pathology"):
                extracted["principal_diagnosis"] = meta["pathology"]

            extracted["_uploaded_file"] = file.filename
            extracted["_file_text"] = text[:50000]
            extracted["_file_size"] = os.path.getsize(filepath)

    # Merge with any manual form fields (form fields override extracted)
    form_data = request.form.to_dict() if request.form else {}
    for key, value in form_data.items():
        if value and value.strip() and key not in ("file",):
            extracted[key] = value.strip()

    if not extracted.get("full_name"):
        return jsonify({"error": "Le nom du patient est requis."}), 400

    # Prepare dossier data
    dossier_data = {
        "full_name": extracted.get("full_name", ""),
        "age": extracted.get("age"),
        "gender": extracted.get("gender", "Inconnu"),
        "origin": extracted.get("origin"),
        "residence": extracted.get("residence"),
        "parent_father": extracted.get("parent_father"),
        "parent_mother": extracted.get("parent_mother"),
        "consanguinity": extracted.get("consanguinity"),
        "siblings_info": extracted.get("siblings_info"),
        "principal_diagnosis": extracted.get("principal_diagnosis"),
        "associated_diagnoses": extracted.get("associated_diagnoses"),
        "age_at_diagnosis": extracted.get("age_at_diagnosis"),
        "treating_doctor": extracted.get("treating_doctor"),
        "current_treatment": extracted.get("current_treatment"),
        "notes": extracted.get("notes"),
    }

    # Handle date_of_diagnosis
    if extracted.get("date_of_diagnosis"):
        dossier_data["date_of_diagnosis"] = extracted["date_of_diagnosis"]

    # Handle date_of_birth
    if extracted.get("date_of_birth"):
        dossier_data["date_of_birth"] = extracted["date_of_birth"]

    try:
        result = supabase.table("patient_dossiers") \
            .insert(dossier_data) \
            .execute()

        dossier_id = result.data[0]["id"]

        # If a file was uploaded, also save it as a medical_report linked to this dossier
        if extracted.get("_uploaded_file"):
            try:
                meta = extract_metadata_from_filename(extracted["_uploaded_file"])
                supabase.table("medical_reports").insert({
                    "filename": extracted["_uploaded_file"],
                    "patient_name": extracted.get("full_name"),
                    "doctor_name": extracted.get("treating_doctor"),
                    "pathology": extracted.get("principal_diagnosis"),
                    "report_date": extracted.get("date_of_diagnosis"),
                    "file_size_bytes": extracted.get("_file_size"),
                    "char_count": len(extracted.get("_file_text", "")),
                    "content_text": extracted.get("_file_text", ""),
                    "dossier_id": dossier_id,
                }).execute()
            except Exception as e:
                print(f"Warning: Could not link report to dossier: {e}")

        return jsonify({
            "dossier": result.data[0],
            "extracted_fields": list(extracted.keys()),
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ── Update Dossier ───────────────────────────────────────────
@app.route("/api/dossiers/<dossier_id>", methods=["PUT"])
def update_dossier(dossier_id):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Filter allowed fields
    allowed = {
        "full_name", "date_of_birth", "age", "gender", "origin", "residence",
        "parent_father", "parent_mother", "consanguinity", "siblings_info",
        "principal_diagnosis", "associated_diagnoses", "date_of_diagnosis",
        "age_at_diagnosis", "treating_doctor", "current_treatment", "notes"
    }
    update_data = {k: v for k, v in data.items() if k in allowed}
    update_data["updated_at"] = datetime.utcnow().isoformat()

    try:
        result = supabase.table("patient_dossiers") \
            .update(update_data) \
            .eq("id", dossier_id) \
            .execute()
        return jsonify({"dossier": result.data[0] if result.data else {}})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Delete Dossier ───────────────────────────────────────────
@app.route("/api/dossiers/<dossier_id>", methods=["DELETE"])
def delete_dossier(dossier_id):
    try:
        # Unlink reports first
        supabase.table("medical_reports") \
            .update({"dossier_id": None}) \
            .eq("dossier_id", dossier_id) \
            .execute()

        supabase.table("patient_dossiers") \
            .delete() \
            .eq("id", dossier_id) \
            .execute()

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Extract Info Preview (from uploaded .docx) ───────────────
@app.route("/api/dossiers/extract-preview", methods=["POST"])
def extract_preview():
    """Upload a .docx and return extracted patient info without creating a dossier."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename or not file.filename.endswith(".docx"):
        return jsonify({"error": "Only .docx files are supported"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        text = extract_docx_text(tmp_path)
        extracted = extract_patient_info_from_text(text)

        # Fallback from filename
        meta = extract_metadata_from_filename(file.filename)
        if not extracted.get("full_name") and meta.get("patient_name"):
            extracted["full_name"] = meta["patient_name"]
        if not extracted.get("treating_doctor") and meta.get("doctor_name"):
            extracted["treating_doctor"] = meta["doctor_name"]

        return jsonify({
            "extracted": extracted,
            "text_preview": text[:2000],
            "filename": file.filename,
        })
    finally:
        os.unlink(tmp_path)


# ── Add Report to Dossier ────────────────────────────────────
@app.route("/api/dossiers/<dossier_id>/reports", methods=["POST"])
def add_report_to_dossier(dossier_id):
    """Upload a .docx report and link it to a dossier."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename or not file.filename.endswith(".docx"):
        return jsonify({"error": "Only .docx files are supported"}), 400

    filepath = os.path.join(REPORTS_DIR, file.filename)
    file.save(filepath)

    text = extract_docx_text(filepath)
    metadata = extract_metadata_from_filename(file.filename)

    try:
        result = supabase.table("medical_reports").insert({
            "filename": file.filename,
            "patient_name": metadata.get("patient_name"),
            "doctor_name": metadata.get("doctor_name"),
            "pathology": metadata.get("pathology"),
            "report_date": metadata.get("report_date"),
            "file_size_bytes": os.path.getsize(filepath),
            "char_count": len(text),
            "content_text": text[:50000],
            "dossier_id": dossier_id,
        }).execute()
        return jsonify({"report": result.data[0] if result.data else {}})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    print("=" * 60)
    print("  Clinical Pre-Analysis — API Server")
    print("  http://localhost:5000")
    print("=" * 60)
    # use_reloader=False prevents the watchdog from restarting
    # when heavy ML models are loaded (avoids connection resets)
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
