"use client";
import { useState, useEffect } from "react";
import { supabase } from "@/lib/supabase";
import styles from "./page.module.css";
import PipelineView from "@/components/PipelineView";
import DossiersView from "@/components/DossiersView";
import LoginPage from "@/components/LoginPage";
import {
  DnaIcon,
  FolderIcon,
  BoltIcon,
  ArrowRightStartOnRectangleIcon,
  SunIcon,
  MoonIcon,
} from "@/components/Icons";

export default function Home() {
  const [activeView, setActiveView] = useState("dossiers");
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [theme, setTheme] = useState("dark");
  const [scrolled, setScrolled] = useState(false);

  // Track scroll for navbar effect
  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Initialize theme from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("clinicalpfe-theme") || "dark";
    setTheme(saved);
    document.documentElement.setAttribute("data-theme", saved);
  }, []);

  // Check for existing session on load
  useEffect(() => {
    const checkSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setUser(session?.user || null);
      setAuthLoading(false);
    };
    checkSession();

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user || null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setUser(null);
  };

  const toggleTheme = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("clinicalpfe-theme", next);
  };

  // Loading state
  if (authLoading) {
    return (
      <div className={styles.loadingScreen}>
        <div className={styles.loadingLogo}>
          <DnaIcon size={36} style={{ color: "var(--accent-cyan)" }} />
        </div>
        <div className={styles.loadingSpinner}></div>
      </div>
    );
  }

  // Not authenticated → show login
  if (!user) {
    return <LoginPage onLogin={(u) => setUser(u)} />;
  }

  // Authenticated → show app
  return (
    <div className={styles.appShell}>
      {/* ═══ Top Nav Bar ═══ */}
      <header className={`${styles.topBar} ${scrolled ? styles.topBarScrolled : ""}`}>
        <div className={styles.topBarInner}>
          <div className={styles.brandGroup}>
            <div className={styles.brandLogo}>
              <DnaIcon size={18} style={{ color: "#fff" }} />
            </div>
            <div>
              <h1 className={styles.brandName}>ClinicalPFE</h1>
              <p className={styles.brandSub}>Pré-analyse clinique intelligente</p>
            </div>
          </div>

          <nav className={styles.navTabs}>
            <button
              className={`${styles.navTab} ${activeView === "dossiers" ? styles.navTabActive : ""}`}
              onClick={() => setActiveView("dossiers")}
            >
              <FolderIcon size={16} />
              Dossiers
            </button>
            <button
              className={`${styles.navTab} ${activeView === "pipeline" ? styles.navTabActive : ""}`}
              onClick={() => setActiveView("pipeline")}
            >
              <BoltIcon size={16} />
              Pipeline
            </button>
          </nav>

          <div className={styles.navRight}>
            <button className={styles.themeToggle} onClick={toggleTheme} title={theme === "dark" ? "Mode clair" : "Mode sombre"}>
              {theme === "dark" ? <SunIcon size={16} /> : <MoonIcon size={16} />}
            </button>
            <div className={styles.userInfo}>
              <div className={styles.userAvatar}>
                {user.user_metadata?.full_name?.[0] || user.email?.[0]?.toUpperCase() || "U"}
              </div>
              <span className={styles.userEmail}>{user.email}</span>
            </div>
            <button className={styles.logoutBtn} onClick={handleLogout} title="Se déconnecter">
              <ArrowRightStartOnRectangleIcon size={16} />
              <span className={styles.logoutLabel}>Déconnexion</span>
            </button>
          </div>
        </div>
      </header>

      {/* ═══ Main Content ═══ */}
      <main className={styles.mainContent}>
        {activeView === "dossiers" && <DossiersView />}
        {activeView === "pipeline" && <PipelineView />}
      </main>
    </div>
  );
}
