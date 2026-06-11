"""
Clinical Pre-Analysis Module — Professional Interface
Streamlit application for clinicians to upload patient reports (.docx)
and receive structured phenotype analysis with rare disease matching.
"""

import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

import sys
import json
import time
import tempfile

import streamlit as st
from docx import Document

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ── Page Config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Module de Pre-Analyse Clinique",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Premium CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: #0a0e17; }
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}

    .top-bar {
        background: linear-gradient(135deg, #0f1923 0%, #162033 100%);
        border-bottom: 1px solid rgba(56, 189, 248, 0.15);
        padding: 1.2rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .top-bar h1 {
        color: #f0f4f8; font-size: 1.35rem; font-weight: 600; margin: 0; letter-spacing: -0.02em;
    }
    .top-bar .subtitle { color: #64748b; font-size: 0.8rem; font-weight: 400; margin-top: 2px; }
    .top-bar .badge {
        background: rgba(56, 189, 248, 0.12); color: #38bdf8;
        padding: 4px 12px; border-radius: 20px; font-size: 0.7rem;
        font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase;
    }

    .card {
        background: linear-gradient(145deg, #111827 0%, #0f172a 100%);
        border: 1px solid rgba(148, 163, 184, 0.08);
        border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;
    }
    .card-header {
        color: #94a3b8; font-size: 0.7rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.8rem;
    }

    .stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 1.5rem 0; }
    .stat-box {
        background: linear-gradient(145deg, #111827 0%, #0f172a 100%);
        border: 1px solid rgba(148, 163, 184, 0.08);
        border-radius: 12px; padding: 1.2rem; text-align: center;
    }
    .stat-value { color: #f0f4f8; font-size: 1.8rem; font-weight: 700; line-height: 1; }
    .stat-value.accent { color: #38bdf8; }
    .stat-value.green { color: #34d399; }
    .stat-value.amber { color: #fbbf24; }
    .stat-value.red { color: #f87171; }
    .stat-label {
        color: #64748b; font-size: 0.7rem; font-weight: 500;
        text-transform: uppercase; letter-spacing: 0.06em; margin-top: 0.5rem;
    }

    .entity-table { width: 100%; border-collapse: separate; border-spacing: 0; margin: 0.5rem 0; }
    .entity-table th {
        background: rgba(30, 41, 59, 0.8); color: #94a3b8; font-size: 0.65rem;
        font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em;
        padding: 0.7rem 1rem; text-align: left;
        border-bottom: 1px solid rgba(148, 163, 184, 0.1);
    }
    .entity-table th:first-child { border-radius: 8px 0 0 0; }
    .entity-table th:last-child { border-radius: 0 8px 0 0; }
    .entity-table td {
        color: #cbd5e1; font-size: 0.8rem; padding: 0.6rem 1rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.05);
    }
    .entity-table tr:hover td { background: rgba(56, 189, 248, 0.04); }

    .tag {
        display: inline-block; padding: 2px 8px; border-radius: 4px;
        font-size: 0.65rem; font-weight: 600; letter-spacing: 0.03em;
    }
    .tag-problem { background: rgba(239, 68, 68, 0.15); color: #fca5a5; }
    .tag-treatment { background: rgba(59, 130, 246, 0.15); color: #93c5fd; }
    .tag-test { background: rgba(168, 85, 247, 0.15); color: #c4b5fd; }
    .tag-negated { background: rgba(251, 191, 36, 0.15); color: #fcd34d; }
    .tag-matched { background: rgba(52, 211, 153, 0.12); color: #6ee7b7; }
    .tag-unmatched { background: rgba(100, 116, 139, 0.15); color: #94a3b8; }

    .ordo-card {
        background: linear-gradient(135deg, #0c4a6e 0%, #164e63 50%, #134e4a 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 12px; padding: 1.5rem; margin: 1rem 0;
    }
    .ordo-name { color: #f0f4f8; font-size: 1.2rem; font-weight: 600; }
    .ordo-score { color: #38bdf8; font-size: 0.85rem; font-weight: 500; margin-top: 0.3rem; }
    .ordo-orpha { color: #94a3b8; font-size: 0.75rem; margin-top: 0.2rem; }

    .pipeline-step { display: flex; align-items: center; gap: 0.8rem; padding: 0.6rem 0; }
    .step-num {
        width: 28px; height: 28px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.7rem; font-weight: 600;
    }
    .step-done { background: #34d399; color: #0a0e17; }
    .step-pending { background: rgba(148, 163, 184, 0.15); color: #64748b; }
    .step-text { color: #e2e8f0; font-size: 0.8rem; font-weight: 500; }
    .step-text.dim { color: #475569; }

    .section-divider { border: none; border-top: 1px solid rgba(148, 163, 184, 0.08); margin: 1.5rem 0; }

    .stFileUploader > div { border: none !important; }
    .stFileUploader label { display: none !important; }
    div[data-testid="stFileUploader"] { background: transparent; }
    div[data-testid="stFileUploader"] section {
        background: linear-gradient(145deg, #111827 0%, #0f172a 100%);
        border: 2px dashed rgba(56, 189, 248, 0.2);
        border-radius: 12px; padding: 2rem;
    }
    div[data-testid="stFileUploader"] section:hover { border-color: rgba(56, 189, 248, 0.5); }
    .stButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: white; border: none; border-radius: 8px;
        padding: 0.6rem 2rem; font-weight: 600; font-size: 0.85rem;
        letter-spacing: 0.02em; transition: all 0.2s ease; width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
        box-shadow: 0 4px 20px rgba(3, 105, 161, 0.3);
    }

    .json-block {
        background: #0d1117; border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 8px; padding: 1rem;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.75rem; color: #c9d1d9;
        overflow-x: auto; max-height: 400px; overflow-y: auto;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0; background: rgba(15, 23, 42, 0.6);
        border-radius: 8px; padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #64748b; font-size: 0.8rem; font-weight: 500;
        border-radius: 6px; padding: 0.5rem 1.2rem;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(56, 189, 248, 0.12) !important;
        color: #38bdf8 !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-bar">
    <div>
        <h1>Module de Pre-Analyse Clinique</h1>
        <div class="subtitle">Extraction et normalisation de phenotypes &mdash; Maladies rares</div>
    </div>
    <div class="badge">Pipeline v3 &mdash; Bilingue FR/EN</div>
</div>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def load_pipeline():
    from pipeline import FullPipeline
    return FullPipeline()


def extract_docx_text(uploaded_file) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    try:
        doc = Document(tmp_path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    finally:
        os.unlink(tmp_path)


def build_entity_rows(entities: list, category: str) -> str:
    tag_class = f"tag-{category}"
    rows = ""
    for e in entities:
        matched_tag = '<span class="tag tag-matched">HPO</span>' if e.get("matched") else '<span class="tag tag-unmatched">--</span>'
        neg_tag = ' <span class="tag tag-negated">NEG</span>' if e.get("negated") else ""
        hpo = e.get("hpo_id") or ""
        hpo_name = e.get("hpo_name") or ""
        conf = f'{e.get("confidence", 0):.0%}' if e.get("matched") else ""
        rows += f"""<tr>
            <td>{e['text'][:55]}</td>
            <td><span class="tag {tag_class}">{category.upper()}</span>{neg_tag}</td>
            <td>{matched_tag}</td>
            <td style="font-family: monospace; font-size: 0.75rem;">{hpo}</td>
            <td>{hpo_name}</td>
            <td>{conf}</td>
        </tr>"""
    return rows


# ── Main ─────────────────────────────────────────────────────────────────
col_upload, col_info = st.columns([2, 1])

with col_upload:
    input_mode = st.radio("Mode d'entrée", ["Fichier (.docx / .txt)", "Texte libre"], horizontal=True, label_visibility="collapsed")
    uploaded = None
    pasted_text = None
    if input_mode == "Fichier (.docx / .txt)":
        uploaded = st.file_uploader(
            "Upload", type=["docx", "txt"],
            accept_multiple_files=False, label_visibility="collapsed",
        )
    else:
        pasted_text = st.text_area(
            "Collez une note clinique (FR ou EN)",
            height=200,
            placeholder="Le patient présente une hypotonie axiale...\nPatient is a 55yo male with...",
        )

with col_info:
    st.markdown("""
    <div class="card" style="margin-top: 0;">
        <div class="card-header">Architecture du pipeline</div>
        <div class="pipeline-step"><div class="step-num step-pending">1</div><div class="step-text dim">De-identification (PHI)</div></div>
        <div class="pipeline-step"><div class="step-num step-pending">2</div><div class="step-text dim">Extraction NER (DeBERTa-v3 / GLiNER)</div></div>
        <div class="pipeline-step"><div class="step-num step-pending">3</div><div class="step-text dim">Validation (NegEx / Temporel / Numerique)</div></div>
        <div class="pipeline-step"><div class="step-num step-pending">4</div><div class="step-text dim">Normalisation HPO / UMLS / ORDO</div></div>
    </div>
    """, unsafe_allow_html=True)


# Determine input text
raw_text = None
source_name = "Texte colle"

if uploaded:
    if uploaded.name.endswith(".txt"):
        raw_text = uploaded.getvalue().decode("utf-8", errors="replace")
    else:
        raw_text = extract_docx_text(uploaded)
    source_name = uploaded.name
elif pasted_text and len(pasted_text.strip()) > 10:
    raw_text = pasted_text.strip()

if raw_text:
    if len(raw_text) < 50:
        st.error("Le texte ne contient pas assez de contenu exploitable.")
        st.stop()

    # Auto-detect language
    from module1_preprocessing.language_detector import detect_language
    detected_lang = detect_language(raw_text)
    lang_display = "Français" if detected_lang == "fr" else "English"

    st.markdown(f"""
    <div class="card">
        <div class="card-header">Rapport chargé</div>
        <div style="color: #e2e8f0; font-size: 0.9rem; font-weight: 500;">{source_name}</div>
        <div style="color: #64748b; font-size: 0.8rem; margin-top: 4px;">{len(raw_text):,} caractères &nbsp;|&nbsp; Langue détectée : {lang_display}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Lancer l'analyse", use_container_width=True):

        with st.spinner("Chargement des modeles NLP..."):
            pipeline_obj = load_pipeline()

        progress = st.progress(0, text="Module 1 : De-identification...")
        start = time.time()
        output_dir = os.path.join(PROJECT_ROOT, "output", "streamlit")
        os.makedirs(output_dir, exist_ok=True)

        progress.progress(15, text="[Module 2] Extraction NER (DeBERTa-v3 — Helios9/BioMed_NER + d4data ensemble)s...")

        try:
            result = pipeline_obj.process_and_save(
                clinical_text=raw_text,
                note_id="UPLOADED",
                output_dir=output_dir,
            )
        except Exception as e:
            st.error(f"Erreur lors de l'analyse : {str(e)}")
            st.stop()

        progress.progress(85, text="Module 4 : Normalisation HPO / ORDO...")
        elapsed = round(time.time() - start, 2)
        progress.progress(100, text=f"Analyse terminee en {elapsed}s")
        time.sleep(0.5)
        progress.empty()

        # ── Results ──────────────────────────────────────────────
        m4 = result.get("module4", {})
        stats = m4.get("stats", {})
        normalized = result.get("module4", {})
        ordo = m4.get("ordo_candidates", [])
        numerics = result.get("module3", {}).get("numeric_phenotypes", [])
        m2_ents = result.get("module2", {}).get("entities", {})

        total_ents = stats.get("total", 0)
        matched = stats.get("matched", 0)
        negated_count = sum(
            1 for cat in ["problem", "treatment", "test"]
            for e in m2_ents.get(cat, []) if e.get("negated", False)
        )

        st.markdown(f"""
        <div class="stat-grid">
            <div class="stat-box"><div class="stat-value accent">{total_ents}</div><div class="stat-label">Entites extraites</div></div>
            <div class="stat-box"><div class="stat-value green">{matched}</div><div class="stat-label">Codes HPO attribues</div></div>
            <div class="stat-box"><div class="stat-value amber">{len(numerics)}</div><div class="stat-label">Phenotypes numeriques</div></div>
            <div class="stat-box"><div class="stat-value red">{negated_count}</div><div class="stat-label">Entites niees (NegEx)</div></div>
        </div>
        """, unsafe_allow_html=True)

        # ORDO
        if ordo:
            top = ordo[0]
            ordo_display = top.get("name_fr") or top["name"]
            st.markdown(f"""
            <div class="ordo-card">
                <div class="card-header" style="color: rgba(56, 189, 248, 0.7);">Maladie rare candidate (ORDO)</div>
                <div class="ordo-name">{ordo_display}</div>
                <div class="ordo-score">Score de correspondance : {top['score']:.1%}</div>
                <div class="ordo-orpha">{top.get('matched_hpo', 0)}/{top.get('total_hpo', 0)} phenotypes concordants</div>
            </div>
            """, unsafe_allow_html=True)

            if len(ordo) > 1:
                others = "".join(
                    f'<div style="color:#94a3b8;font-size:0.8rem;padding:0.3rem 0;">{(c.get("name_fr") or c["name"])} &mdash; {c["score"]:.1%}</div>'
                    for c in ordo[1:4]
                )
                st.markdown(f'<div class="card"><div class="card-header">Autres candidats</div>{others}</div>', unsafe_allow_html=True)

        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Entites cliniques", "Valeurs biologiques", "Phenopacket (JSON)", "Texte source"])

        with tab1:
            all_rows = ""
            for cat in ["problem", "treatment", "test"]:
                all_rows += build_entity_rows(normalized.get(cat, []), cat)
            if all_rows:
                st.markdown(f"""
                <table class="entity-table">
                    <thead><tr><th>Entite</th><th>Type</th><th>Statut</th><th>Code HPO</th><th>Terme HPO</th><th>Confiance</th></tr></thead>
                    <tbody>{all_rows}</tbody>
                </table>
                """, unsafe_allow_html=True)

        with tab2:
            if numerics:
                nr = "".join(f'<tr><td>{n.get("phenotype","")}</td><td style="font-family:monospace;">{n.get("hpo_id","")}</td><td>{n.get("raw_value","")}</td><td>{n.get("interpretation","")}</td></tr>' for n in numerics)
                st.markdown(f'<table class="entity-table"><thead><tr><th>Phenotype</th><th>Code HPO</th><th>Valeur brute</th><th>Interpretation</th></tr></thead><tbody>{nr}</tbody></table>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#64748b;padding:2rem;text-align:center;">Aucune valeur biologique anormale detectee</div>', unsafe_allow_html=True)

        with tab3:
            pp = result.get("phenopacket", {})
            if pp:
                js = json.dumps(pp, indent=2, ensure_ascii=False)
                st.markdown(f'<pre class="json-block">{js}</pre>', unsafe_allow_html=True)
                fname = uploaded.name.replace('.docx', '').replace('.txt', '') if uploaded else "clinical_note"
                st.download_button("Telecharger le Phenopacket", data=js, file_name=f"phenopacket_{fname}.json", mime="application/json")

        with tab4:
            st.markdown(f"""
            <div class="card">
                <div class="card-header">Texte clinique extrait ({len(raw_text):,} caracteres)</div>
                <div style="color:#cbd5e1;font-size:0.8rem;line-height:1.6;max-height:500px;overflow-y:auto;white-space:pre-wrap;">{raw_text[:5000]}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <hr class="section-divider">
        <div style="display:flex;justify-content:space-between;color:#475569;font-size:0.7rem;padding:0 0.5rem;">
            <span>Temps : {elapsed}s</span>
            <span>DeBERTa-v3 + GLiNER + SapBERT + NegEx | Bilingue FR/EN</span>
            <span>GA4GH Phenopackets (ISO 4454:2022)</span>
        </div>
        """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;">
        <div style="margin-bottom:1.5rem;">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#1e3a5f" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10 9 9 9 8 9"/>
            </svg>
        </div>
        <div style="color:#e2e8f0;font-size:1.1rem;font-weight:500;margin-bottom:0.5rem;">
            Deposez un rapport clinique (.docx)
        </div>
        <div style="color:#475569;font-size:0.85rem;max-width:450px;margin:0 auto;line-height:1.6;">
            Le systeme extraira automatiquement les entites cliniques, identifiera les phenotypes
            et proposera un diagnostic de maladie rare via la base ORDO.
        </div>
    </div>
    """, unsafe_allow_html=True)
