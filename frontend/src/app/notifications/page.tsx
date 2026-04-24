"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { Navbar } from "@/components/Navbar";
import { Sidebar } from "@/components/Sidebar";
import { ApiError, getNotifications, markAllNotificationsRead, markNotificationRead, NotificationItem } from "@/lib/api";

export default function NotificationsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("dialogus_token");
    if (!token) {
      router.replace("/login");
      return;
    }

    let mounted = true;

    async function loadNotifications() {
      try {
        setLoading(true);
        const result = await getNotifications(50);
        if (mounted) {
          setNotifications(result.notifications);
          setUnreadCount(result.unread_count);
          setError("");
        }
      } catch (err) {
        if (mounted) {
          if (err instanceof ApiError && err.status === 401) {
            localStorage.removeItem("dialogus_token");
            localStorage.removeItem("userEmail");
            router.replace("/login");
            return;
          }
          setError(err instanceof Error ? err.message : "Failed to load notifications");
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadNotifications();
    return () => {
      mounted = false;
    };
  }, [router]);

  const handleMarkRead = async (notification: NotificationItem) => {
    try {
      await markNotificationRead(notification.id);
      setNotifications((current) => current.map((item) => (item.id === notification.id ? { ...item, is_read: true } : item)));
      setUnreadCount((current) => Math.max(0, current - 1));
      if (notification.link) {
        router.push(notification.link);
      }
    } catch {
      if (notification.link) {
        router.push(notification.link);
      }
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllNotificationsRead();
      setNotifications((current) => current.map((item) => ({ ...item, is_read: true })));
      setUnreadCount(0);
    } catch {
      // best effort
    }
  };

  return (
    <main className="screen backdrop">
      <Navbar />
      <section className="app-layout">
        <Sidebar />
        <div className="content-column">
          <section className="glass panel notifications-panel">
            <div className="notifications-header">
              <div>
                <h2>Notifications</h2>
                <p>{unreadCount} unread</p>
              </div>
              <button type="button" className="text-btn" onClick={handleMarkAllRead}>
                Mark all read
              </button>
            </div>

            {loading ? <p>Loading notifications...</p> : null}
            {error ? <p className="error-text">{error}</p> : null}

            <div className="notifications-list">
              {!loading && notifications.length === 0 ? <p className="notification-empty">No notifications yet.</p> : null}

              {notifications.map((notification) => (
                <button
                  key={notification.id}
                  type="button"
                  className={`notification-row ${notification.is_read ? "read" : "unread"}`}
                  onClick={() => handleMarkRead(notification)}
                >
                  <div className="notification-row-body">
                    <div className="notification-item-title">{notification.title}</div>
                    <div className="notification-item-message">{notification.message}</div>
                    <div className="notification-item-meta">
                      <span>{notification.actor_name || "Dialogus"}</span>
                      <span>{new Date(notification.created_at).toLocaleString()}</span>
                    </div>
                  </div>
                  <span className="notification-row-chevron">›</span>
                </button>
              ))}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
