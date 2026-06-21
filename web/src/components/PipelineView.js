"use client";
import { useState, useRef } from "react";
import styles from "./PipelineView.module.css";
import {
  DocumentTextIcon,
  PencilIcon,
  DocumentArrowUpIcon,
  XMarkIcon,
  MicroscopeIcon,
  ArrowDownTrayIcon,
} from "@/components/Icons";

const API_URL = typeof window !== "undefined" && window.location.hostname.includes("devtunnels.ms")
  ? "https://wn3r3xh0-5000.uks1.devtunnels.ms"
  : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000");

export default function PipelineView() {
  const [inputMode, setInputMode] = useState("file");
  const [selectedFile, setSelectedFile] = useState(null);
  const [pastedText, setPastedText] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState({ percent: 0, text: "" });
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("entities");
  const [stepStatuses, setStepStatuses] = useState([0, 0, 0, 0]);
  const fileInputRef = useRef(null);

  const handleFileDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const file = e.dataTransfer?.files?.[0] || e.target.files?.[0];
    if (file && (file.name.endsWith(".docx") || file.name.endsWith(".txt"))) {
      setSelectedFile(file);
      setError(null);
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const runAnalysis = async () => {
    setIsAnalyzing(true);
    setError(null);
    setResult(null);
    setStepStatuses([1, 0, 0, 0]);
    setProgress({ percent: 10, text: "Module 1 : Dé-identification (PHI)..." });

    try {
      const formData = new FormData();
      if (inputMode === "file" && selectedFile) {
        formData.append("file", selectedFile);
      } else if (inputMode === "text" && pastedText.trim()) {
        formData.append("text", pastedText.trim());
      } else {
        setError("Veuillez fournir un fichier ou du texte.");
        setIsAnalyzing(false);
        return;
      }

      // Simulate progress steps
      setStepStatuses([2, 1, 0, 0]);
      setProgress({ percent: 30, text: "Module 2 : Extraction NER (DeBERTa-v3 / GLiNER)..." });

      const res = await fetch(`${API_URL}/api/pipeline/run`, {
        method: "POST",
        body: formData,
      });

      setStepStatuses([2, 2, 1, 0]);
      setProgress({ percent: 70, text: "Module 3 : Validation (NegEx / Temporel)..." });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Erreur serveur");
      }

      setStepStatuses([2, 2, 2, 2]);
      setProgress({ percent: 100, text: `Analyse terminée en ${data.processing_time}s` });

      setTimeout(() => {
        setResult(data);
        setIsAnalyzing(false);
      }, 500);
    } catch (err) {
      setError(err.message);
      setIsAnalyzing(false);
      setStepStatuses([0, 0, 0, 0]);
    }
  };

  const downloadPhenopacket = () => {
    if (!result?.phenopacket) return;
    const blob = new Blob([JSON.stringify(result.phenopacket, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `phenopacket_${result.source_name || "clinical_note"}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const syntaxHighlight = (json) => {
    const str = JSON.stringify(json, null, 2);
    return str.replace(
      /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
      (match) => {
        let cls = styles.jsonNumber;
        if (/^"/.test(match)) {
          cls = /:$/.test(match) ? styles.jsonKey : styles.jsonString;
        } else if (/true|false/.test(match)) {
          cls = styles.jsonBoolean;
        } else if (/null/.test(match)) {
          cls = styles.jsonNull;
        }
        return `<span class="${cls}">${match}</span>`;
      }
    );
  };

  const stepNames = [
    "Dé-identification (PHI)",
    "Extraction NER (DeBERTa-v3 / GLiNER)",
    "Validation (NegEx / Temporel / Numérique)",
    "Normalisation HPO / UMLS / ORDO",
  ];

  const getStepClass = (status) => {
    if (status === 2) return styles.stepDone;
    if (status === 1) return styles.stepActive;
    return styles.stepPending;
  };

  return (
    <div className={styles.twoCol}>
      <div>
        {/* Input Mode Toggle */}
        <div className={styles.modeToggle}>
          <button
            className={`${styles.modeBtn} ${inputMode === "file" ? styles.modeBtnActive : ""}`}
            onClick={() => setInputMode("file")}
          >
            <DocumentTextIcon size={15} /> Fichier (.docx / .txt)
          </button>
          <button
            className={`${styles.modeBtn} ${inputMode === "text" ? styles.modeBtnActive : ""}`}
            onClick={() => setInputMode("text")}
          >
            <PencilIcon size={15} /> Texte libre
          </button>
        </div>

        {/* File Upload */}
        {inputMode === "file" && !selectedFile && (
          <div
            className={styles.uploadZone}
            onClick={() => fileInputRef.current?.click()}
            onDrop={handleFileDrop}
            onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add(styles.dragover); }}
            onDragLeave={(e) => e.currentTarget.classList.remove(styles.dragover)}
          >
            <input
              type="file"
              ref={fileInputRef}
              accept=".docx,.txt"
              onChange={handleFileDrop}
              style={{ display: "none" }}
            />
            <div className={styles.uploadIcon}>
              <DocumentArrowUpIcon size={36} style={{ color: "var(--accent-cyan)", opacity: 0.7 }} />
            </div>
            <div className={styles.uploadTitle}>Déposez un rapport clinique (.docx / .txt)</div>
            <div className={styles.uploadSubtitle}>ou cliquez pour parcourir vos fichiers</div>
          </div>
        )}

        {/* File Banner */}
        {inputMode === "file" && selectedFile && (
          <div className={styles.fileBanner}>
            <div>
              <div className={styles.fileBannerName}>{selectedFile.name}</div>
              <div className={styles.fileBannerMeta}>
                {(selectedFile.size / 1024).toFixed(1)} Ko
              </div>
            </div>
            <button className={styles.btnSmSecondary} onClick={clearFile}>
              <XMarkIcon size={13} style={{ verticalAlign: "middle", marginRight: 3 }} /> Retirer
            </button>
          </div>
        )}

        {/* Text Input */}
        {inputMode === "text" && (
          <textarea
            className={styles.textInput}
            value={pastedText}
            onChange={(e) => setPastedText(e.target.value)}
            placeholder="Le patient présente une hypotonie axiale, un retard psychomoteur et des crises épileptiques depuis l'âge de 3 mois...&#10;&#10;Patient is a 55yo male with progressive muscle weakness..."
          />
        )}

        {/* Analyze Button */}
        <button
          className={styles.btnPrimary}
          onClick={runAnalysis}
          disabled={isAnalyzing || (inputMode === "file" && !selectedFile) || (inputMode === "text" && pastedText.trim().length < 50)}
        >
          {isAnalyzing ? (
            <>
              <span className={styles.spinner}></span> Analyse en cours...
            </>
          ) : (
            <>
              <MicroscopeIcon size={17} style={{ verticalAlign: "middle", marginRight: 4 }} /> Lancer l&apos;analyse
            </>
          )}
        </button>

        {/* Progress */}
        {isAnalyzing && (
          <div className={styles.progressContainer}>
            <div className={styles.progressBar}>
              <div className={styles.progressFill} style={{ width: `${progress.percent}%` }}></div>
            </div>
            <div className={styles.progressText}>{progress.text}</div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className={styles.errorCard}>
            <strong>Erreur :</strong> {error}
          </div>
        )}

        {/* ═══ Results ═══ */}
        {result && (
          <div className={styles.resultsSection}>
            {/* Stats Grid */}
            <div className={styles.statGrid}>
              <div className={styles.statBox}>
                <div className={`${styles.statValue} ${styles.cyan}`}>{result.stats.total_entities}</div>
                <div className={styles.statLabel}>Entités extraites</div>
              </div>
              <div className={styles.statBox}>
                <div className={`${styles.statValue} ${styles.green}`}>{result.stats.matched_hpo}</div>
                <div className={styles.statLabel}>Codes HPO attribués</div>
              </div>
              <div className={styles.statBox}>
                <div className={`${styles.statValue} ${styles.amber}`}>{result.stats.numeric_phenotypes}</div>
                <div className={styles.statLabel}>Phénotypes numériques</div>
              </div>
              <div className={styles.statBox}>
                <div className={`${styles.statValue} ${styles.red}`}>{result.stats.negated_count}</div>
                <div className={styles.statLabel}>Entités niées (NegEx)</div>
              </div>
            </div>

            {/* ORDO Card */}
            {result.ordo_candidates?.length > 0 && (
              <div className={styles.ordoCard}>
                <div className={styles.cardHeader} style={{ color: "rgba(56, 189, 248, 0.7)" }}>
                  Maladie rare candidate (ORDO)
                </div>
                <div className={styles.ordoName}>
                  {result.ordo_candidates[0].name_fr || result.ordo_candidates[0].name}
                </div>
                <div className={styles.ordoScore}>
                  Score de correspondance : {(result.ordo_candidates[0].score * 100).toFixed(1)}%
                </div>
                <div className={styles.ordoDetail}>
                  {result.ordo_candidates[0].matched_hpo || 0}/{result.ordo_candidates[0].total_hpo || 0} phénotypes concordants
                </div>
              </div>
            )}

            {/* Other ORDO candidates */}
            {result.ordo_candidates?.length > 1 && (
              <div className={styles.card}>
                <div className={styles.cardHeader}>Autres candidats</div>
                {result.ordo_candidates.slice(1, 4).map((c, i) => (
                  <div key={i} className={styles.ordoOther}>
                    {c.name_fr || c.name} — {(c.score * 100).toFixed(1)}%
                  </div>
                ))}
              </div>
            )}

            {/* Result Tabs */}
            <div className={styles.tabs}>
              {[
                { key: "entities", label: "Entités cliniques" },
                { key: "numerics", label: "Valeurs biologiques" },
                { key: "phenopacket", label: "Phenopacket (JSON)" },
                { key: "source", label: "Texte source" },
              ].map((t) => (
                <button
                  key={t.key}
                  className={`${styles.tabBtn} ${activeTab === t.key ? styles.tabBtnActive : ""}`}
                  onClick={() => setActiveTab(t.key)}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {/* Entities Tab */}
            {activeTab === "entities" && (
              <div className={styles.card} style={{ padding: 0, overflow: "auto", maxHeight: 500 }}>
                <table className={styles.dataTable}>
                  <thead>
                    <tr>
                      <th>Entité</th>
                      <th>Type</th>
                      <th>Statut</th>
                      <th>Code HPO</th>
                      <th>Terme HPO</th>
                      <th>Confiance</th>
                    </tr>
                  </thead>
                  <tbody>
                    {["problem", "treatment", "test"].flatMap((cat) =>
                      (result.entities?.[cat] || []).map((e, i) => (
                        <tr key={`${cat}-${i}`}>
                          <td>{(e.text || "").substring(0, 55)}</td>
                          <td>
                            <span className={`${styles.tag} ${styles[`tag${cat.charAt(0).toUpperCase() + cat.slice(1)}`]}`}>
                              {cat.toUpperCase()}
                            </span>
                            {e.negated && <span className={`${styles.tag} ${styles.tagNegated}`} style={{ marginLeft: 4 }}>NEG</span>}
                          </td>
                          <td>
                            <span className={`${styles.tag} ${e.matched ? styles.tagMatched : styles.tagUnmatched}`}>
                              {e.matched ? "HPO" : "--"}
                            </span>
                          </td>
                          <td style={{ fontFamily: "monospace", fontSize: "0.75rem" }}>{e.hpo_id || ""}</td>
                          <td>{e.hpo_name || ""}</td>
                          <td>{e.matched ? `${(e.confidence * 100).toFixed(0)}%` : ""}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {/* Numerics Tab */}
            {activeTab === "numerics" && (
              <div className={styles.card} style={{ padding: 0, overflow: "auto", maxHeight: 500 }}>
                {result.numerics?.length > 0 ? (
                  <table className={styles.dataTable}>
                    <thead>
                      <tr>
                        <th>Phénotype</th>
                        <th>Code HPO</th>
                        <th>Valeur brute</th>
                        <th>Interprétation</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.numerics.map((n, i) => (
                        <tr key={i}>
                          <td>{n.phenotype || ""}</td>
                          <td style={{ fontFamily: "monospace" }}>{n.hpo_id || ""}</td>
                          <td>{n.raw_value || ""}</td>
                          <td>{n.interpretation || ""}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <div className={styles.emptyState}>
                    <div className={styles.emptyText}>Aucune valeur biologique anormale détectée</div>
                  </div>
                )}
              </div>
            )}

            {/* Phenopacket Tab */}
            {activeTab === "phenopacket" && (
              <div>
                <div
                  className={styles.jsonBlock}
                  dangerouslySetInnerHTML={{ __html: syntaxHighlight(result.phenopacket) }}
                />
                <button className={styles.btnSecondary} onClick={downloadPhenopacket} style={{ marginTop: "1rem" }}>
                  <ArrowDownTrayIcon size={15} style={{ verticalAlign: "middle", marginRight: 5 }} /> Télécharger le Phenopacket
                </button>
              </div>
            )}

            {/* Source Tab */}
            {activeTab === "source" && (
              <div className={styles.card}>
                <div className={styles.cardHeader}>
                  Texte clinique extrait ({result.char_count?.toLocaleString()} caractères)
                </div>
                <div className={styles.textContent}>{result.source_text}</div>
              </div>
            )}

            {/* Footer */}
            <hr className={styles.divider} />
            <div className={styles.footer}>
              <span>Temps : {result.processing_time}s</span>
              <span>DeBERTa-v3 + GLiNER + SapBERT + NegEx | Bilingue FR/EN</span>
              <span>GA4GH Phenopackets (ISO 4454:2022)</span>
            </div>
          </div>
        )}
      </div>

      {/* ═══ Sidebar ═══ */}
      <div>
        <div className={styles.card}>
          <div className={styles.cardHeader}>Architecture du pipeline</div>
          <div className={styles.pipelineSteps}>
            {stepNames.map((name, i) => (
              <div key={i} className={styles.pipelineStep}>
                <div className={`${styles.stepNum} ${getStepClass(stepStatuses[i])}`}>{i + 1}</div>
                <div className={`${styles.stepText} ${stepStatuses[i] === 0 ? styles.dim : ""}`}>{name}</div>
              </div>
            ))}
          </div>
        </div>

        <div className={styles.card} style={{ marginTop: "1rem" }}>
          <div className={styles.cardHeader}>Statut du pipeline</div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div
              style={{
                width: 8, height: 8, borderRadius: "50%",
                background: isAnalyzing ? "var(--accent-amber)" : result ? "var(--accent-green)" : "var(--text-dim)",
              }}
            />
            <span style={{ color: "var(--text-secondary)", fontSize: "0.8rem" }}>
              {isAnalyzing ? "Analyse en cours..." : result ? "Analyse terminée" : "En attente"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
