"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { Navbar } from "@/components/Navbar";
import { Sidebar } from "@/components/Sidebar";
import { ApiError, AdminDashboard, getAdminDashboard, NotificationItem, updateUserRole } from "@/lib/api";

const roleOptions: Array<"member" | "admin"> = ["member", "admin"];

export default function AdminPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [savingUserId, setSavingUserId] = useState<number | null>(null);
  const [dashboard, setDashboard] = useState<AdminDashboard | null>(null);
  const [draftRoles, setDraftRoles] = useState<Record<number, "member" | "admin">>({});
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("dialogus_token");
    if (!token) {
      router.replace("/login");
      return;
    }

    let mounted = true;

    async function load() {
      try {
        setLoading(true);
        const result = await getAdminDashboard();
        if (mounted) {
          setDashboard(result);
          setDraftRoles(
            Object.fromEntries(result.users.map((user) => [user.id, (user.role as "member" | "admin") ?? "member"]))
          );
        }
      } catch (err) {
        if (mounted) {
          if (err instanceof ApiError && err.status === 401) {
            localStorage.removeItem("dialogus_token");
            localStorage.removeItem("userEmail");
            localStorage.removeItem("userRole");
            router.replace("/login");
            return;
          }
          if (err instanceof ApiError && err.status === 403) {
            router.replace("/home");
            setError("Admin access required.");
            return;
          }
          setError(err instanceof Error ? err.message : "Failed to load admin dashboard");
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      mounted = false;
    };
  }, [router]);

  const activeUserCount = useMemo(() => dashboard?.users.length ?? 0, [dashboard]);

  const saveRole = async (userId: number) => {
    const nextRole = draftRoles[userId] ?? "member";
    try {
      setSavingUserId(userId);
      const updated = await updateUserRole(userId, nextRole);
      setDashboard((current) =>
        current
          ? {
              ...current,
              users: current.users.map((user) => (user.id === updated.id ? updated : user)),
            }
          : current
      );
      setSuccess(`Updated ${updated.full_name}'s role.`);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update role");
      setSuccess("");
    } finally {
      setSavingUserId(null);
    }
  };

  const renderNotification = (notification: NotificationItem) => (
    <article key={notification.id} className={`admin-activity-item ${notification.is_read ? "read" : "unread"}`}>
      <div>
        <strong>{notification.title}</strong>
        <p>{notification.message}</p>
      </div>
      <small>{new Date(notification.created_at).toLocaleString()}</small>
    </article>
  );

  return (
    <main className="screen backdrop">
      <Navbar />
      <section className="app-layout">
        <Sidebar />
        <div className="content-column">
          <section className="glass panel admin-hero">
            <div>
              <p className="thread-meta">Moderation center</p>
              <h2>Admin Dashboard</h2>
              <p>Manage users, review community activity, and keep the reading room running smoothly.</p>
            </div>
            <div className="admin-hero-badge">{activeUserCount} users</div>
          </section>

          {loading ? (
            <section className="glass panel">
              <p>Loading admin dashboard...</p>
            </section>
          ) : null}

          {error ? <section className="glass panel"><p className="error-text">{error}</p></section> : null}
          {success ? <section className="glass panel"><p className="success-text">{success}</p></section> : null}

          {dashboard ? (
            <>
              <section className="admin-stats-grid">
                {[
                  { label: "Users", value: dashboard.stats.total_users },
                  { label: "Admins", value: dashboard.stats.total_admins },
                  { label: "Books", value: dashboard.stats.total_books },
                  { label: "Discussions", value: dashboard.stats.total_discussions },
                  { label: "Replies", value: dashboard.stats.total_replies },
                  { label: "Unread notifications", value: dashboard.stats.unread_notifications },
                ].map((stat) => (
                  <article key={stat.label} className="glass admin-stat-card">
                    <strong>{stat.value}</strong>
                    <span>{stat.label}</span>
                  </article>
                ))}
              </section>

              <section className="glass panel">
                <div className="panel-header-row">
                  <h3>User management</h3>
                  <span>{dashboard.users.length} accounts</span>
                </div>
                <div className="admin-table">
                  {dashboard.users.map((user) => (
                    <div key={user.id} className="admin-user-row">
                      <div className="admin-user-main">
                        <div className="admin-avatar">{(user.avatar_url ? user.full_name : user.full_name).slice(0, 2).toUpperCase()}</div>
                        <div>
                          <strong>{user.full_name}</strong>
                          <p>{user.email}</p>
                          <small>
                            {user.discussion_count} discussions • {user.reply_count} replies • {user.unread_notification_count} unread
                          </small>
                        </div>
                      </div>
                      <div className="admin-user-actions">
                        <select
                          value={draftRoles[user.id] ?? user.role}
                          onChange={(event) =>
                            setDraftRoles((current) => ({
                              ...current,
                              [user.id]: event.target.value as "member" | "admin",
                            }))
                          }
                        >
                          {roleOptions.map((role) => (
                            <option key={role} value={role}>
                              {role}
                            </option>
                          ))}
                        </select>
                        <button type="button" className="action-btn small" disabled={savingUserId === user.id} onClick={() => saveRole(user.id)}>
                          {savingUserId === user.id ? "Saving..." : "Save role"}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              <section className="admin-content-grid">
                <article className="glass panel">
                  <div className="panel-header-row">
                    <h3>Recent discussions</h3>
                    <span>{dashboard.recent_discussions.length}</span>
                  </div>
                  <div className="admin-activity-list">
                    {dashboard.recent_discussions.map((discussion) => (
                      <div key={discussion.id} className="admin-activity-item">
                        <div>
                          <strong>{discussion.title}</strong>
                          <p>{discussion.book_title}</p>
                          <small>{discussion.replies} replies • {discussion.likes_count} likes</small>
                        </div>
                        <button type="button" className="text-btn" onClick={() => router.push(`/discussions/${discussion.id}`)}>
                          Open
                        </button>
                      </div>
                    ))}
                  </div>
                </article>

                <article className="glass panel">
                  <div className="panel-header-row">
                    <h3>Recent notifications</h3>
                    <span>{dashboard.recent_notifications.length}</span>
                  </div>
                  <div className="admin-activity-list">{dashboard.recent_notifications.map(renderNotification)}</div>
                </article>
              </section>
            </>
          ) : null}
        </div>
      </section>
    </main>
  );
}
