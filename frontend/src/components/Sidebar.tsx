import Link from "next/link";

const items = [
  "Trending",
  "My Discussions",
  "Saved Books",
  "Recommendations",
  "Topics",
  "Settings"
];

export function Sidebar() {
  return (
    <aside className="sidebar glass">
      {items.map((item) => (
        <Link key={item} href="/home" className="sidebar-item">
          {item}
        </Link>
      ))}
    </aside>
  );
}
