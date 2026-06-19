"use client";
import { useState, useEffect } from "react";
import { supabase } from "@/lib/supabase";
import styles from "./page.module.css";
import PipelineView from "@/components/PipelineView";
import DossiersView from "@/components/DossiersView";
import LoginPage from "@/components/LoginPage";

export default function Home() {
  const [activeView, setActiveView] = useState("dossiers");
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

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

  // Loading state
  if (authLoading) {
    return (
      <div className={styles.loadingScreen}>
        <div className={styles.loadingLogo}>🧬</div>
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
      <header className={styles.topBar}>
        <div className={styles.topBarInner}>
          <div className={styles.brandGroup}>
            <div className={styles.brandLogo}>
              <span className={styles.logoIcon}>🧬</span>
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
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
              Dossiers
            </button>
            <button
              className={`${styles.navTab} ${activeView === "pipeline" ? styles.navTabActive : ""}`}
              onClick={() => setActiveView("pipeline")}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
              Pipeline
            </button>
          </nav>

          <div className={styles.navRight}>
            <div className={styles.userInfo}>
              <div className={styles.userAvatar}>
                {user.user_metadata?.full_name?.[0] || user.email?.[0]?.toUpperCase() || "U"}
              </div>
              <span className={styles.userEmail}>{user.email}</span>
            </div>
            <button className={styles.logoutBtn} onClick={handleLogout} title="Se déconnecter">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
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
