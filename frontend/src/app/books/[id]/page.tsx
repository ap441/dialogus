"use client";

import { FormEvent, useEffect, useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";

import { DiscussionCard } from "@/components/DiscussionCard";
import { Navbar } from "@/components/Navbar";
import { Sidebar } from "@/components/Sidebar";
import { BookDetail, createDiscussion, getBook, toggleDiscussionLike } from "@/lib/api";

export default function BookDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [book, setBook] = useState<BookDetail | null>(null);
  const [threadTitle, setThreadTitle] = useState("");
  const [threadExcerpt, setThreadExcerpt] = useState("");
  const [threadBody, setThreadBody] = useState("");
  const [savingThread, setSavingThread] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("dialogus_token");
    if (!token) {
      router.replace("/login");
      return;
    }

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
  }, [params.id, router]);

  async function handleCreateThread(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!book) {
      return;
    }

    try {
      setSavingThread(true);
      const created = await createDiscussion(book.id, {
        title: threadTitle,
        excerpt: threadExcerpt,
        body: threadBody,
      });
      setBook((current) => {
        if (!current) {
          return current;
        }
        return {
          ...current,
          discussions: [created, ...current.discussions],
        };
      });
      setThreadTitle("");
      setThreadExcerpt("");
      setThreadBody("");
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create discussion");
    } finally {
      setSavingThread(false);
    }
  }

  async function handleLike(discussionId: number) {
    try {
      const result = await toggleDiscussionLike(discussionId);
      setBook((current) => {
        if (!current) {
          return current;
        }
        return {
          ...current,
          discussions: current.discussions.map((discussion) =>
            discussion.id === discussionId
              ? {
                  ...discussion,
                  likes_count: result.likes_count,
                  liked_by_me: result.liked,
                }
              : discussion
          ),
        };
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to appreciate discussion");
    }
  }

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
            <form className="thread-form" onSubmit={handleCreateThread}>
              <input
                value={threadTitle}
                onChange={(event) => setThreadTitle(event.target.value)}
                placeholder="Thread title"
                required
              />
              <input
                value={threadExcerpt}
                onChange={(event) => setThreadExcerpt(event.target.value)}
                placeholder="One-line prompt"
                required
              />
              <textarea
                value={threadBody}
                onChange={(event) => setThreadBody(event.target.value)}
                placeholder="Share your deeper take"
                rows={4}
              />
              <button type="submit" disabled={savingThread}>
                {savingThread ? "Publishing..." : "Publish Thread"}
              </button>
            </form>
            <p className="book-description">{book.description}</p>

            <div className="discussion-stack">
              {book.discussions.map((discussion) => (
                <DiscussionCard
                  key={discussion.id}
                  discussion={discussion}
                  onOpen={(discussionId) => router.push(`/discussions/${discussionId}`)}
                  onLike={handleLike}
                />
              ))}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
