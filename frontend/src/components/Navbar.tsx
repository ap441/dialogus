"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { MouseEvent as ReactMouseEvent, useState, useEffect, useRef } from "react";
import { ApiError, getNotifications, markAllNotificationsRead, markNotificationRead, NotificationItem, searchUsers, ProfileData } from "@/lib/api";

type Props = {
  compact?: boolean;
};

export function Navbar({ compact = false }: Props) {
  const router = useRouter();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [userName, setUserName] = useState<string | null>(null);
  const [userRole, setUserRole] = useState<string>("member");
  const [userAvatar, setUserAvatar] = useState<string | null>(null);
  const [isSignedIn, setIsSignedIn] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notificationsLoading, setNotificationsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<ProfileData[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const notificationsRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const token = localStorage.getItem("dialogus_token");
    const name = localStorage.getItem("userName");
    const role = localStorage.getItem("userRole") || "member";
    const avatar = localStorage.getItem("userAvatar");
    const email = localStorage.getItem("userEmail");
    setIsSignedIn(Boolean(token));
    if (token && email) {
      setUserEmail(email);
    }
    if (name) {
      setUserName(name);
    }
    if (avatar) {
      setUserAvatar(avatar);
    }
    setUserRole(role);
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
      if (searchRef.current && !searchRef.current.contains(target)) {
        setIsSearching(false);
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
    localStorage.removeItem("userName");
    localStorage.removeItem("userRole");
    localStorage.removeItem("userAvatar");
    setIsSignedIn(false);
    setUserEmail(null);
    setUserName(null);
    setUserRole("member");
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

  const displayName = userName || userEmail || "Profile";
  const initialsSource = userName || userEmail || "?";

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
        <div className="navbar-search" ref={searchRef}>
          <div className="search-input-wrapper">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="search-icon"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            <input 
              type="text" 
              placeholder="Search users..." 
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                if (e.target.value.length > 0) {
                  searchUsers(e.target.value).then(setSearchResults).catch(() => {});
                } else {
                  setSearchResults([]);
                }
              }}
              onFocus={() => setIsSearching(true)}
            />
          </div>
          {isSearching && searchQuery && (
             <div className="search-dropdown">
               {searchResults.length > 0 ? (
                 searchResults.map(user => (
                   <Link key={user.id} href={`/users/${user.id}`} className="search-item" onClick={() => { setIsSearching(false); setSearchQuery(''); }}>
                     {user.avatar_url ? <img src={user.avatar_url} className="search-avatar-img" alt="" /> : <div className="search-avatar initials">{getInitials(user.full_name || user.email)}</div>}
                     <div className="search-info">
                       <strong>{user.full_name}</strong>
                       <small>@{user.email.split('@')[0]}</small>
                     </div>
                   </Link>
                 ))
               ) : (
                 <div className="search-empty">No users found.</div>
               )}
             </div>
          )}
        </div>

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
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
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
        <button className="icon-btn" title="Settings" aria-label="Settings" onClick={() => router.push(isSignedIn ? "/profile" : "/login")}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
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
            title={displayName}
          >
            {userAvatar ? (
              <img src={userAvatar} alt="Profile" className="profile-avatar-img" />
            ) : (
              <div className="profile-avatar">{getInitials(initialsSource)}</div>
            )}
          </button>

          {dropdownOpen && (
            <div className="dropdown-menu">
              <div className="dropdown-header">
                <div>{displayName}</div>
                <small>{userRole === "admin" ? "Admin" : "Member"}</small>
              </div>
              <Link href="/profile" className="dropdown-item" onClick={() => setDropdownOpen(false)}>
                Profile
              </Link>
              {userRole === "admin" ? (
                <Link href="/admin" className="dropdown-item" onClick={() => setDropdownOpen(false)}>
                  Admin Dashboard
                </Link>
              ) : null}
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
