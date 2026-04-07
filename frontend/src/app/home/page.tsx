"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { BookCard } from "@/components/BookCard";
import { DiscussionCard } from "@/components/DiscussionCard";
import { Navbar } from "@/components/Navbar";
import { Sidebar } from "@/components/Sidebar";
import { Discussion, HomeData, getHomeData, getTimeline, setDiscussionReaction } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<HomeData | null>(null);
  const [timeline, setTimeline] = useState<Discussion[]>([]);
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
        const [result, timelineData] = await Promise.all([getHomeData(query), getTimeline(query)]);
        if (mounted) {
          setData(result);
          setTimeline(timelineData);
          setError("");
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : "Failed to load data");
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
  }, [query, router]);

  async function handleReact(discussionId: number, reactionType: "like" | "dislike" | "recommend") {
    try {
      const result = await setDiscussionReaction(discussionId, reactionType);
      setTimeline((current) =>
        current.map((discussion) =>
          discussion.id === discussionId
            ? {
                ...discussion,
                likes_count: result.likes_count,
                liked_by_me: result.reaction_type === "like",
                user_reaction: result.reaction_type,
                reaction_counts: result.reaction_counts,
              }
            : discussion
        )
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update appreciation");
    }
  }

  return (
    <main className="screen backdrop">
      <Navbar />
      <section className="app-layout">
        <Sidebar />
        <div className="content-column">
          <div className="glass panel">
            <h2>Welcome back, {data?.welcome_name ?? "Reader"}</h2>
            <div className="search-row">
              <input
                name="q"
                placeholder="Search"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
            </div>
          </div>

          <section className="glass panel">
            <h3>Timeline Feed</h3>
            <div className="discussion-grid">
              {timeline.map((discussion) => (
                <DiscussionCard
                  key={`timeline-${discussion.id}`}
                  discussion={discussion}
                  onOpen={(discussionId) => router.push(`/discussions/${discussionId}`)}
                  onReact={handleReact}
                />
              ))}
            </div>
          </section>

          <section className="glass panel">
            <h3>Trending Discussions</h3>
            <div className="discussion-grid">
              {loading ? <p>Loading discussions...</p> : null}
              {error ? <p className="error-text">{error}</p> : null}
              {data?.trending_discussions.map((discussion) => (
                <DiscussionCard
                  key={discussion.id}
                  discussion={discussion}
                  onOpen={(discussionId) => router.push(`/discussions/${discussionId}`)}
                  onReact={handleReact}
                />
              ))}
            </div>
          </section>

          <section className="glass panel">
            <h3>Recommended Books</h3>
            <div className="book-grid">
              {data?.recommended_books.map((book) => (
                <BookCard key={book.id} book={book} />
              ))}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
