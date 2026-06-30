"use client";
import { useState, useEffect, useCallback } from "react";
import { supabase } from "@/lib/supabase";
import styles from "./DashboardView.module.css";
import {
  FolderIcon, ClipboardDocumentListIcon, UserGroupIcon,
  MapPinIcon, HeartIcon, CalendarDaysIcon, DnaIcon,
  IdentificationIcon, ShieldCheckIcon,
} from "@/components/Icons";

// ── Tiny SVG Chart Components ──────────────────────────

function DonutChart({ data, size = 160 }) {
  const total = data.reduce((s, d) => s + d.value, 0);
  if (!total) return null;
  const cx = size / 2, cy = size / 2, r = size / 2 - 12;
  let cumulative = 0;

  const segments = data.map((d, i) => {
    const pct = d.value / total;
    const start = cumulative * 2 * Math.PI - Math.PI / 2;
    cumulative += pct;
    const end = cumulative * 2 * Math.PI - Math.PI / 2;
    const large = pct > 0.5 ? 1 : 0;
    const x1 = cx + r * Math.cos(start), y1 = cy + r * Math.sin(start);
    const x2 = cx + r * Math.cos(end), y2 = cy + r * Math.sin(end);
    return (
      <path
        key={i}
        d={`M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2} Z`}
        fill={d.color}
        stroke="var(--bg-secondary)"
        strokeWidth="2"
        className={styles.donutSegment}
      >
        <title>{d.label}: {d.value} ({(pct * 100).toFixed(0)}%)</title>
      </path>
    );
  });

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      {segments}
      <circle cx={cx} cy={cy} r={r * 0.55} fill="var(--bg-secondary)" />
      <text x={cx} y={cy - 6} textAnchor="middle" className={styles.donutCenter}>{total}</text>
      <text x={cx} y={cy + 12} textAnchor="middle" className={styles.donutLabel}>total</text>
    </svg>
  );
}

function HBarChart({ data, maxItems = 8 }) {
  const sorted = [...data].sort((a, b) => b.value - a.value).slice(0, maxItems);
  const max = Math.max(...sorted.map(d => d.value), 1);
  return (
    <div className={styles.hbarList}>
      {sorted.map((d, i) => (
        <div key={i} className={styles.hbarItem}>
          <span className={styles.hbarLabel} title={d.label}>{d.label}</span>
          <div className={styles.hbarTrack}>
            <div
              className={styles.hbarFill}
              style={{ width: `${(d.value / max) * 100}%`, background: d.color || "var(--accent-cyan)", animationDelay: `${i * 0.05}s` }}
            />
          </div>
          <span className={styles.hbarValue}>{d.value}</span>
        </div>
      ))}
    </div>
  );
}

function SparkArea({ data, width = 320, height = 100, color = "var(--accent-cyan)" }) {
  if (!data.length) return null;
  const max = Math.max(...data.map(d => d.value), 1);
  const padX = 0, padY = 10;
  const w = width - padX * 2, h = height - padY * 2;
  const points = data.map((d, i) => ({
    x: padX + (i / (data.length - 1 || 1)) * w,
    y: padY + h - (d.value / max) * h,
  }));
  const line = points.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");
  const area = `${line} L ${points[points.length - 1].x} ${height} L ${points[0].x} ${height} Z`;

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} className={styles.sparkSvg}>
      <defs>
        <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.25" />
          <stop offset="100%" stopColor={color} stopOpacity="0.02" />
        </linearGradient>
      </defs>
      <path d={area} fill="url(#areaGrad)" />
      <path d={line} fill="none" stroke={color} strokeWidth="2" strokeLinejoin="round" className={styles.sparkLine} />
      {points.map((p, i) => (
        <g key={i}>
          <circle cx={p.x} cy={p.y} r="3.5" fill="var(--bg-secondary)" stroke={color} strokeWidth="1.5" className={styles.sparkDot} />
          <title>{data[i].label}: {data[i].value}</title>
        </g>
      ))}
    </svg>
  );
}

// ── Colors ──
const COLORS = [
  "#38bdf8", "#a78bfa", "#34d399", "#fb923c", "#f87171",
  "#facc15", "#2dd4bf", "#e879f9", "#60a5fa", "#4ade80",
];

export default function DashboardView() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = useCallback(async () => {
    setLoading(true);
    try {
      const [dossiersRes, reportsRes] = await Promise.all([
        supabase.from("patient_dossiers").select("*"),
        supabase.from("medical_reports").select("id, created_at, filename, patient_name, dossier_id"),
      ]);

      const dossiers = dossiersRes.data || [];
      const reports = reportsRes.data || [];

      // Summary
      const totalDossiers = dossiers.length;
      const totalReports = reports.length;
      const uniqueDiagnoses = new Set(dossiers.map(d => d.principal_diagnosis).filter(Boolean)).size;
      const uniqueCities = new Set(dossiers.map(d => d.origin).filter(Boolean)).size;
      const avgReportsPerDossier = totalDossiers ? (totalReports / totalDossiers).toFixed(1) : 0;
      const withDossierNum = dossiers.filter(d => d.dossier_number).length;

      // Gender distribution
      const genderMap = {};
      dossiers.forEach(d => {
        const g = d.gender === "M" ? "Masculin" : d.gender === "F" ? "Féminin" : "Inconnu";
        genderMap[g] = (genderMap[g] || 0) + 1;
      });
      const genderData = Object.entries(genderMap).map(([label, value], i) => ({
        label, value, color: label === "Masculin" ? "#38bdf8" : label === "Féminin" ? "#e879f9" : "#64748b",
      }));

      // Diagnosis distribution
      const diagMap = {};
      dossiers.forEach(d => {
        if (d.principal_diagnosis) {
          // Simplify diagnosis names
          let diag = d.principal_diagnosis;
          if (diag.length > 35) diag = diag.substring(0, 35) + "…";
          diagMap[diag] = (diagMap[diag] || 0) + 1;
        }
      });
      const diagData = Object.entries(diagMap)
        .map(([label, value], i) => ({ label, value, color: COLORS[i % COLORS.length] }));

      // City distribution
      const cityMap = {};
      dossiers.forEach(d => {
        if (d.origin) cityMap[d.origin] = (cityMap[d.origin] || 0) + 1;
      });
      const cityData = Object.entries(cityMap)
        .map(([label, value], i) => ({ label, value, color: COLORS[(i + 3) % COLORS.length] }));

      // Monthly trend (last 6 months)
      const monthNames = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"];
      const now = new Date();
      const monthlyData = [];
      for (let i = 5; i >= 0; i--) {
        const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
        const month = d.getMonth();
        const year = d.getFullYear();
        const count = reports.filter(r => {
          const rd = new Date(r.created_at);
          return rd.getMonth() === month && rd.getFullYear() === year;
        }).length;
        monthlyData.push({ label: `${monthNames[month]} ${year.toString().slice(-2)}`, value: count });
      }

      // Doctor distribution
      const doctorMap = {};
      dossiers.forEach(d => {
        if (d.treating_doctor) {
          doctorMap[d.treating_doctor] = (doctorMap[d.treating_doctor] || 0) + 1;
        }
      });
      const doctorData = Object.entries(doctorMap)
        .map(([label, value], i) => ({ label: `Dr. ${label}`, value, color: COLORS[(i + 5) % COLORS.length] }));

      // Age distribution
      const ageGroups = { "0-1 an": 0, "1-3 ans": 0, "3-6 ans": 0, "6-12 ans": 0, "12+ ans": 0 };
      dossiers.forEach(d => {
        if (d.age) {
          const numMatch = d.age.match(/(\d+)/);
          if (numMatch) {
            const n = parseInt(numMatch[1]);
            const isMois = /mois/i.test(d.age);
            const ageYears = isMois ? n / 12 : n;
            if (ageYears < 1) ageGroups["0-1 an"]++;
            else if (ageYears < 3) ageGroups["1-3 ans"]++;
            else if (ageYears < 6) ageGroups["3-6 ans"]++;
            else if (ageYears < 12) ageGroups["6-12 ans"]++;
            else ageGroups["12+ ans"]++;
          }
        }
      });
      const ageData = Object.entries(ageGroups)
        .filter(([, v]) => v > 0)
        .map(([label, value], i) => ({ label, value, color: COLORS[(i + 1) % COLORS.length] }));

      // Recent dossiers
      const recentDossiers = [...dossiers]
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 5);

      setStats({
        totalDossiers, totalReports, uniqueDiagnoses, uniqueCities,
        avgReportsPerDossier, withDossierNum,
        genderData, diagData, cityData, monthlyData,
        doctorData, ageData, recentDossiers,
      });
    } catch (err) {
      console.error("Dashboard error:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchStats(); }, [fetchStats]);

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner} />
        <span>Chargement du tableau de bord...</span>
      </div>
    );
  }

  if (!stats) return null;

  const formatDate = (d) => new Date(d).toLocaleDateString("fr-FR", { day: "2-digit", month: "short" });

  return (
    <div className={styles.container}>
      {/* ═══ Summary Cards ═══ */}
      <div className={styles.summaryGrid}>
        <div className={styles.summaryCard}>
          <div className={`${styles.summaryIcon} ${styles.iconCyan}`}><FolderIcon size={20} /></div>
          <div className={styles.summaryData}>
            <span className={styles.summaryValue}>{stats.totalDossiers}</span>
            <span className={styles.summaryLabel}>Dossiers</span>
          </div>
        </div>
        <div className={styles.summaryCard}>
          <div className={`${styles.summaryIcon} ${styles.iconPurple}`}><ClipboardDocumentListIcon size={20} /></div>
          <div className={styles.summaryData}>
            <span className={styles.summaryValue}>{stats.totalReports}</span>
            <span className={styles.summaryLabel}>Rapports</span>
          </div>
        </div>
        <div className={styles.summaryCard}>
          <div className={`${styles.summaryIcon} ${styles.iconGreen}`}><HeartIcon size={20} /></div>
          <div className={styles.summaryData}>
            <span className={styles.summaryValue}>{stats.uniqueDiagnoses}</span>
            <span className={styles.summaryLabel}>Diagnostics</span>
          </div>
        </div>
        <div className={styles.summaryCard}>
          <div className={`${styles.summaryIcon} ${styles.iconOrange}`}><MapPinIcon size={20} /></div>
          <div className={styles.summaryData}>
            <span className={styles.summaryValue}>{stats.uniqueCities}</span>
            <span className={styles.summaryLabel}>Villes</span>
          </div>
        </div>
        <div className={styles.summaryCard}>
          <div className={`${styles.summaryIcon} ${styles.iconRed}`}><DnaIcon size={20} /></div>
          <div className={styles.summaryData}>
            <span className={styles.summaryValue}>{stats.avgReportsPerDossier}</span>
            <span className={styles.summaryLabel}>Rapp./Dossier</span>
          </div>
        </div>
        <div className={styles.summaryCard}>
          <div className={`${styles.summaryIcon} ${styles.iconTeal}`}><IdentificationIcon size={20} /></div>
          <div className={styles.summaryData}>
            <span className={styles.summaryValue}>{stats.withDossierNum}</span>
            <span className={styles.summaryLabel}>Avec N° dossier</span>
          </div>
        </div>
      </div>

      {/* ═══ Charts Grid ═══ */}
      <div className={styles.chartsGrid}>

        {/* Monthly Trend */}
        <div className={`${styles.chartCard} ${styles.chartWide}`}>
          <h3 className={styles.chartTitle}>
            <CalendarDaysIcon size={15} style={{ opacity: 0.6 }} />
            Rapports par mois
          </h3>
          <div className={styles.chartBody}>
            <SparkArea data={stats.monthlyData} width={480} height={120} />
            <div className={styles.sparkLabels}>
              {stats.monthlyData.map((d, i) => (
                <span key={i} className={styles.sparkLabel}>{d.label}</span>
              ))}
            </div>
          </div>
        </div>

        {/* Gender Donut */}
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>
            <UserGroupIcon size={15} style={{ opacity: 0.6 }} />
            Répartition par sexe
          </h3>
          <div className={styles.chartBodyCenter}>
            <DonutChart data={stats.genderData} size={140} />
            <div className={styles.legend}>
              {stats.genderData.map((d, i) => (
                <div key={i} className={styles.legendItem}>
                  <span className={styles.legendDot} style={{ background: d.color }} />
                  <span className={styles.legendLabel}>{d.label}</span>
                  <span className={styles.legendValue}>{d.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Diagnosis Distribution */}
        <div className={`${styles.chartCard} ${styles.chartWide}`}>
          <h3 className={styles.chartTitle}>
            <HeartIcon size={15} style={{ opacity: 0.6 }} />
            Distribution des diagnostics
          </h3>
          <div className={styles.chartBody}>
            <HBarChart data={stats.diagData} maxItems={8} />
          </div>
        </div>

        {/* Age Distribution */}
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>
            <ShieldCheckIcon size={15} style={{ opacity: 0.6 }} />
            Tranches d'âge
          </h3>
          <div className={styles.chartBodyCenter}>
            <DonutChart data={stats.ageData} size={140} />
            <div className={styles.legend}>
              {stats.ageData.map((d, i) => (
                <div key={i} className={styles.legendItem}>
                  <span className={styles.legendDot} style={{ background: d.color }} />
                  <span className={styles.legendLabel}>{d.label}</span>
                  <span className={styles.legendValue}>{d.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* City Distribution */}
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>
            <MapPinIcon size={15} style={{ opacity: 0.6 }} />
            Patients par ville
          </h3>
          <div className={styles.chartBody}>
            <HBarChart data={stats.cityData} maxItems={6} />
          </div>
        </div>

        {/* Doctor Distribution */}
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>
            <HeartIcon size={15} style={{ opacity: 0.6 }} />
            Patients par médecin
          </h3>
          <div className={styles.chartBody}>
            <HBarChart data={stats.doctorData} maxItems={6} />
          </div>
        </div>

        {/* Recent Dossiers */}
        <div className={`${styles.chartCard} ${styles.chartWide}`}>
          <h3 className={styles.chartTitle}>
            <FolderIcon size={15} style={{ opacity: 0.6 }} />
            Derniers dossiers ajoutés
          </h3>
          <div className={styles.recentList}>
            {stats.recentDossiers.map((d, i) => (
              <div key={d.id} className={styles.recentItem}>
                <div className={styles.recentRank}>{i + 1}</div>
                <div className={styles.recentInfo}>
                  <span className={styles.recentName}>{d.full_name}</span>
                  <span className={styles.recentMeta}>
                    {d.principal_diagnosis || "—"} · {d.age || "?"} · {d.origin || "—"}
                  </span>
                </div>
                {d.dossier_number && (
                  <span className={styles.recentBadge}>N°{d.dossier_number}</span>
                )}
                <span className={styles.recentDate}>{formatDate(d.created_at)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
