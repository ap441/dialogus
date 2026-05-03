"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type Item = {
  label: string;
  href: string;
};

export function Sidebar() {
  const [role, setRole] = useState<string>("member");

  useEffect(() => {
    const storedRole = localStorage.getItem("userRole") || "member";
    setRole(storedRole);
  }, []);

  const items: Item[] = [
    { label: "Home", href: "/home" },
    { label: "Browse", href: "/browse" },
    { label: "Notifications", href: "/notifications" },
    { label: "My Profile", href: "/profile" },
  ];

  if (role === "admin") {
    items.push({ label: "Admin Dashboard", href: "/admin" });
  }

  return (
    <aside className="sidebar glass">
      {items.map((item) => (
        <Link key={item.href} href={item.href} className="sidebar-item">
          {item.label}
        </Link>
      ))}
    </aside>
  );
}
