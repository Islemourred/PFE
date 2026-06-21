"use client";
import { useState } from "react";
import { supabase } from "@/lib/supabase";
import styles from "./LoginPage.module.css";
import {
  DnaIcon,
  EnvelopeIcon,
  LockClosedIcon,
  EyeIcon,
  EyeSlashIcon,
  XCircleIcon,
  ArrowLeftEndOnRectangleIcon,
  ShieldCheckIcon,
} from "@/components/Icons";

export default function LoginPage({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const { data, error: authError } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password,
      });

      if (authError) {
        if (authError.message.includes("Invalid login")) {
          setError("Email ou mot de passe incorrect");
        } else {
          setError(authError.message);
        }
        return;
      }

      if (data?.user) {
        onLogin(data.user);
      }
    } catch (err) {
      setError("Erreur de connexion: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.loginShell}>
      {/* Background decoration */}
      <div className={styles.bgOrb1}></div>
      <div className={styles.bgOrb2}></div>
      <div className={styles.bgOrb3}></div>

      <div className={styles.loginCard}>
        {/* Brand */}
        <div className={styles.brand}>
          <div className={styles.brandLogo}>
            <DnaIcon size={24} style={{ color: "#fff" }} />
          </div>
          <h1 className={styles.brandTitle}>ClinicalPFE</h1>
          <p className={styles.brandSub}>Système de pré-analyse clinique</p>
        </div>

        {/* Form */}
        <form className={styles.form} onSubmit={handleLogin}>
          <div className={styles.formGroup}>
            <label className={styles.label}>
              <EnvelopeIcon size={14} />
              Email
            </label>
            <input
              className={styles.input}
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@clinicalpfe.dz"
              required
              autoFocus
              autoComplete="email"
            />
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>
              <LockClosedIcon size={14} />
              Mot de passe
            </label>
            <div className={styles.passwordWrap}>
              <input
                className={styles.input}
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••"
                required
                autoComplete="current-password"
              />
              <button
                type="button"
                className={styles.togglePassword}
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
              >
                {showPassword ? (
                  <EyeSlashIcon size={16} />
                ) : (
                  <EyeIcon size={16} />
                )}
              </button>
            </div>
          </div>

          {error && (
            <div className={styles.error}>
              <XCircleIcon size={14} />
              {error}
            </div>
          )}

          <button className={styles.submitBtn} type="submit" disabled={loading || !email || !password}>
            {loading ? (
              <><div className={styles.spinner}></div> Connexion...</>
            ) : (
              <>
                <ArrowLeftEndOnRectangleIcon size={16} />
                Se connecter
              </>
            )}
          </button>
        </form>

        <div className={styles.footer}>
          <div className={styles.footerLock}>
            <ShieldCheckIcon size={12} />
            Connexion sécurisée via Supabase Auth
          </div>
        </div>
      </div>
    </div>
  );
}
