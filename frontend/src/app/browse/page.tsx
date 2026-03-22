"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { BookCard } from "@/components/BookCard";
import { Navbar } from "@/components/Navbar";
import { Sidebar } from "@/components/Sidebar";
import { BookCard as BookCardType, getBooks } from "@/lib/api";

export default function BrowsePage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [books, setBooks] = useState<BookCardType[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("dialogus_token");
    if (!token) {
      router.replace("/login");
      return;
    }

    let mounted = true;

    async function loadBooks() {
      try {
        setLoading(true);
        const result = await getBooks(query);
        if (mounted) {
          setBooks(result);
          setError("");
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : "Failed to load books");
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadBooks();
    return () => {
      mounted = false;
    };
  }, [query, router]);

  return (
    <main className="screen backdrop">
      <Navbar />
      <section className="app-layout">
        <Sidebar />
        <div className="content-column">
          <section className="glass panel">
            <h2>Browse Library</h2>
            <div className="search-row">
              <input
                name="q"
                placeholder="Search title, author, or genre"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
            </div>
          </section>

          <section className="glass panel">
            <h3>All Books</h3>
            {loading ? <p>Loading books...</p> : null}
            {error ? <p className="error-text">{error}</p> : null}
            <div className="book-grid">
              {books.map((book) => (
                <BookCard key={book.id} book={book} />
              ))}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
