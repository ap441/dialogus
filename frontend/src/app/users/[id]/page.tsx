"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { MarkdownRenderer } from "@/components/MarkdownRenderer";
import { Navbar } from "@/components/Navbar";
import { Sidebar } from "@/components/Sidebar";
import { ApiError, getUserProfile, ProfileData } from "@/lib/api";

export default function UserProfilePage() {
  const router = useRouter();
  const params = useParams();
  const id = Number(params.id);
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;

    async function loadProfile() {
      try {
        const result = await getUserProfile(id);
        if (mounted) {
          setProfile(result);
        }
      } catch (err) {
        if (mounted) {
          if (err instanceof ApiError && err.status === 404) {
            setError("User not found.");
            return;
          }
          setError(err instanceof Error ? err.message : "Failed to load profile");
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    if (id) {
      loadProfile();
    }
    
    return () => {
      mounted = false;
    };
  }, [id]);

  const initials = useMemo(() => {
    const source = profile?.full_name || profile?.email || "?";
    return source.slice(0, 2).toUpperCase();
  }, [profile]);

  return (
    <main className="screen backdrop">
      <Navbar />
      <section className="app-layout">
        <Sidebar />
        <div className="content-column">
          {loading ? (
            <section className="glass panel">
              <p>Loading profile...</p>
            </section>
          ) : null}

          {error ? (
            <section className="glass panel">
              <p className="error-text">{error}</p>
            </section>
          ) : null}

          {profile ? (
            <>
              <section className="glass panel profile-hero">
                <div className="profile-avatar-lg">{profile.avatar_url ? <img src={profile.avatar_url} alt={profile.full_name} /> : initials}</div>
                <div className="profile-hero-copy">
                  <p className="thread-meta">{profile.role === "admin" ? "Administrator" : "Member profile"}</p>
                  <h2>{profile.full_name}</h2>
                  <p>Joined {new Date(profile.created_at).toLocaleDateString()}</p>
                  <div className="profile-stats-inline">
                    <span>{profile.discussion_count} discussions</span>
                    <span>{profile.reply_count} replies</span>
                  </div>
                </div>
              </section>

              <section className="glass panel">
                <h3>Bio</h3>
                <div className="markdown-preview glass" style={{ marginTop: '16px' }}>
                  <MarkdownRenderer content={profile.bio || "*This user has not written a bio yet.*"} />
                </div>
              </section>
            </>
          ) : null}
        </div>
      </section>
    </main>
  );
}
