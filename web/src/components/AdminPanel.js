"use client";
import { useState, useEffect, useCallback } from "react";
import { supabase } from "@/lib/supabase";
import styles from "./AdminPanel.module.css";
import {
  UserGroupIcon,
  PlusIcon,
  TrashIcon,
  XMarkIcon,
  CheckCircleIcon,
  ShieldCheckIcon,
  UserIcon,
  IdentificationIcon,
  CalendarDaysIcon,
} from "@/components/Icons";

export default function AdminPanel() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [creating, setCreating] = useState(false);
  const [toast, setToast] = useState(null);
  const [newUser, setNewUser] = useState({ email: "", password: "", full_name: "" });

  const showToast = (message, type = "info") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  };

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const { data, error } = await supabase
        .from("user_profiles")
        .select("*")
        .order("created_at", { ascending: true });
      if (error) throw error;
      setUsers(data || []);
    } catch (err) {
      showToast("Erreur: " + err.message, "error");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const handleCreateUser = async (e) => {
    e.preventDefault();
    if (!newUser.email || !newUser.password) {
      return showToast("Email et mot de passe requis", "error");
    }
    if (newUser.password.length < 6) {
      return showToast("Le mot de passe doit contenir au moins 6 caractères", "error");
    }
    setCreating(true);
    try {
      const { data, error } = await supabase.rpc("create_intern_user", {
        p_email: newUser.email,
        p_password: newUser.password,
        p_full_name: newUser.full_name || "",
      });
      if (error) throw error;
      showToast(`Compte créé pour ${newUser.email}`, "success");
      setNewUser({ email: "", password: "", full_name: "" });
      setShowCreateForm(false);
      fetchUsers();
    } catch (err) {
      showToast("Erreur: " + err.message, "error");
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteUser = async (user) => {
    if (user.role === "admin") {
      return showToast("Impossible de supprimer un admin", "error");
    }
    if (!confirm(`Supprimer le compte de ${user.email} ?`)) return;
    try {
      const { error } = await supabase.rpc("delete_intern_user", {
        p_user_id: user.id,
      });
      if (error) throw error;
      showToast(`Compte ${user.email} supprimé`, "success");
      fetchUsers();
    } catch (err) {
      showToast("Erreur: " + err.message, "error");
    }
  };

  const formatDate = (d) => {
    if (!d) return "—";
    return new Date(d).toLocaleDateString("fr-FR", {
      day: "2-digit", month: "short", year: "numeric",
    });
  };

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <div className={styles.headerIcon}>
            <UserGroupIcon size={20} />
          </div>
          <div>
            <h2 className={styles.headerTitle}>Gestion des Comptes</h2>
            <p className={styles.headerSub}>{users.length} utilisateur{users.length > 1 ? "s" : ""} enregistré{users.length > 1 ? "s" : ""}</p>
          </div>
        </div>
        <button
          className={styles.createBtn}
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          {showCreateForm ? (
            <><XMarkIcon size={15} /> Annuler</>
          ) : (
            <><PlusIcon size={15} /> Nouveau compte</>
          )}
        </button>
      </div>

      {/* Create Form */}
      {showCreateForm && (
        <form className={styles.createForm} onSubmit={handleCreateUser}>
          <h3 className={styles.formTitle}>
            <IdentificationIcon size={16} style={{ verticalAlign: "middle", marginRight: 6, opacity: 0.7 }} />
            Créer un compte interne
          </h3>
          <div className={styles.formGrid}>
            <div className={styles.formField}>
              <label className={styles.formLabel}>Nom complet</label>
              <input
                className={styles.formInput}
                type="text"
                placeholder="Dr. Nom Prénom"
                value={newUser.full_name}
                onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })}
              />
            </div>
            <div className={styles.formField}>
              <label className={styles.formLabel}>Email *</label>
              <input
                className={styles.formInput}
                type="email"
                placeholder="interne@clinicalpfe.dz"
                value={newUser.email}
                onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                required
              />
            </div>
            <div className={styles.formField}>
              <label className={styles.formLabel}>Mot de passe *</label>
              <input
                className={styles.formInput}
                type="password"
                placeholder="Minimum 6 caractères"
                value={newUser.password}
                onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                required
                minLength={6}
              />
            </div>
          </div>
          <div className={styles.formNote}>
            <ShieldCheckIcon size={13} style={{ verticalAlign: "middle", marginRight: 4, opacity: 0.6 }} />
            Le compte sera créé avec le rôle <strong>Interne</strong> — pas de permission de suppression
          </div>
          <button className={styles.submitBtn} type="submit" disabled={creating}>
            {creating ? (
              <><span className={styles.spinner} /> Création...</>
            ) : (
              <><CheckCircleIcon size={14} style={{ verticalAlign: "middle", marginRight: 4 }} /> Créer le compte</>
            )}
          </button>
        </form>
      )}

      {/* Users List */}
      <div className={styles.usersList}>
        {loading ? (
          <div className={styles.loadingState}>Chargement...</div>
        ) : users.length === 0 ? (
          <div className={styles.emptyState}>Aucun utilisateur</div>
        ) : (
          users.map((user) => (
            <div key={user.id} className={styles.userCard}>
              <div className={styles.userAvatar}>
                {user.role === "admin" ? (
                  <ShieldCheckIcon size={18} />
                ) : (
                  <UserIcon size={18} />
                )}
              </div>
              <div className={styles.userInfo}>
                <div className={styles.userNameRow}>
                  <span className={styles.userName}>
                    {user.full_name || user.email.split("@")[0]}
                  </span>
                  <span className={`${styles.roleBadge} ${user.role === "admin" ? styles.roleAdmin : styles.roleIntern}`}>
                    {user.role === "admin" ? "Admin" : "Interne"}
                  </span>
                </div>
                <span className={styles.userEmail}>{user.email}</span>
                <span className={styles.userDate}>
                  <CalendarDaysIcon size={11} style={{ verticalAlign: "middle", marginRight: 3, opacity: 0.5 }} />
                  Créé le {formatDate(user.created_at)}
                </span>
              </div>
              <div className={styles.userActions}>
                {user.role !== "admin" && (
                  <button
                    className={styles.deleteBtn}
                    onClick={() => handleDeleteUser(user)}
                    title="Supprimer ce compte"
                  >
                    <TrashIcon size={14} />
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

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
