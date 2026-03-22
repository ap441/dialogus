"use client";

import { useEffect, useState } from "react";
import Image from "next/image";

import { DiscussionCard } from "@/components/DiscussionCard";
import { Navbar } from "@/components/Navbar";
import { Sidebar } from "@/components/Sidebar";
import { BookDetail, getBook } from "@/lib/api";

export default function BookDetailPage({ params }: { params: { id: string } }) {
  const [book, setBook] = useState<BookDetail | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const bookId = Number(params.id);
        const result = await getBook(bookId);
        setBook(result);
        setError("");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load book");
      }
    }

    load();
  }, [params.id]);

  if (error) {
    return (
      <main className="screen backdrop">
        <Navbar />
        <section className="app-layout">
          <Sidebar />
          <div className="glass panel">
            <p className="error-text">{error}</p>
          </div>
        </section>
      </main>
    );
  }

  if (!book) {
    return (
      <main className="screen backdrop">
        <Navbar />
        <section className="app-layout">
          <Sidebar />
          <div className="glass panel">
            <p>Loading book...</p>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="screen backdrop">
      <Navbar />
      <section className="app-layout">
        <Sidebar />
        <div className="book-layout">
          <aside className="glass book-panel">
            <Image src={book.cover_url} alt={book.title} width={220} height={320} className="book-cover-lg" />
            <h1>{book.title}</h1>
            <p>by {book.author}</p>
            <ul>
              <li>Genre: {book.genre}</li>
              <li>Rating: {book.rating.toFixed(1)} / 5</li>
              <li>Publication: {book.publication_year}</li>
              <li>Language: {book.language}</li>
              <li>Pages: {book.pages}</li>
            </ul>
          </aside>

          <section className="glass panel discussion-panel">
            <div className="tab-row">
              <button className="active">Overview</button>
              <button>Discussions</button>
              <button>Similar</button>
              <button>Stats</button>
            </div>

            <h3>Start New Thread</h3>
            <p className="book-description">{book.description}</p>

            <div className="discussion-stack">
              {book.discussions.map((discussion) => (
                <DiscussionCard key={discussion.id} discussion={discussion} />
              ))}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
