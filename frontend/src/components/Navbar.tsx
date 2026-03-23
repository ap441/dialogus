"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { MouseEvent as ReactMouseEvent, useState, useEffect, useRef } from "react";

type Props = {
  compact?: boolean;
};

export function Navbar({ compact = false }: Props) {
  const router = useRouter();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [isSignedIn, setIsSignedIn] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

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
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("dialogus_token");
    localStorage.removeItem("userEmail");
    setIsSignedIn(false);
    setUserEmail(null);
    setDropdownOpen(false);
    router.push("/");
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
        <button className="icon-btn" title="Notifications" aria-label="Notifications">
          🔔
        </button>
        <button className="icon-btn" title="Search" aria-label="Search">
          ⌕
        </button>
        <button className="icon-btn" title="Settings" aria-label="Settings">
          ⚙
        </button>

        <div className="profile-dropdown" ref={dropdownRef}>
          <button
            className="profile-btn"
            onClick={() => (isSignedIn ? setDropdownOpen(!dropdownOpen) : router.push("/login"))}
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
