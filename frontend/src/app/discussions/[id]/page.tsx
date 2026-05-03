"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { MarkdownEditor } from "@/components/MarkdownEditor";
import { MarkdownRenderer } from "@/components/MarkdownRenderer";
import { ReactionBar } from "@/components/ReactionBar";
import { Navbar } from "@/components/Navbar";
import { Sidebar } from "@/components/Sidebar";
import { ApiError, createThreadReply, DiscussionThread, getDiscussionThread, setDiscussionReaction } from "@/lib/api";

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
          if (err instanceof ApiError && err.status === 401) {
            localStorage.removeItem("dialogus_token");
            localStorage.removeItem("userEmail");
            router.replace("/login");
            return;
          }

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
              liked_by_me: result.user_reactions.includes("like"),
              user_reaction: result.user_reactions[0] ?? null,
              user_reactions: result.user_reactions,
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
                    <div className="thread-body-markdown">
                      <MarkdownRenderer content={thread.body || thread.excerpt} />
                    </div>
                  </div>
                  <ReactionBar
                    reactionCounts={thread.reaction_counts}
                    activeReaction={thread.user_reaction ?? null}
                    activeReactions={thread.user_reactions ?? []}
                    onReact={handleReactThread}
                  />
                </div>
              </section>

              <section className="glass panel">
                <h3>Thread Replies</h3>
                <div className="discussion-stack">
                  {thread.posts.map((post) => (
                    <article key={post.id} className="thread-post" style={{ marginLeft: `min(${post.depth * 28}px, 15vw)` }}>
                      <div className="thread-post-head">
                        <div className="thread-post-avatar">
                          {post.author_name.substring(0, 2).toUpperCase()}
                        </div>
                        <div className="thread-post-author-info">
                          <strong>{post.author_name}</strong>
                          <small>{new Date(post.created_at).toLocaleString()}</small>
                        </div>
                      </div>
                      <div className="thread-post-body">
                        <MarkdownRenderer content={post.content} />
                      </div>
                      <div className="thread-post-actions">
                        <button type="button" className="action-btn-small" onClick={() => setReplyTo(post.id)}>
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '6px' }}><polyline points="15 10 20 15 15 20"></polyline><path d="M4 4v7a4 4 0 0 0 4 4h12"></path></svg>
                          Reply
                        </button>
                      </div>
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
                  <MarkdownEditor
                    value={draft}
                    onChange={setDraft}
                    placeholder="Share your thoughts in markdown..."
                    rows={5}
                    hint="Replies support markdown formatting, quotes, links, and code snippets."
                    previewLabel="Preview reply"
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
