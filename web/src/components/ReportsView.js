"use client";
import { useState, useEffect, useRef, useCallback } from "react";
import { supabase } from "@/lib/supabase";
import styles from "./ReportsView.module.css";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

export default function ReportsView() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedReport, setSelectedReport] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [toast, setToast] = useState(null);
  const uploadInputRef = useRef(null);
  const searchTimeoutRef = useRef(null);

  const showToast = (message, type = "info") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const fetchReports = useCallback(async (query = "") => {
    setLoading(true);
    try {
      let result;
      if (query.trim()) {
        result = await supabase
          .from("medical_reports")
          .select("*")
          .or(
            `patient_name.ilike.%${query}%,doctor_name.ilike.%${query}%,pathology.ilike.%${query}%,filename.ilike.%${query}%`
          )
          .order("created_at", { ascending: false });
      } else {
        result = await supabase
          .from("medical_reports")
          .select("*")
          .order("created_at", { ascending: false });
      }
      if (result.error) throw result.error;
      setReports(result.data || []);
    } catch (err) {
      console.error("Error fetching reports:", err);
      showToast("Erreur de chargement des rapports", "error");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  const handleSearch = (e) => {
    const q = e.target.value;
    setSearchQuery(q);
    clearTimeout(searchTimeoutRef.current);
    searchTimeoutRef.current = setTimeout(() => fetchReports(q), 300);
  };

  const syncReports = async () => {
    setSyncing(true);
    try {
      const res = await fetch(`${API_URL}/api/reports/sync`, { method: "POST" });
      const data = await res.json();
      showToast(`${data.synced} rapports synchronisés sur ${data.total}`, "success");
      fetchReports();
    } catch (err) {
      showToast("Erreur de synchronisation", "error");
    } finally {
      setSyncing(false);
    }
  };

  const deleteReport = async (id, e) => {
    e.stopPropagation();
    if (!confirm("Supprimer ce rapport ?")) return;
    try {
      const { error } = await supabase
        .from("medical_reports")
        .delete()
        .eq("id", id);
      if (error) throw error;
      showToast("Rapport supprimé", "success");
      fetchReports(searchQuery);
      if (selectedReport?.id === id) setSelectedReport(null);
    } catch (err) {
      showToast("Erreur de suppression", "error");
    }
  };

  const handleUpload = async (e) => {
    const files = e.target.files;
    if (!files?.length) return;

    const formData = new FormData();
    for (const file of files) {
      formData.append("files", file);
    }

    try {
      const res = await fetch(`${API_URL}/api/reports/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      showToast(`${data.count} rapport(s) ajouté(s)`, "success");
      setShowUploadModal(false);
      fetchReports();
    } catch (err) {
      showToast("Erreur d'upload", "error");
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "—";
    try {
      return new Date(dateStr).toLocaleDateString("fr-FR", {
        day: "numeric",
        month: "short",
        year: "numeric",
      });
    } catch {
      return dateStr;
    }
  };

  const formatSize = (bytes) => {
    if (!bytes) return "—";
    if (bytes < 1024) return `${bytes} o`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} Ko`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`;
  };

  // Get unique pathologies and doctors for filter tags
  const pathologies = [...new Set(reports.filter(r => r.pathology).map(r => r.pathology))];
  const doctors = [...new Set(reports.filter(r => r.doctor_name).map(r => r.doctor_name))];

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.sectionHeader}>
        <div>
          <h1 className={styles.sectionTitle}>📋 Rapports Médicaux</h1>
          <div className={styles.sectionCount}>
            {loading ? "Chargement..." : `${reports.length} rapport(s)`}
          </div>
        </div>
        <div className={styles.headerActions}>
          <button
            className={styles.btnSecondary}
            onClick={syncReports}
            disabled={syncing}
          >
            {syncing ? "⏳ Synchronisation..." : "🔄 Synchroniser les fichiers locaux"}
          </button>
          <button className={styles.btnPrimary} onClick={() => setShowUploadModal(true)}>
            ➕ Ajouter un rapport
          </button>
        </div>
      </div>

      {/* Search */}
      <div className={styles.searchBar}>
        <span className={styles.searchIcon}>🔍</span>
        <input
          type="text"
          className={styles.searchInput}
          placeholder="Rechercher par nom du patient, médecin, pathologie..."
          value={searchQuery}
          onChange={handleSearch}
        />
      </div>

      {/* Filter Tags */}
      {pathologies.length > 0 && (
        <div className={styles.filterTags}>
          {pathologies.map((p) => (
            <button
              key={p}
              className={`${styles.filterTag} ${searchQuery === p ? styles.filterTagActive : ""}`}
              onClick={() => {
                setSearchQuery(searchQuery === p ? "" : p);
                fetchReports(searchQuery === p ? "" : p);
              }}
            >
              {p}
            </button>
          ))}
          {doctors.map((d) => (
            <button
              key={d}
              className={`${styles.filterTag} ${styles.filterTagDoctor} ${searchQuery === d ? styles.filterTagActive : ""}`}
              onClick={() => {
                setSearchQuery(searchQuery === d ? "" : d);
                fetchReports(searchQuery === d ? "" : d);
              }}
            >
              Dr. {d}
            </button>
          ))}
        </div>
      )}

      {/* Reports Grid */}
      {loading ? (
        <div className={styles.loadingState}>
          <div className={styles.spinner}></div>
          <span>Chargement des rapports...</span>
        </div>
      ) : reports.length === 0 ? (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>📋</div>
          <div className={styles.emptyTitle}>Aucun rapport trouvé</div>
          <div className={styles.emptyText}>
            {searchQuery
              ? "Essayez de modifier votre recherche"
              : 'Cliquez sur "Synchroniser" pour importer les rapports existants'}
          </div>
          {!searchQuery && (
            <button className={styles.btnPrimary} onClick={syncReports} style={{ width: "auto", marginTop: "1rem" }}>
              🔄 Synchroniser les fichiers locaux
            </button>
          )}
        </div>
      ) : (
        <div className={styles.reportsGrid}>
          {reports.map((report) => (
            <div
              key={report.id}
              className={styles.reportCard}
              onClick={() => setSelectedReport(report)}
            >
              <div className={styles.reportCardHeader}>
                <div className={styles.reportPatient}>
                  {report.patient_name || "Patient inconnu"}
                </div>
                {report.pathology && (
                  <span className={styles.tagPathology}>{report.pathology}</span>
                )}
              </div>

              <div className={styles.reportMeta}>
                {report.doctor_name && (
                  <span className={styles.metaItem}>👨‍⚕️ Dr. {report.doctor_name}</span>
                )}
                {report.report_date && (
                  <span className={styles.metaItem}>📅 {formatDate(report.report_date)}</span>
                )}
                <span className={styles.metaItem}>📄 {formatSize(report.file_size_bytes)}</span>
                {report.char_count && (
                  <span className={styles.metaItem}>✏️ {report.char_count.toLocaleString()} car.</span>
                )}
              </div>

              <div className={styles.reportActions}>
                <button
                  className={styles.btnAction}
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedReport(report);
                  }}
                >
                  👁️ Voir
                </button>
                <button
                  className={`${styles.btnAction} ${styles.btnActionDanger}`}
                  onClick={(e) => deleteReport(report.id, e)}
                >
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ═══ Report Detail Modal ═══ */}
      {selectedReport && (
        <div className={styles.modalOverlay} onClick={() => setSelectedReport(null)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <div>
                <h2 className={styles.modalTitle}>
                  {selectedReport.patient_name || "Patient inconnu"}
                </h2>
                <div className={styles.modalSubtitle}>
                  {selectedReport.filename}
                </div>
              </div>
              <button className={styles.modalClose} onClick={() => setSelectedReport(null)}>
                ✕
              </button>
            </div>

            <div className={styles.modalMeta}>
              {selectedReport.doctor_name && (
                <span className={styles.metaItem}>👨‍⚕️ Dr. {selectedReport.doctor_name}</span>
              )}
              {selectedReport.report_date && (
                <span className={styles.metaItem}>📅 {formatDate(selectedReport.report_date)}</span>
              )}
              {selectedReport.pathology && (
                <span className={styles.tagPathology}>{selectedReport.pathology}</span>
              )}
              <span className={styles.metaItem}>
                ✏️ {selectedReport.char_count?.toLocaleString()} caractères
              </span>
            </div>

            <div className={styles.modalContent}>
              <div className={styles.contentLabel}>Contenu du rapport</div>
              <div className={styles.textContent}>
                {selectedReport.content_text || "Contenu non disponible"}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ═══ Upload Modal ═══ */}
      {showUploadModal && (
        <div className={styles.modalOverlay} onClick={() => setShowUploadModal(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Ajouter un rapport médical</h2>
              <button className={styles.modalClose} onClick={() => setShowUploadModal(false)}>
                ✕
              </button>
            </div>
            <div
              className={styles.uploadZone}
              onClick={() => uploadInputRef.current?.click()}
            >
              <input
                type="file"
                ref={uploadInputRef}
                accept=".docx"
                multiple
                onChange={handleUpload}
                style={{ display: "none" }}
              />
              <div className={styles.uploadIcon}>📤</div>
              <div className={styles.uploadTitle}>Déposez des fichiers .docx ici</div>
              <div className={styles.uploadSubtitle}>ou cliquez pour parcourir</div>
            </div>
          </div>
        </div>
      )}

      {/* ═══ Toast ═══ */}
      {toast && (
        <div className={`${styles.toast} ${styles[`toast${toast.type.charAt(0).toUpperCase() + toast.type.slice(1)}`]}`}>
          {toast.message}
        </div>
      )}
    </div>
  );
}
