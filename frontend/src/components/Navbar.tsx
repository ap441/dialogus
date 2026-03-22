import Link from "next/link";

type Props = {
  compact?: boolean;
};

export function Navbar({ compact = false }: Props) {
  return (
    <header className={`topbar ${compact ? "compact" : ""}`.trim()}>
      <div className="brand">Dialogus</div>
      <nav className="nav-links">
        <Link href="/home">Home</Link>
        <Link href="/home">Browse</Link>
        <span aria-hidden>🔔</span>
        <span aria-hidden>⌕</span>
        <span aria-hidden>⚙</span>
        <span aria-hidden>◉</span>
      </nav>
    </header>
  );
}
