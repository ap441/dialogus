"use client";

import { FormEvent, useEffect, useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";

import { DiscussionCard } from "@/components/DiscussionCard";
import { MarkdownEditor } from "@/components/MarkdownEditor";
import { MarkdownRenderer } from "@/components/MarkdownRenderer";
import { Navbar } from "@/components/Navbar";
import { Sidebar } from "@/components/Sidebar";
import { ApiError, BookDetail, createDiscussion, getBook, setDiscussionReaction } from "@/lib/api";

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
        if (err instanceof ApiError && err.status === 401) {
          localStorage.removeItem("dialogus_token");
          localStorage.removeItem("userEmail");
          router.replace("/login");
          return;
        }

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

  async function handleReact(discussionId: number, reactionType: "like" | "dislike" | "recommend") {
    try {
      const result = await setDiscussionReaction(discussionId, reactionType);
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
                  liked_by_me: result.user_reactions.includes("like"),
                  user_reaction: result.user_reactions[0] ?? null,
                  user_reactions: result.user_reactions,
                  reaction_counts: result.reaction_counts,
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
              <MarkdownEditor
                value={threadBody}
                onChange={setThreadBody}
                placeholder="Share your deeper take in markdown"
                rows={5}
                hint="Markdown is supported here, so you can style the discussion before it even begins."
                previewLabel="Preview thread"
              />
              <button type="submit" disabled={savingThread}>
                {savingThread ? "Publishing..." : "Publish Thread"}
              </button>
            </form>
            <div className="book-description markdown-inline">
              <MarkdownRenderer content={book.description} />
            </div>

            <div className="discussion-stack">
              {book.discussions.map((discussion) => (
                <DiscussionCard
                  key={discussion.id}
                  discussion={discussion}
                  onOpen={(discussionId) => router.push(`/discussions/${discussionId}`)}
                  onReact={handleReact}
                />
              ))}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
