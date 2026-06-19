"use client";
import { useState, useEffect, useRef, useCallback } from "react";
import { supabase } from "@/lib/supabase";
import { extractPatientInfo, extractFromFilename } from "@/lib/extractPatientInfo";
import mammoth from "mammoth";
import styles from "./DossiersView.module.css";

const FIELD_LABELS = {
  full_name: "Nom complet",
  age: "Âge",
  gender: "Sexe",
  date_of_birth: "Date de naissance",
  origin: "Origine",
  residence: "Résidence",
  parent_father: "Père",
  parent_mother: "Mère",
  consanguinity: "Consanguinité",
  siblings_info: "Fratrie",
  principal_diagnosis: "Diagnostic principal",
  associated_diagnoses: "Diagnostics associés",
  date_of_diagnosis: "Date du diagnostic",
  age_at_diagnosis: "Âge au diagnostic",
  treating_doctor: "Médecin traitant",
  current_treatment: "Traitement en cours",
  notes: "Notes",
};

const INFO_ICONS = {
  age: "🎂", gender: "⚧", date_of_birth: "📅", origin: "📍", residence: "🏠",
  parent_father: "👨", parent_mother: "👩", consanguinity: "🧬", siblings_info: "👨‍👩‍👧‍👦",
  principal_diagnosis: "🩺", associated_diagnoses: "📋", date_of_diagnosis: "📆",
  age_at_diagnosis: "🔬", treating_doctor: "👨‍⚕️", current_treatment: "💊", notes: "📝",
};

export default function DossiersView() {
  const [dossiers, setDossiers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedDossier, setSelectedDossier] = useState(null);
  const [dossierReports, setDossierReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createMode, setCreateMode] = useState("file");
  const [extractedData, setExtractedData] = useState(null);
  const [formData, setFormData] = useState({});
  const [extracting, setExtracting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingDossier, setEditingDossier] = useState(null);
  const [toast, setToast] = useState(null);
  const [uploadedFileInfo, setUploadedFileInfo] = useState(null);
  const [activeFilter, setActiveFilter] = useState(null);
  const [stats, setStats] = useState({ total: 0, diagnoses: 0, cities: 0 });
  const [viewerReport, setViewerReport] = useState(null);
  const fileInputRef = useRef(null);
  const reportInputRef = useRef(null);
  const searchTimeoutRef = useRef(null);
  const pdfContentRef = useRef(null);

  const showToast = (message, type = "info") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  };

  const fetchDossiers = useCallback(async (query = "") => {
    setLoading(true);
    try {
      let result;
      if (query.trim()) {
        result = await supabase.from("patient_dossiers").select("*")
          .or(`full_name.ilike.%${query}%,principal_diagnosis.ilike.%${query}%,treating_doctor.ilike.%${query}%,origin.ilike.%${query}%`)
          .order("created_at", { ascending: false });
      } else {
        result = await supabase.from("patient_dossiers").select("*")
          .order("created_at", { ascending: false });
      }
      if (result.error) throw result.error;
      const data = result.data || [];
      setDossiers(data);
      setStats({
        total: data.length,
        diagnoses: new Set(data.filter(d => d.principal_diagnosis).map(d => d.principal_diagnosis)).size,
        cities: new Set(data.filter(d => d.origin).map(d => d.origin)).size,
      });
    } catch (err) {
      console.error(err);
      showToast("Erreur de chargement", "error");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchDossiers(); }, [fetchDossiers]);

  const handleSearch = (e) => {
    const q = e.target.value;
    setSearchQuery(q);
    clearTimeout(searchTimeoutRef.current);
    searchTimeoutRef.current = setTimeout(() => fetchDossiers(q), 300);
  };

  const readDocxText = async (file) => {
    const arrayBuffer = await file.arrayBuffer();
    const result = await mammoth.extractRawText({ arrayBuffer });
    return result.value;
  };

  const handleFileExtract = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setExtracting(true);
    try {
      const text = await readDocxText(file);
      const extracted = extractPatientInfo(text);
      const fromFilename = extractFromFilename(file.name);
      if (!extracted.full_name && fromFilename.full_name) extracted.full_name = fromFilename.full_name;
      if (!extracted.treating_doctor && fromFilename.treating_doctor) extracted.treating_doctor = fromFilename.treating_doctor;
      if (!extracted.principal_diagnosis && fromFilename.principal_diagnosis) extracted.principal_diagnosis = fromFilename.principal_diagnosis;
      setExtractedData({ extracted, filename: file.name });
      setUploadedFileInfo({ name: file.name, text, size: file.size });
      setFormData(extracted);
      showToast(`${Object.keys(extracted).length} champ(s) extrait(s)`, "success");
    } catch (err) {
      showToast("Erreur: " + err.message, "error");
    } finally {
      setExtracting(false);
    }
  };

  const handleCreate = async () => {
    if (!formData.full_name) return showToast("Nom requis", "error");
    setSaving(true);
    try {
      const dossierData = {};
      for (const key of Object.keys(FIELD_LABELS)) {
        if (formData[key]) dossierData[key] = formData[key];
      }
      if (!dossierData.gender) dossierData.gender = "Inconnu";
      const { data: dossier, error } = await supabase.from("patient_dossiers").insert(dossierData).select().single();
      if (error) throw error;
      if (uploadedFileInfo) {
        await supabase.from("medical_reports").insert({
          filename: uploadedFileInfo.name, patient_name: formData.full_name,
          doctor_name: formData.treating_doctor || null, pathology: formData.principal_diagnosis || null,
          file_size_bytes: uploadedFileInfo.size, char_count: uploadedFileInfo.text?.length || 0,
          content_text: (uploadedFileInfo.text || "").substring(0, 50000), dossier_id: dossier.id,
        });
      }
      showToast("Dossier créé ✓", "success");
      closeCreateModal();
      fetchDossiers();
    } catch (err) { showToast("Erreur: " + err.message, "error"); }
    finally { setSaving(false); }
  };

  const openDossier = async (dossier) => {
    setSelectedDossier(dossier);
    setSelectedReport(null);
    const { data } = await supabase.from("medical_reports")
      .select("*").eq("dossier_id", dossier.id).order("created_at", { ascending: false });
    setDossierReports(data || []);
  };

  const deleteDossier = async (id, e) => {
    e?.stopPropagation();
    if (!confirm("Supprimer ce dossier et dissocier ses rapports ?")) return;
    try {
      await supabase.from("medical_reports").update({ dossier_id: null }).eq("dossier_id", id);
      await supabase.from("patient_dossiers").delete().eq("id", id);
      showToast("Dossier supprimé", "success");
      if (selectedDossier?.id === id) setSelectedDossier(null);
      fetchDossiers();
    } catch { showToast("Erreur", "error"); }
  };

  const handleUpdate = async () => {
    if (!editingDossier) return;
    setSaving(true);
    try {
      const updateData = {};
      for (const key of Object.keys(FIELD_LABELS)) {
        if (formData[key] !== undefined) updateData[key] = formData[key];
      }
      updateData.updated_at = new Date().toISOString();
      const { error } = await supabase.from("patient_dossiers").update(updateData).eq("id", editingDossier.id);
      if (error) throw error;
      showToast("Mis à jour ✓", "success");
      setEditingDossier(null); setFormData({});
      fetchDossiers();
      if (selectedDossier?.id === editingDossier.id) setSelectedDossier({ ...selectedDossier, ...updateData });
    } catch (err) { showToast("Erreur: " + err.message, "error"); }
    finally { setSaving(false); }
  };

  const addReportToDossier = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !selectedDossier) return;
    try {
      const text = await readDocxText(file);
      const meta = extractFromFilename(file.name);
      await supabase.from("medical_reports").insert({
        filename: file.name, patient_name: meta.full_name || selectedDossier.full_name,
        doctor_name: meta.treating_doctor || selectedDossier.treating_doctor,
        pathology: meta.principal_diagnosis || selectedDossier.principal_diagnosis,
        file_size_bytes: file.size, char_count: text.length,
        content_text: text.substring(0, 50000), dossier_id: selectedDossier.id,
      });
      showToast("Rapport ajouté ✓", "success");
      const { data } = await supabase.from("medical_reports").select("*").eq("dossier_id", selectedDossier.id).order("created_at", { ascending: false });
      setDossierReports(data || []);
    } catch (err) { showToast("Erreur: " + err.message, "error"); }
    if (reportInputRef.current) reportInputRef.current.value = "";
  };

  const closeCreateModal = () => {
    setShowCreateModal(false); setEditingDossier(null);
    setFormData({}); setExtractedData(null); setUploadedFileInfo(null);
  };

  // ── Download as TXT ──
  const downloadTxt = (report) => {
    const blob = new Blob([report.content_text || ""], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = (report.filename || "rapport").replace(".docx", ".txt");
    a.click();
    URL.revokeObjectURL(url);
    showToast("Téléchargé en .txt", "success");
  };

  // ── Download / View as PDF ──
  const downloadPdf = async (report) => {
    const html2pdf = (await import("html2pdf.js")).default;
    const content = buildPdfHtml(report);
    const container = document.createElement("div");
    container.innerHTML = content;
    document.body.appendChild(container);

    await html2pdf().set({
      margin: [12, 12, 12, 12],
      filename: (report.filename || "rapport").replace(".docx", ".pdf"),
      image: { type: "jpeg", quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true },
      jsPDF: { unit: "mm", format: "a4", orientation: "portrait" },
    }).from(container).save();

    document.body.removeChild(container);
    showToast("PDF téléchargé", "success");
  };

  const openPdfViewer = (report) => {
    setViewerReport(report);
  };

  const buildPdfHtml = (report) => {
    const patientName = selectedDossier?.full_name || report.patient_name || "Patient";
    const date = formatDate(report.report_date || report.created_at);
    const doctor = selectedDossier?.treating_doctor || report.doctor_name || "";
    const diag = selectedDossier?.principal_diagnosis || report.pathology || "";
    const text = (report.content_text || "").replace(/\n/g, "<br/>");

    return `
      <div style="font-family: 'Segoe UI', Arial, sans-serif; color: #1a1a2e; max-width: 700px; padding: 32px;">
        <div style="border-bottom: 3px solid #0ea5e9; padding-bottom: 16px; margin-bottom: 24px;">
          <h1 style="font-size: 20px; color: #0ea5e9; margin: 0 0 4px;">Rapport Médical</h1>
          <p style="font-size: 12px; color: #64748b; margin: 0;">ClinicalPFE — Pré-analyse clinique</p>
        </div>
        <table style="width: 100%; font-size: 13px; margin-bottom: 20px; border-collapse: collapse;">
          <tr><td style="padding: 4px 8px; color: #64748b; width: 130px;">Patient</td><td style="padding: 4px 8px; font-weight: 600;">${patientName}</td></tr>
          ${doctor ? `<tr><td style="padding: 4px 8px; color: #64748b;">Médecin</td><td style="padding: 4px 8px;">Dr. ${doctor}</td></tr>` : ""}
          ${diag ? `<tr><td style="padding: 4px 8px; color: #64748b;">Diagnostic</td><td style="padding: 4px 8px;">${diag}</td></tr>` : ""}
          <tr><td style="padding: 4px 8px; color: #64748b;">Date</td><td style="padding: 4px 8px;">${date}</td></tr>
          <tr><td style="padding: 4px 8px; color: #64748b;">Fichier</td><td style="padding: 4px 8px;">${report.filename || "—"}</td></tr>
        </table>
        <div style="border-top: 1px solid #e2e8f0; padding-top: 16px; font-size: 13px; line-height: 1.8; color: #334155;">
          ${text}
        </div>
        <div style="margin-top: 32px; padding-top: 12px; border-top: 1px solid #e2e8f0; font-size: 10px; color: #94a3b8; text-align: center;">
          Généré par ClinicalPFE · ${new Date().toLocaleDateString("fr-FR")}
        </div>
      </div>
    `;
  };

  const printReport = (report) => {
    const content = buildPdfHtml(report);
    const win = window.open("", "_blank");
    win.document.write(`<!DOCTYPE html><html><head><title>${report.filename || "Rapport"}</title></head><body>${content}</body></html>`);
    win.document.close();
    win.focus();
    win.print();
  };

  const formatDate = (d) => {
    if (!d) return "—";
    try { return new Date(d).toLocaleDateString("fr-FR", { day: "numeric", month: "short", year: "numeric" }); } catch { return d; }
  };

  const genderIcon = (g) => g === "M" ? "👦" : g === "F" ? "👧" : "👤";
  const genderColor = (g) => g === "M" ? "#60a5fa" : g === "F" ? "#f472b6" : "#94a3b8";

  const diagnoses = [...new Set(dossiers.filter(d => d.principal_diagnosis).map(d => d.principal_diagnosis))];
  const filteredDossiers = activeFilter ? dossiers.filter(d => d.principal_diagnosis === activeFilter) : dossiers;

  return (
    <div className={styles.container}>
      {/* ═══ Stats Banner ═══ */}
      <div className={styles.statsRow}>
        <div className={styles.statCard}>
          <div className={styles.statValue}>{stats.total}</div>
          <div className={styles.statLabel}>Patients</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statValue}>{stats.diagnoses}</div>
          <div className={styles.statLabel}>Pathologies</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statValue}>{stats.cities}</div>
          <div className={styles.statLabel}>Villes</div>
        </div>
        <div className={styles.statCardAction}>
          <button className={styles.btnCreate} onClick={() => { setShowCreateModal(true); setFormData({}); setExtractedData(null); setUploadedFileInfo(null); }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            Nouveau dossier
          </button>
        </div>
      </div>

      {/* ═══ Search & Filters ═══ */}
      <div className={styles.controlsRow}>
        <div className={styles.searchWrap}>
          <svg className={styles.searchSvg} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input className={styles.searchInput} placeholder="Rechercher un patient..." value={searchQuery} onChange={handleSearch} />
        </div>
        {diagnoses.length > 0 && (
          <div className={styles.filterChips}>
            {activeFilter && (
              <button className={styles.chipClear} onClick={() => setActiveFilter(null)}>✕ Tout</button>
            )}
            {diagnoses.slice(0, 6).map((d) => (
              <button key={d} className={`${styles.chip} ${activeFilter === d ? styles.chipActive : ""}`}
                onClick={() => setActiveFilter(activeFilter === d ? null : d)}>
                {d.length > 28 ? d.substring(0, 28) + "…" : d}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* ═══ Dossiers Grid ═══ */}
      {loading ? (
        <div className={styles.loadingWrap}>
          <div className={styles.loadingSpinner}></div>
          <span>Chargement des dossiers...</span>
        </div>
      ) : filteredDossiers.length === 0 ? (
        <div className={styles.emptyWrap}>
          <div className={styles.emptyGraphic}>
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="var(--text-dim)" strokeWidth="1"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
          </div>
          <h3 className={styles.emptyTitle}>Aucun dossier</h3>
          <p className={styles.emptyText}>Commencez par créer un dossier patient depuis un rapport .docx</p>
        </div>
      ) : (
        <div className={styles.grid}>
          {filteredDossiers.map((d, i) => (
            <div key={d.id} className={styles.card} onClick={() => openDossier(d)} style={{ animationDelay: `${i * 0.03}s` }}>
              {/* Card accent line */}
              <div className={styles.cardAccent} style={{ background: `linear-gradient(90deg, ${genderColor(d.gender)}, transparent)` }}></div>

              <div className={styles.cardTop}>
                <div className={styles.avatar} style={{ borderColor: genderColor(d.gender) }}>
                  {genderIcon(d.gender)}
                </div>
                <div className={styles.cardInfo}>
                  <div className={styles.cardName}>{d.full_name}</div>
                  <div className={styles.cardSub}>{d.age || "Âge inconnu"}{d.origin ? ` · ${d.origin}` : ""}</div>
                </div>
              </div>

              {d.principal_diagnosis && (
                <div className={styles.diagPill}>{d.principal_diagnosis}</div>
              )}

              <div className={styles.cardMeta}>
                {d.treating_doctor && <span className={styles.metaTag}>👨‍⚕️ Dr. {d.treating_doctor}</span>}
                {d.consanguinity && <span className={styles.metaTag}>🧬 Consanguinité</span>}
                {d.age_at_diagnosis && <span className={styles.metaTag}>🔬 Diag. {d.age_at_diagnosis}</span>}
              </div>

              <div className={styles.cardFooter}>
                <span className={styles.cardDate}>{formatDate(d.created_at)}</span>
                <div className={styles.cardActions}>
                  <button className={styles.iconBtn} title="Modifier" onClick={(e) => { e.stopPropagation(); setEditingDossier(d); setFormData({...d}); }}>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                  </button>
                  <button className={`${styles.iconBtn} ${styles.iconBtnDanger}`} title="Supprimer" onClick={(e) => deleteDossier(d.id, e)}>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ═══ Dossier Detail (Full-Page Overlay) ═══ */}
      {selectedDossier && (
        <div className={styles.overlay} onClick={() => { setSelectedDossier(null); setDossierReports([]); setSelectedReport(null); }}>
          <div className={styles.detailPanel} onClick={(e) => e.stopPropagation()}>
            {/* Detail Header */}
            <div className={styles.detailHeader}>
              <div className={styles.detailHeaderBg} style={{ background: `linear-gradient(135deg, ${genderColor(selectedDossier.gender)}22 0%, transparent 60%)` }}></div>
              <button className={styles.detailClose} onClick={() => { setSelectedDossier(null); setDossierReports([]); setSelectedReport(null); }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>

              <div className={styles.detailProfile}>
                <div className={styles.avatarLg} style={{ borderColor: genderColor(selectedDossier.gender) }}>
                  {genderIcon(selectedDossier.gender)}
                </div>
                <div>
                  <h2 className={styles.detailName}>{selectedDossier.full_name}</h2>
                  <p className={styles.detailSub}>
                    {selectedDossier.age || "—"} · {selectedDossier.origin || "—"}
                    {selectedDossier.principal_diagnosis && (
                      <span className={styles.detailDiagBadge}>{selectedDossier.principal_diagnosis}</span>
                    )}
                  </p>
                </div>
              </div>
            </div>

            {/* Detail Body — Two Columns */}
            <div className={styles.detailBody}>
              {/* Left: Patient Info */}
              <div className={styles.detailLeft}>
                <h3 className={styles.sectionLabel}>Informations personnelles</h3>
                <div className={styles.infoCards}>
                  {Object.entries(FIELD_LABELS).map(([key, label]) => {
                    const value = selectedDossier[key];
                    if (!value || key === "full_name") return null;
                    return (
                      <div key={key} className={styles.infoCard}>
                        <span className={styles.infoIcon}>{INFO_ICONS[key] || "📋"}</span>
                        <div>
                          <div className={styles.infoCardLabel}>{label}</div>
                          <div className={styles.infoCardValue}>{key.includes("date") ? formatDate(value) : value}</div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Right: Reports */}
              <div className={styles.detailRight}>
                <div className={styles.reportsSectionHead}>
                  <h3 className={styles.sectionLabel}>Rapports médicaux ({dossierReports.length})</h3>
                  <button className={styles.btnAddReport} onClick={() => reportInputRef.current?.click()}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                    Ajouter
                  </button>
                  <input type="file" ref={reportInputRef} accept=".docx" onChange={addReportToDossier} style={{ display: "none" }} />
                </div>

                {dossierReports.length > 0 ? (
                  <div className={styles.reportCards}>
                    {dossierReports.map((r) => (
                      <div key={r.id} className={styles.reportCardWrap}>
                        <div className={`${styles.reportCard} ${selectedReport?.id === r.id ? styles.reportCardActive : ""}`}
                          onClick={() => setSelectedReport(selectedReport?.id === r.id ? null : r)}>
                          <div className={styles.reportCardIcon}>📄</div>
                          <div className={styles.reportCardInfo}>
                            <div className={styles.reportCardTitle}>{r.filename?.replace(".docx", "") || "Rapport"}</div>
                            <div className={styles.reportCardMeta}>
                              {formatDate(r.report_date || r.created_at)}
                              {r.char_count ? ` · ${(r.char_count / 1000).toFixed(1)}k car.` : ""}
                            </div>
                          </div>
                          <svg className={styles.reportChevron} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="6 9 12 15 18 9"/></svg>
                        </div>
                        {/* Action buttons */}
                        <div className={styles.reportActions}>
                          <button className={styles.reportActionBtn} title="Lire" onClick={(e) => { e.stopPropagation(); openPdfViewer(r); }}>
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                            Lire
                          </button>
                          <button className={styles.reportActionBtn} title="PDF" onClick={(e) => { e.stopPropagation(); downloadPdf(r); }}>
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                            PDF
                          </button>
                          <button className={styles.reportActionBtn} title="TXT" onClick={(e) => { e.stopPropagation(); downloadTxt(r); }}>
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                            TXT
                          </button>
                          <button className={styles.reportActionBtn} title="Imprimer" onClick={(e) => { e.stopPropagation(); printReport(r); }}>
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
                            Imprimer
                          </button>
                        </div>
                        {/* Expanded content */}
                        {selectedReport?.id === r.id && (
                          <div className={styles.reportContent}>
                            <div className={styles.reportContentHeader}>
                              <span>📋 Contenu du rapport</span>
                              <button className={styles.reportContentClose} onClick={() => setSelectedReport(null)}>✕</button>
                            </div>
                            <pre className={styles.reportText}>{r.content_text || "Aucun contenu disponible"}</pre>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className={styles.noReports}>
                    <p>Aucun rapport lié</p>
                    <button className={styles.btnAddReport} onClick={() => reportInputRef.current?.click()}>Ajouter un .docx</button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ═══ Create / Edit Modal ═══ */}
      {(showCreateModal || editingDossier) && (
        <div className={styles.overlay} onClick={closeCreateModal}>
          <div className={styles.formPanel} onClick={(e) => e.stopPropagation()}>
            <div className={styles.formPanelHeader}>
              <h2 className={styles.formPanelTitle}>
                {editingDossier ? "Modifier le dossier" : "Nouveau dossier"}
              </h2>
              <button className={styles.detailClose} onClick={closeCreateModal}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>

            {!editingDossier && (
              <div className={styles.modeSwitch}>
                <button className={`${styles.modeSwitchBtn} ${createMode === "file" ? styles.modeSwitchActive : ""}`} onClick={() => setCreateMode("file")}>
                  📄 Depuis .docx
                </button>
                <button className={`${styles.modeSwitchBtn} ${createMode === "manual" ? styles.modeSwitchActive : ""}`} onClick={() => setCreateMode("manual")}>
                  ✏️ Manuel
                </button>
              </div>
            )}

            {!editingDossier && createMode === "file" && !extractedData && (
              <div className={styles.dropZone} onClick={() => fileInputRef.current?.click()}>
                <input type="file" ref={fileInputRef} accept=".docx" onChange={handleFileExtract} style={{ display: "none" }} />
                {extracting ? (
                  <><div className={styles.loadingSpinner}></div><p style={{ marginTop: 12 }}>Extraction en cours...</p></>
                ) : (
                  <>
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--accent-cyan)" strokeWidth="1.5" style={{ opacity: 0.6 }}>
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="12" y2="12"/><line x1="15" y1="15" x2="12" y2="12"/>
                    </svg>
                    <p className={styles.dropTitle}>Déposez un rapport .docx</p>
                    <p className={styles.dropSub}>Extraction automatique des données patient</p>
                  </>
                )}
              </div>
            )}

            {extractedData && (
              <div className={styles.extractSuccess}>
                ✅ {Object.keys(extractedData.extracted).length} champs extraits de «{extractedData.filename}»
              </div>
            )}

            {(createMode === "manual" || extractedData || editingDossier) && (
              <>
                <div className={styles.formGrid}>
                  {Object.entries(FIELD_LABELS).map(([key, label]) => (
                    <div key={key} className={["current_treatment", "notes", "siblings_info", "associated_diagnoses"].includes(key) ? styles.formColFull : styles.formCol}>
                      <label className={styles.formLabel}>
                        <span>{INFO_ICONS[key]}</span> {label}
                      </label>
                      {key === "gender" ? (
                        <select className={styles.formInput} value={formData[key] || "Inconnu"} onChange={(e) => setFormData({ ...formData, [key]: e.target.value })}>
                          <option value="M">Masculin</option><option value="F">Féminin</option><option value="Inconnu">Inconnu</option>
                        </select>
                      ) : ["current_treatment", "notes", "siblings_info"].includes(key) ? (
                        <textarea className={`${styles.formInput} ${styles.formTextarea}`} value={formData[key] || ""} onChange={(e) => setFormData({ ...formData, [key]: e.target.value })} rows={2} />
                      ) : (
                        <input className={styles.formInput} type={key.includes("date") ? "date" : "text"} value={formData[key] || ""} onChange={(e) => setFormData({ ...formData, [key]: e.target.value })} />
                      )}
                    </div>
                  ))}
                </div>
                <div className={styles.formFooter}>
                  <button className={styles.btnCancel} onClick={closeCreateModal}>Annuler</button>
                  <button className={styles.btnSubmit} onClick={editingDossier ? handleUpdate : handleCreate} disabled={saving || !formData.full_name}>
                    {saving ? "Enregistrement..." : editingDossier ? "Sauvegarder" : "Créer le dossier"}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* ═══ PDF Viewer Modal ═══ */}
      {viewerReport && (
        <div className={styles.overlay} onClick={() => setViewerReport(null)}>
          <div className={styles.viewerPanel} onClick={(e) => e.stopPropagation()}>
            <div className={styles.viewerHeader}>
              <h3 className={styles.viewerTitle}>📋 {viewerReport.filename?.replace(".docx", "") || "Rapport"}</h3>
              <div className={styles.viewerActions}>
                <button className={styles.viewerBtn} onClick={() => downloadPdf(viewerReport)}>⬇️ PDF</button>
                <button className={styles.viewerBtn} onClick={() => downloadTxt(viewerReport)}>⬇️ TXT</button>
                <button className={styles.viewerBtn} onClick={() => printReport(viewerReport)}>🖨️ Imprimer</button>
                <button className={styles.viewerClose} onClick={() => setViewerReport(null)}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
              </div>
            </div>
            <div className={styles.viewerMeta}>
              <span>👤 {selectedDossier?.full_name || viewerReport.patient_name}</span>
              {(selectedDossier?.treating_doctor || viewerReport.doctor_name) && <span>👨‍⚕️ Dr. {selectedDossier?.treating_doctor || viewerReport.doctor_name}</span>}
              <span>📅 {formatDate(viewerReport.report_date || viewerReport.created_at)}</span>
              {viewerReport.char_count && <span>📝 {(viewerReport.char_count / 1000).toFixed(1)}k caractères</span>}
            </div>
            <div className={styles.viewerContent} ref={pdfContentRef}>
              <pre className={styles.viewerText}>{viewerReport.content_text || "Aucun contenu disponible"}</pre>
            </div>
          </div>
        </div>
      )}

      {/* Toast */}
      {toast && (
        <div className={`${styles.toast} ${styles[`toast${toast.type.charAt(0).toUpperCase() + toast.type.slice(1)}`]}`}>
          {toast.message}
        </div>
      )}
    </div>
  );
}
