"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { ReactionBar } from "@/components/ReactionBar";
import { Navbar } from "@/components/Navbar";
import { Sidebar } from "@/components/Sidebar";
import { createThreadReply, DiscussionThread, getDiscussionThread, setDiscussionReaction } from "@/lib/api";

export default function DiscussionThreadPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [thread, setThread] = useState<DiscussionThread | null>(null);
  const [draft, setDraft] = useState("");
  const [replyTo, setReplyTo] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("dialogus_token");
    if (!token) {
      router.replace("/login");
      return;
    }

    let mounted = true;

    async function load() {
      try {
        setLoading(true);
        const result = await getDiscussionThread(Number(params.id));
        if (mounted) {
          setThread(result);
          setError("");
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : "Failed to load thread");
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      mounted = false;
    };
  }, [params.id, router]);

  async function handleReactThread(reactionType: "like" | "dislike" | "recommend") {
    if (!thread) {
      return;
    }

    try {
      const result = await setDiscussionReaction(thread.id, reactionType);
      setThread((current) =>
        current
          ? {
              ...current,
              likes_count: result.likes_count,
              liked_by_me: result.reaction_type === "like",
              user_reaction: result.reaction_type,
              reaction_counts: result.reaction_counts,
            }
          : current
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to appreciate discussion");
    }
  }

  async function handleReply(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!thread) {
      return;
    }

    try {
      setSubmitting(true);
      const created = await createThreadReply(thread.id, {
        content: draft,
        parent_post_id: replyTo,
      });
      setThread((current) =>
        current
          ? {
              ...current,
              replies: current.replies + 1,
              posts: [...current.posts, created],
            }
          : current
      );
      setDraft("");
      setReplyTo(null);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to post reply");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="screen backdrop">
      <Navbar />
      <section className="app-layout">
        <Sidebar />
        <div className="content-column">
          {loading ? <div className="glass panel"><p>Loading thread...</p></div> : null}
          {error ? <div className="glass panel"><p className="error-text">{error}</p></div> : null}

          {thread ? (
            <>
              <section className="glass panel">
                <div className="thread-header-row">
                  <div>
                    <p className="thread-meta">{thread.book_title} • started by {thread.author_name}</p>
                    <h2>{thread.title}</h2>
                    <p className="book-description">{thread.body || thread.excerpt}</p>
                  </div>
                  <ReactionBar
                    reactionCounts={thread.reaction_counts}
                    activeReaction={thread.user_reaction ?? null}
                    onReact={handleReactThread}
                  />
                </div>
              </section>

              <section className="glass panel">
                <h3>Thread Replies</h3>
                <div className="discussion-stack">
                  {thread.posts.map((post) => (
                    <article key={post.id} className="thread-post" style={{ marginLeft: `${post.depth * 18}px` }}>
                      <div className="thread-post-head">
                        <strong>{post.author_name}</strong>
                        <small>{new Date(post.created_at).toLocaleString()}</small>
                      </div>
                      <p>{post.content}</p>
                      <button type="button" className="text-btn" onClick={() => setReplyTo(post.id)}>
                        Reply
                      </button>
                    </article>
                  ))}
                </div>

                <form className="thread-form" onSubmit={handleReply}>
                  {replyTo ? (
                    <p className="thread-meta">
                      Replying to post #{replyTo}{" "}
                      <button type="button" className="text-btn" onClick={() => setReplyTo(null)}>
                        Cancel
                      </button>
                    </p>
                  ) : null}
                  <textarea
                    value={draft}
                    onChange={(event) => setDraft(event.target.value)}
                    rows={4}
                    placeholder="Share your thoughts..."
                    required
                  />
                  <button type="submit" disabled={submitting}>
                    {submitting ? "Posting..." : "Post Reply"}
                  </button>
                </form>
              </section>
            </>
          ) : null}
        </div>
      </section>
    </main>
  );
}
