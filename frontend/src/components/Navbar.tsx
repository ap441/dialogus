"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { MouseEvent as ReactMouseEvent, useState, useEffect, useRef } from "react";
import { ApiError, getNotifications, markAllNotificationsRead, markNotificationRead, NotificationItem } from "@/lib/api";

type Props = {
  compact?: boolean;
};

export function Navbar({ compact = false }: Props) {
  const router = useRouter();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [isSignedIn, setIsSignedIn] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notificationsLoading, setNotificationsLoading] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const notificationsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const token = localStorage.getItem("dialogus_token");
    const email = localStorage.getItem("userEmail");
    setIsSignedIn(Boolean(token));
    if (token && email) {
      setUserEmail(email);
    }
  }, []);

  useEffect(() => {
    // Close dropdown when clicking outside
    function handleClickOutside(event: globalThis.MouseEvent) {
      const target = event.target as Node;
      if (dropdownRef.current && !dropdownRef.current.contains(target)) {
        setDropdownOpen(false);
      }
      if (notificationsRef.current && !notificationsRef.current.contains(target)) {
        setNotificationsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (!isSignedIn || !notificationsOpen) {
      return;
    }

    let mounted = true;

    async function loadNotifications() {
      try {
        setNotificationsLoading(true);
        const result = await getNotifications(6);
        if (mounted) {
          setNotifications(result.notifications);
          setUnreadCount(result.unread_count);
        }
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          localStorage.removeItem("dialogus_token");
          localStorage.removeItem("userEmail");
          router.push("/login");
        }
      } finally {
        if (mounted) {
          setNotificationsLoading(false);
        }
      }
    }

    loadNotifications();
    return () => {
      mounted = false;
    };
  }, [isSignedIn, notificationsOpen, router]);

  const handleLogout = () => {
    localStorage.removeItem("dialogus_token");
    localStorage.removeItem("userEmail");
    setIsSignedIn(false);
    setUserEmail(null);
    setDropdownOpen(false);
    setNotificationsOpen(false);
    router.push("/");
  };

  const handleNotificationClick = async (notification: NotificationItem) => {
    try {
      await markNotificationRead(notification.id);
      setNotifications((current) => current.map((item) => (item.id === notification.id ? { ...item, is_read: true } : item)));
      setUnreadCount((current) => Math.max(0, current - 1));
      setNotificationsOpen(false);
      if (notification.link) {
        router.push(notification.link);
      }
    } catch {
      // Keep the dropdown usable even if mark-read fails.
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
      // no-op; best effort
    }
  };

  const handleProtectedNav = (event: ReactMouseEvent<HTMLAnchorElement>) => {
    if (isSignedIn) {
      return;
    }
    event.preventDefault();
    router.push("/login");
    return;
  };

  const getInitials = (email: string) => {
    return email.substring(0, 2).toUpperCase();
  };

  return (
    <header className={`topbar ${compact ? "compact" : ""}`.trim()}>
      <Link href="/" className="brand">
        Dialogus
      </Link>

      <nav className="nav-links">
        <Link href="/home" className="nav-link" onClick={handleProtectedNav}>
          Home
        </Link>
        <Link href="/browse" className="nav-link" onClick={handleProtectedNav}>
          Browse
        </Link>
      </nav>

      <div className="navbar-spacer"></div>

      <div className="navbar-actions">
        <div className="notification-dropdown" ref={notificationsRef}>
          <button
            className="icon-btn notification-trigger"
            title="Notifications"
            aria-label="Notifications"
            onClick={() => {
              if (!isSignedIn) {
                router.push("/login");
                return;
              }
              setDropdownOpen(false);
              setNotificationsOpen(!notificationsOpen);
            }}
          >
            🔔
            {unreadCount > 0 ? <span className="notification-badge">{unreadCount}</span> : null}
          </button>

          {notificationsOpen ? (
            <div className="notification-menu">
              <div className="notification-menu-header">
                <span>Notifications</span>
                <button type="button" className="text-btn" onClick={handleMarkAllRead}>
                  Mark all read
                </button>
              </div>

              <div className="notification-menu-list">
                {notificationsLoading ? <p className="notification-empty">Loading notifications...</p> : null}
                {!notificationsLoading && notifications.length === 0 ? (
                  <p className="notification-empty">No notifications yet.</p>
                ) : null}

                {notifications.map((notification) => (
                  <button
                    key={notification.id}
                    type="button"
                    className={`notification-item ${notification.is_read ? "read" : "unread"}`}
                    onClick={() => handleNotificationClick(notification)}
                  >
                    <div className="notification-item-title">{notification.title}</div>
                    <div className="notification-item-message">{notification.message}</div>
                    <div className="notification-item-meta">
                      {notification.actor_name ? <span>{notification.actor_name}</span> : <span>Dialogus</span>}
                      <span>{new Date(notification.created_at).toLocaleString()}</span>
                    </div>
                  </button>
                ))}
              </div>

              <div className="notification-menu-footer">
                <Link href="/notifications" className="text-btn" onClick={() => setNotificationsOpen(false)}>
                  View all notifications
                </Link>
              </div>
            </div>
          ) : null}
        </div>
        <button className="icon-btn" title="Search" aria-label="Search">
          ⌕
        </button>
        <button className="icon-btn" title="Settings" aria-label="Settings">
          ⚙
        </button>

        <div className="profile-dropdown" ref={dropdownRef}>
          <button
            className="profile-btn"
            onClick={() => {
              setNotificationsOpen(false);
              if (isSignedIn) {
                setDropdownOpen(!dropdownOpen);
              } else {
                router.push("/login");
              }
            }}
            title={userEmail || "Profile"}
          >
            <div className="profile-avatar">{userEmail ? getInitials(userEmail) : "?"}</div>
          </button>

          {dropdownOpen && (
            <div className="dropdown-menu">
              {userEmail && <div className="dropdown-header">{userEmail}</div>}
              <button onClick={handleLogout} className="dropdown-item logout-item">
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
