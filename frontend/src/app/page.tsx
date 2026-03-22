import Link from "next/link";

import { Navbar } from "@/components/Navbar";

export default function LandingPage() {
  return (
    <main className="screen backdrop">
      <Navbar compact />
      <section className="hero glass">
        <h1>Welcome To Dialogus</h1>
        <p>Explore ideas and discuss literature with an AI powered platform.</p>
        <div className="hero-actions">
          <Link href="/login" className="action-btn">Log In</Link>
          <Link href="/signup" className="action-btn">Sign Up</Link>
        </div>
      </section>
    </main>
  );
}
