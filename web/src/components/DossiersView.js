"use client";
import { useState, useEffect, useRef, useCallback } from "react";
import { supabase } from "@/lib/supabase";
import { extractPatientInfo, extractFromFilename } from "@/lib/extractPatientInfo";
import mammoth from "mammoth";
import styles from "./DossiersView.module.css";
import {
  CakeIcon,
  IdentificationIcon,
  CalendarDaysIcon,
  MapPinIcon,
  HomeIcon,
  UserIcon,
  DnaIcon,
  UserGroupIcon,
  HeartIcon,
  ClipboardDocumentListIcon,
  MicroscopeIcon,
  ShieldCheckIcon,
  DocumentMagnifyingGlassIcon,
  PencilSquareIcon,
  TrashIcon,
  XMarkIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  DocumentTextIcon,
  DocumentArrowUpIcon,
  PencilIcon,
  CheckCircleIcon,
  EyeIcon,
  ArrowDownTrayIcon,
  PrinterIcon,
  ChevronDownIcon,
  FolderIcon,
} from "@/components/Icons";

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

// Map each field key to an icon component
const INFO_ICON_COMPONENTS = {
  age: CakeIcon,
  gender: IdentificationIcon,
  date_of_birth: CalendarDaysIcon,
  origin: MapPinIcon,
  residence: HomeIcon,
  parent_father: UserIcon,
  parent_mother: UserIcon,
  consanguinity: DnaIcon,
  siblings_info: UserGroupIcon,
  principal_diagnosis: HeartIcon,
  associated_diagnoses: ClipboardDocumentListIcon,
  date_of_diagnosis: CalendarDaysIcon,
  age_at_diagnosis: MicroscopeIcon,
  treating_doctor: HeartIcon,
  current_treatment: ShieldCheckIcon,
  notes: DocumentMagnifyingGlassIcon,
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
  const [filters, setFilters] = useState({ diagnosis: "", origin: "", gender: "", doctor: "" });
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

  const readDocxContent = async (file) => {
    const arrayBuffer = await file.arrayBuffer();
    const [textResult, htmlResult] = await Promise.all([
      mammoth.extractRawText({ arrayBuffer }),
      mammoth.convertToHtml({ arrayBuffer }),
    ]);
    return { text: textResult.value, html: htmlResult.value };
  };

  const handleFileExtract = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setExtracting(true);
    try {
      const { text, html } = await readDocxContent(file);
      const extracted = extractPatientInfo(text);
      const fromFilename = extractFromFilename(file.name);
      if (!extracted.full_name && fromFilename.full_name) extracted.full_name = fromFilename.full_name;
      if (!extracted.treating_doctor && fromFilename.treating_doctor) extracted.treating_doctor = fromFilename.treating_doctor;
      if (!extracted.principal_diagnosis && fromFilename.principal_diagnosis) extracted.principal_diagnosis = fromFilename.principal_diagnosis;
      setExtractedData({ extracted, filename: file.name });
      setUploadedFileInfo({ name: file.name, text, html, size: file.size });
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
          content_text: (uploadedFileInfo.html || uploadedFileInfo.text || "").substring(0, 50000), dossier_id: dossier.id,
        });
      }
      showToast("Dossier créé avec succès", "success");
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
      showToast("Mis à jour avec succès", "success");
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
      const { text, html } = await readDocxContent(file);
      const meta = extractFromFilename(file.name);
      await supabase.from("medical_reports").insert({
        filename: file.name, patient_name: meta.full_name || selectedDossier.full_name,
        doctor_name: meta.treating_doctor || selectedDossier.treating_doctor,
        pathology: meta.principal_diagnosis || selectedDossier.principal_diagnosis,
        file_size_bytes: file.size, char_count: text.length,
        content_text: (html || text).substring(0, 50000), dossier_id: selectedDossier.id,
      });
      showToast("Rapport ajouté avec succès", "success");
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

  // ── Download original DOCX ──
  const downloadDocx = (report) => {
    if (!report.filename) return showToast("Nom de fichier manquant", "error");
    const apiBase = typeof window !== "undefined" && window.location.hostname.includes("devtunnels.ms")
      ? "https://gj2k374z-5000.uks1.devtunnels.ms"
      : "http://localhost:5000";
    const url = `${apiBase}/api/reports/download/${encodeURIComponent(report.filename)}`;
    const a = document.createElement("a");
    a.href = url;
    a.download = report.filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    showToast("Téléchargement du .docx", "success");
  };

  // ── Download / View as PDF ──
  const downloadPdf = (report) => {
    const content = buildPdfHtml(report);
    const pdfFilename = (report.filename || "rapport").replace(".docx", "");
    const win = window.open("", "_blank");
    if (!win) return showToast("Pop-up bloquée par le navigateur", "error");
    win.document.write(`<!DOCTYPE html><html><head>
      <title>${pdfFilename}</title>
      <style>
        body { font-family: 'Segoe UI', system-ui, sans-serif; color: #1e293b; margin: 20px; }
        @media print { @page { margin: 10mm; } body { margin: 0; } }
        table { width:100%; border-collapse:collapse; margin:8px 0; font-size:12px; }
        th, td { border:1px solid #d1d5db; padding:6px 10px; text-align:left; vertical-align:top; }
        th { background:#f1f5f9; font-weight:600; color:#1e293b; }
        tr:nth-child(even) td { background:#f8fafc; }
        h1,h2,h3,h4 { color:#0f172a; margin:14px 0 6px; }
        h1 { font-size:16px; border-bottom:2px solid #0ea5e9; padding-bottom:6px; }
        h2 { font-size:14px; } h3 { font-size:13px; } h4 { font-size:12px; }
        strong, b { color:#1e293b; }
        ul, ol { padding-left:20px; margin:6px 0; }
        p { margin:4px 0; line-height:1.8; }
      </style>
    </head><body>${content}</body></html>`);
    win.document.close();
    showToast("Utilisez Ctrl+P pour enregistrer en PDF", "success");
  };



  const openPdfViewer = (report) => {
    setViewerReport(report);
  };

  const buildPdfHtml = (report) => {
    const d = selectedDossier || {};
    const patientName = d.full_name || report.patient_name || "Patient";
    const date = formatDate(report.report_date || report.created_at);
    const doctor = d.treating_doctor || report.doctor_name || "";
    const diag = d.principal_diagnosis || report.pathology || "";
    const rawContent = report.content_text || "";
    const isHtml = rawContent.trim().startsWith("<");
    const reportContent = isHtml
      ? rawContent  // Already HTML from mammoth
      : rawContent.replace(/\n/g, "<br/>");  // Legacy plain text
    const now = new Date();
    const generatedDate = now.toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
    const generatedTime = now.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });

    // Inline styles for mammoth tables in PDF
    const tableStyle = `<style>
      table { width:100%; border-collapse:collapse; margin:10px 0; font-size:12px; }
      th, td { border:1px solid #d1d5db; padding:6px 10px; text-align:left; vertical-align:top; }
      th { background:#f1f5f9; font-weight:600; color:#1e293b; }
      tr:nth-child(even) td { background:#f8fafc; }
      h1,h2,h3,h4 { color:#0f172a; margin:14px 0 6px; }
      h1 { font-size:16px; border-bottom:2px solid #0ea5e9; padding-bottom:6px; }
      h2 { font-size:14px; } h3 { font-size:13px; } h4 { font-size:12px; }
      strong, b { color:#1e293b; }
      ul, ol { padding-left:20px; margin:6px 0; }
      p { margin:4px 0; line-height:1.8; }
    </style>`;

    const infoRow = (label, value) => value ? `
      <tr>
        <td style="padding:6px 12px;color:#64748b;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;width:140px;border-bottom:1px solid #f1f5f9;">${label}</td>
        <td style="padding:6px 12px;font-size:12.5px;color:#1e293b;font-weight:500;border-bottom:1px solid #f1f5f9;">${value}</td>
      </tr>` : "";

    const sectionTitle = (title) => `
      <div style="margin-top:20px;margin-bottom:8px;display:flex;align-items:center;gap:6px;">
        <div style="width:4px;height:16px;background:linear-gradient(135deg,#0ea5e9,#8b5cf6);border-radius:2px;"></div>
        <span style="font-size:11px;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.08em;">${title}</span>
      </div>`;

    return `
      ${isHtml ? tableStyle : ""}
      <div style="font-family:'Segoe UI',system-ui,-apple-system,sans-serif;color:#1e293b;max-width:750px;margin:0 auto;padding:0;">

        <!-- ════ Header ════ -->
        <div style="background:linear-gradient(135deg,#0c4a6e 0%,#1e3a5f 50%,#312e81 100%);padding:28px 32px 24px;border-radius:0 0 16px 16px;margin-bottom:28px;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div>
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                <div style="width:36px;height:36px;background:linear-gradient(135deg,#38bdf8,#8b5cf6);border-radius:10px;display:flex;align-items:center;justify-content:center;">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2c-2 0-3.5 1.5-3.5 3.5 0 1 .5 2 1.2 2.6C8.5 9 7.5 10.5 7.5 12.5c0 1 .3 2 .8 2.8-.8.8-1.3 1.8-1.3 3.2 0 2 1.5 3.5 3.5 3.5M12 2c2 0 3.5 1.5 3.5 3.5 0 1-.5 2-1.2 2.6 1.2.9 2.2 2.4 2.2 4.4 0 1-.3 2-.8 2.8.8.8 1.3 1.8 1.3 3.2 0 2-1.5 3.5-3.5 3.5M12 2v20"/></svg>
                </div>
                <div>
                  <h1 style="font-size:18px;font-weight:800;color:#f1f5f9;margin:0;letter-spacing:-0.02em;">ClinicalPFE</h1>
                  <p style="font-size:10px;color:#94a3b8;margin:0;font-weight:400;">Module de Pré-Analyse Clinique Intelligente</p>
                </div>
              </div>
            </div>
            <div style="text-align:right;">
              <div style="font-size:14px;font-weight:700;color:#e2e8f0;">RAPPORT MÉDICAL</div>
              <div style="font-size:10px;color:#94a3b8;margin-top:2px;">${date}</div>
              <div style="font-size:9px;color:#64748b;margin-top:1px;">Réf: RPT-${(report.id || "000").toString().substring(0, 8).toUpperCase()}</div>
            </div>
          </div>
        </div>

        <!-- ════ Patient Identity Card ════ -->
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:0;margin:0 16px 20px;overflow:hidden;">
          <div style="background:linear-gradient(90deg,#0ea5e9,#8b5cf6);height:4px;"></div>
          <div style="padding:16px 20px 12px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
              <div>
                <div style="font-size:9px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.1em;font-weight:600;">Patient</div>
                <div style="font-size:18px;font-weight:800;color:#0f172a;letter-spacing:-0.02em;">${patientName}</div>
              </div>
              ${d.gender ? '<div style="width:32px;height:32px;border-radius:8px;background:' + (d.gender === "M" ? "#dbeafe" : d.gender === "F" ? "#fce7f3" : "#f1f5f9") + ';display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;color:' + (d.gender === "M" ? "#2563eb" : d.gender === "F" ? "#db2777" : "#64748b") + ';">' + d.gender + '</div>' : ""}
            </div>

            ${sectionTitle("Identité")}
            <table style="width:100%;border-collapse:collapse;">
              ${infoRow("Âge", d.age)}
              ${infoRow("Sexe", d.gender === "M" ? "Masculin" : d.gender === "F" ? "Féminin" : d.gender)}
              ${infoRow("Date de naissance", d.date_of_birth ? formatDate(d.date_of_birth) : "")}
              ${infoRow("Origine", d.origin)}
              ${infoRow("Résidence", d.residence)}
            </table>

            ${(d.parent_father || d.parent_mother || d.consanguinity || d.siblings_info) ?
              sectionTitle("Antécédents Familiaux") +
              '<table style="width:100%;border-collapse:collapse;">' +
                infoRow("Père", d.parent_father) +
                infoRow("Mère", d.parent_mother) +
                infoRow("Consanguinité", d.consanguinity) +
                infoRow("Fratrie", d.siblings_info) +
              '</table>'
            : ""}

            ${sectionTitle("Diagnostic & Traitement")}
            <table style="width:100%;border-collapse:collapse;">
              ${infoRow("Diagnostic principal", diag)}
              ${infoRow("Diagnostics associés", d.associated_diagnoses)}
              ${infoRow("Date du diagnostic", d.date_of_diagnosis ? formatDate(d.date_of_diagnosis) : "")}
              ${infoRow("Âge au diagnostic", d.age_at_diagnosis)}
              ${infoRow("Médecin traitant", doctor ? "Dr. " + doctor : "")}
              ${infoRow("Traitement en cours", d.current_treatment)}
            </table>

            ${d.notes ?
              sectionTitle("Notes Cliniques") +
              '<div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:10px 14px;font-size:12px;color:#475569;line-height:1.7;margin-top:4px;">' +
                d.notes.replace(/\n/g, "<br/>") +
              '</div>'
            : ""}
          </div>
        </div>

        <!-- ════ Report Content ════ -->
        <div style="margin:0 16px 24px;">
          <div style="display:flex;align-items:center;gap:6px;margin-bottom:10px;">
            <div style="width:4px;height:16px;background:linear-gradient(135deg,#0ea5e9,#8b5cf6);border-radius:2px;"></div>
            <span style="font-size:11px;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.08em;">Contenu du Rapport</span>
            <span style="font-size:10px;color:#94a3b8;margin-left:auto;">${report.filename || "—"}</span>
          </div>
          <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:20px 24px;">
            <div style="font-size:12.5px;line-height:1.9;color:#334155;">
              ${reportContent}
            </div>
          </div>
        </div>

        <!-- ════ Footer ════ -->
        <div style="margin:0 16px;padding:16px 0;border-top:2px solid #e2e8f0;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
              <div style="font-size:9px;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;">Document généré automatiquement</div>
              <div style="font-size:9px;color:#cbd5e1;margin-top:2px;">ClinicalPFE · ${generatedDate} à ${generatedTime}</div>
            </div>
            <div style="text-align:right;">
              <div style="font-size:9px;color:#94a3b8;font-weight:600;">CONFIDENTIEL</div>
              <div style="font-size:8px;color:#cbd5e1;margin-top:1px;">Usage médical uniquement</div>
            </div>
          </div>
        </div>

      </div>
    `;
  };

  const printReport = (report) => {
    const content = buildPdfHtml(report);
    const win = window.open("", "_blank");
    if (!win) return showToast("Pop-up bloquée par le navigateur", "error");
    win.document.write(`<!DOCTYPE html><html><head>
      <title>${(report.filename || "Rapport").replace(".docx", "")}</title>
      <style>
        body { font-family: 'Segoe UI', system-ui, sans-serif; color: #1e293b; margin: 0; padding: 0; }
        @media print { @page { margin: 12mm; } }
        table { width:100%; border-collapse:collapse; margin:8px 0; }
        th, td { border:1px solid #d1d5db; padding:6px 10px; text-align:left; vertical-align:top; }
        th { background:#f1f5f9; font-weight:600; color:#1e293b; }
        tr:nth-child(even) td { background:#f8fafc; }
        h1,h2,h3,h4 { color:#0f172a; margin:12px 0 6px; }
        h1 { font-size:16px; border-bottom:2px solid #0ea5e9; padding-bottom:6px; }
        h2 { font-size:14px; } h3 { font-size:13px; }
        strong, b { color:#1e293b; }
        ul, ol { padding-left:20px; margin:6px 0; }
        p { margin:4px 0; line-height:1.8; }
      </style>
    </head><body>${content}</body></html>`);
    win.document.close();
    win.focus();
    setTimeout(() => { win.print(); }, 500);
  };

  const formatDate = (d) => {
    if (!d) return "—";
    try { return new Date(d).toLocaleDateString("fr-FR", { day: "numeric", month: "short", year: "numeric" }); } catch { return d; }
  };

  const GenderAvatar = ({ gender, large = false }) => {
    const size = large ? 24 : 16;
    const color = gender === "M" ? "#60a5fa" : gender === "F" ? "#f472b6" : "#94a3b8";
    return <UserIcon size={size} style={{ color }} />;
  };

  const genderColor = (g) => g === "M" ? "#60a5fa" : g === "F" ? "#f472b6" : "#94a3b8";

  // Derived unique lists for filter dropdowns
  const diagnoses = [...new Set(dossiers.filter(d => d.principal_diagnosis).map(d => d.principal_diagnosis))].sort();
  const origins = [...new Set(dossiers.filter(d => d.origin).map(d => d.origin))].sort();
  const doctors = [...new Set(dossiers.filter(d => d.treating_doctor).map(d => d.treating_doctor))].sort();

  const activeFilterCount = Object.values(filters).filter(Boolean).length;

  const filteredDossiers = dossiers.filter(d => {
    if (filters.diagnosis && d.principal_diagnosis !== filters.diagnosis) return false;
    if (filters.origin && d.origin !== filters.origin) return false;
    if (filters.gender && d.gender !== filters.gender) return false;
    if (filters.doctor && d.treating_doctor !== filters.doctor) return false;
    return true;
  });

  // Render the correct icon for an info field
  const renderInfoIcon = (key) => {
    const IconComp = INFO_ICON_COMPONENTS[key] || ClipboardDocumentListIcon;
    return <IconComp size={16} style={{ color: "var(--accent-cyan)", opacity: 0.7 }} />;
  };

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
            <PlusIcon size={18} />
            Nouveau dossier
          </button>
        </div>
      </div>

      {/* ═══ Search & Filters ═══ */}
      <div className={styles.controlsRow}>
        <div className={styles.searchWrap}>
          <MagnifyingGlassIcon size={16} style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", color: "var(--text-dim)", pointerEvents: "none" }} />
          <input className={styles.searchInput} placeholder="Rechercher un patient..." value={searchQuery} onChange={handleSearch} />
        </div>
      </div>

      {/* ═══ Filter Bar ═══ */}
      <div className={styles.filterBar}>
        <div className={styles.filterBarLeft}>
          {/* Wilaya / Ville */}
          <div className={styles.filterGroup}>
            <MapPinIcon size={13} className={styles.filterIcon} />
            <select
              className={`${styles.filterSelect} ${filters.origin ? styles.filterSelectActive : ""}`}
              value={filters.origin}
              onChange={(e) => setFilters({ ...filters, origin: e.target.value })}
            >
              <option value="">Toutes les wilayas</option>
              {origins.map((o) => <option key={o} value={o}>{o}</option>)}
            </select>
          </div>

          {/* Pathologie */}
          <div className={styles.filterGroup}>
            <HeartIcon size={13} className={styles.filterIcon} />
            <select
              className={`${styles.filterSelect} ${filters.diagnosis ? styles.filterSelectActive : ""}`}
              value={filters.diagnosis}
              onChange={(e) => setFilters({ ...filters, diagnosis: e.target.value })}
            >
              <option value="">Toutes les pathologies</option>
              {diagnoses.map((d) => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>

          {/* Sexe */}
          <div className={styles.filterGroup}>
            <IdentificationIcon size={13} className={styles.filterIcon} />
            <select
              className={`${styles.filterSelect} ${filters.gender ? styles.filterSelectActive : ""}`}
              value={filters.gender}
              onChange={(e) => setFilters({ ...filters, gender: e.target.value })}
            >
              <option value="">Tous les sexes</option>
              <option value="M">Masculin</option>
              <option value="F">Féminin</option>
              <option value="Inconnu">Inconnu</option>
            </select>
          </div>

          {/* Médecin */}
          {doctors.length > 0 && (
            <div className={styles.filterGroup}>
              <HeartIcon size={13} className={styles.filterIcon} />
              <select
                className={`${styles.filterSelect} ${filters.doctor ? styles.filterSelectActive : ""}`}
                value={filters.doctor}
                onChange={(e) => setFilters({ ...filters, doctor: e.target.value })}
              >
                <option value="">Tous les médecins</option>
                {doctors.map((d) => <option key={d} value={d}>Dr. {d}</option>)}
              </select>
            </div>
          )}
        </div>

        {/* Active filter count + clear */}
        {activeFilterCount > 0 && (
          <button className={styles.filterClearAll} onClick={() => setFilters({ diagnosis: "", origin: "", gender: "", doctor: "" })}>
            <XMarkIcon size={12} />
            Réinitialiser ({activeFilterCount})
          </button>
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
            <FolderIcon size={64} style={{ color: "var(--text-dim)" }} />
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
                  <GenderAvatar gender={d.gender} />
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
                {d.treating_doctor && <span className={styles.metaTag}><HeartIcon size={11} style={{ opacity: 0.6 }} /> Dr. {d.treating_doctor}</span>}
                {d.consanguinity && <span className={styles.metaTag}><DnaIcon size={11} style={{ opacity: 0.6 }} /> Consanguinité</span>}
                {d.age_at_diagnosis && <span className={styles.metaTag}><MicroscopeIcon size={11} style={{ opacity: 0.6 }} /> Diag. {d.age_at_diagnosis}</span>}
              </div>

              <div className={styles.cardFooter}>
                <span className={styles.cardDate}>{formatDate(d.created_at)}</span>
                <div className={styles.cardActions}>
                  <button className={styles.iconBtn} title="Modifier" onClick={(e) => { e.stopPropagation(); setEditingDossier(d); setFormData({...d}); }}>
                    <PencilSquareIcon size={13} />
                  </button>
                  <button className={`${styles.iconBtn} ${styles.iconBtnDanger}`} title="Supprimer" onClick={(e) => deleteDossier(d.id, e)}>
                    <TrashIcon size={13} />
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
                <XMarkIcon size={20} />
              </button>

              <div className={styles.detailProfile}>
                <div className={styles.avatarLg} style={{ borderColor: genderColor(selectedDossier.gender) }}>
                  <GenderAvatar gender={selectedDossier.gender} large />
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
                        <span className={styles.infoIcon}>{renderInfoIcon(key)}</span>
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
                    <PlusIcon size={14} />
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
                          <div className={styles.reportCardIcon}>
                            <DocumentTextIcon size={20} style={{ color: "var(--accent-cyan)" }} />
                          </div>
                          <div className={styles.reportCardInfo}>
                            <div className={styles.reportCardTitle}>{r.filename?.replace(".docx", "") || "Rapport"}</div>
                            <div className={styles.reportCardMeta}>
                              {formatDate(r.report_date || r.created_at)}
                              {r.char_count ? ` · ${(r.char_count / 1000).toFixed(1)}k car.` : ""}
                            </div>
                          </div>
                          <ChevronDownIcon size={16} className={styles.reportChevron} />
                        </div>
                        {/* Action buttons */}
                        <div className={styles.reportActions}>
                          <button className={styles.reportActionBtn} title="Lire" onClick={(e) => { e.stopPropagation(); openPdfViewer(r); }}>
                            <EyeIcon size={13} />
                            Lire
                          </button>
                          <button className={styles.reportActionBtn} title="PDF" onClick={(e) => { e.stopPropagation(); downloadPdf(r); }}>
                            <ArrowDownTrayIcon size={13} />
                            PDF
                          </button>
                          <button className={styles.reportActionBtn} title="TXT" onClick={(e) => { e.stopPropagation(); downloadTxt(r); }}>
                            <ArrowDownTrayIcon size={13} />
                            TXT
                          </button>
                          <button className={styles.reportActionBtn} title="DOCX" onClick={(e) => { e.stopPropagation(); downloadDocx(r); }}>
                            <ArrowDownTrayIcon size={13} />
                            DOCX
                          </button>
                          <button className={styles.reportActionBtn} title="Imprimer" onClick={(e) => { e.stopPropagation(); printReport(r); }}>
                            <PrinterIcon size={13} />
                            Imprimer
                          </button>
                        </div>
                        {/* Expanded content */}
                        {selectedReport?.id === r.id && (
                          <div className={styles.reportContent}>
                            <div className={styles.reportContentHeader}>
                              <span><ClipboardDocumentListIcon size={14} style={{ verticalAlign: "middle", marginRight: 4 }} /> Contenu du rapport</span>
                              <button className={styles.reportContentClose} onClick={() => setSelectedReport(null)}>
                                <XMarkIcon size={14} />
                              </button>
                            </div>
                            {(() => {
                              const content = r.content_text || "Aucun contenu disponible";
                              const isHtml = content.trim().startsWith("<");
                              return isHtml
                                ? <div className={styles.reportHtml} dangerouslySetInnerHTML={{ __html: content }} />
                                : <pre className={styles.reportText}>{content}</pre>;
                            })()}
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
                <XMarkIcon size={20} />
              </button>
            </div>

            {!editingDossier && (
              <div className={styles.modeSwitch}>
                <button className={`${styles.modeSwitchBtn} ${createMode === "file" ? styles.modeSwitchActive : ""}`} onClick={() => setCreateMode("file")}>
                  <DocumentArrowUpIcon size={15} /> Depuis .docx
                </button>
                <button className={`${styles.modeSwitchBtn} ${createMode === "manual" ? styles.modeSwitchActive : ""}`} onClick={() => setCreateMode("manual")}>
                  <PencilIcon size={15} /> Manuel
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
                    <DocumentArrowUpIcon size={40} style={{ color: "var(--accent-cyan)", opacity: 0.6 }} />
                    <p className={styles.dropTitle}>Déposez un rapport .docx</p>
                    <p className={styles.dropSub}>Extraction automatique des données patient</p>
                  </>
                )}
              </div>
            )}

            {extractedData && (
              <div className={styles.extractSuccess}>
                <CheckCircleIcon size={16} style={{ verticalAlign: "middle", marginRight: 6 }} />
                {Object.keys(extractedData.extracted).length} champs extraits de «{extractedData.filename}»
              </div>
            )}

            {(createMode === "manual" || extractedData || editingDossier) && (
              <>
                <div className={styles.formGrid}>
                  {Object.entries(FIELD_LABELS).map(([key, label]) => (
                    <div key={key} className={["current_treatment", "notes", "siblings_info", "associated_diagnoses"].includes(key) ? styles.formColFull : styles.formCol}>
                      <label className={styles.formLabel}>
                        <span className={styles.formLabelIcon}>{renderInfoIcon(key)}</span> {label}
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
              <h3 className={styles.viewerTitle}>
                <ClipboardDocumentListIcon size={18} style={{ verticalAlign: "middle", marginRight: 6, opacity: 0.7 }} />
                {viewerReport.filename?.replace(".docx", "") || "Rapport"}
              </h3>
              <div className={styles.viewerActions}>
                <button className={styles.viewerBtn} onClick={() => downloadPdf(viewerReport)}>
                  <ArrowDownTrayIcon size={13} style={{ verticalAlign: "middle", marginRight: 4 }} /> PDF
                </button>
                <button className={styles.viewerBtn} onClick={() => downloadTxt(viewerReport)}>
                  <ArrowDownTrayIcon size={13} style={{ verticalAlign: "middle", marginRight: 4 }} /> TXT
                </button>
                <button className={styles.viewerBtn} onClick={() => printReport(viewerReport)}>
                  <PrinterIcon size={13} style={{ verticalAlign: "middle", marginRight: 4 }} /> Imprimer
                </button>
                <button className={styles.viewerClose} onClick={() => setViewerReport(null)}>
                  <XMarkIcon size={18} />
                </button>
              </div>
            </div>
            <div className={styles.viewerMeta}>
              <span><UserIcon size={13} style={{ verticalAlign: "middle", marginRight: 4, opacity: 0.6 }} /> {selectedDossier?.full_name || viewerReport.patient_name}</span>
              {(selectedDossier?.treating_doctor || viewerReport.doctor_name) && <span><HeartIcon size={13} style={{ verticalAlign: "middle", marginRight: 4, opacity: 0.6 }} /> Dr. {selectedDossier?.treating_doctor || viewerReport.doctor_name}</span>}
              <span><CalendarDaysIcon size={13} style={{ verticalAlign: "middle", marginRight: 4, opacity: 0.6 }} /> {formatDate(viewerReport.report_date || viewerReport.created_at)}</span>
              {viewerReport.char_count && <span><DocumentMagnifyingGlassIcon size={13} style={{ verticalAlign: "middle", marginRight: 4, opacity: 0.6 }} /> {(viewerReport.char_count / 1000).toFixed(1)}k caractères</span>}
            </div>
            <div className={styles.viewerContent} ref={pdfContentRef}>
              {(() => {
                const content = viewerReport.content_text || "Aucun contenu disponible";
                const isHtml = content.trim().startsWith("<");
                return isHtml
                  ? <div className={styles.viewerHtml} dangerouslySetInnerHTML={{ __html: content }} />
                  : <pre className={styles.viewerText}>{content}</pre>;
              })()}
            </div>
          </div>
        </div>
      )}

      {/* Toast */}
      {toast && (
        <div className={`${styles.toast} ${styles[`toast${toast.type.charAt(0).toUpperCase() + toast.type.slice(1)}`]}`}>
          {toast.type === "success" && <CheckCircleIcon size={15} style={{ color: "var(--accent-green)", flexShrink: 0 }} />}
          {toast.type === "error" && <XMarkIcon size={15} style={{ color: "var(--accent-red)", flexShrink: 0 }} />}
          {toast.message}
        </div>
      )}
    </div>
  );
}
