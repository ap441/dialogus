"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { MarkdownEditor } from "@/components/MarkdownEditor";
import { MarkdownRenderer } from "@/components/MarkdownRenderer";
import { Navbar } from "@/components/Navbar";
import { Sidebar } from "@/components/Sidebar";
import { ApiError, getProfile, updateProfile, ProfileData } from "@/lib/api";

export default function ProfilePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [fullName, setFullName] = useState("");
  const [bio, setBio] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("dialogus_token");
    if (!token) {
      router.replace("/login");
      return;
    }

    let mounted = true;

    async function loadProfile() {
      try {
        const result = await getProfile();
        if (mounted) {
          setProfile(result);
          setFullName(result.full_name);
          setBio(result.bio || "");
          setAvatarUrl(result.avatar_url || "");
        }
      } catch (err) {
        if (mounted) {
          if (err instanceof ApiError && err.status === 401) {
            localStorage.removeItem("dialogus_token");
            localStorage.removeItem("userEmail");
            localStorage.removeItem("userRole");
            router.replace("/login");
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

    loadProfile();
    return () => {
      mounted = false;
    };
  }, [router]);

  const initials = useMemo(() => {
    const source = profile?.full_name || profile?.email || "?";
    return source.slice(0, 2).toUpperCase();
  }, [profile]);

  const handleSave = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      setSaving(true);
      const result = await updateProfile({ full_name: fullName, bio, avatar_url: avatarUrl || null });
      setProfile(result);
      setFullName(result.full_name);
      setBio(result.bio || "");
      setAvatarUrl(result.avatar_url || "");
      localStorage.setItem("userName", result.full_name);
      localStorage.setItem("userEmail", result.email);
      localStorage.setItem("userRole", result.role);
      if (result.avatar_url) {
        localStorage.setItem("userAvatar", result.avatar_url);
      }
      setSuccess("Profile updated successfully.");
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update profile");
      setSuccess("");
    } finally {
      setSaving(false);
    }
  };

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

          {profile ? (
            <>
              <section className="glass panel profile-hero">
                <div className="profile-avatar-lg">{profile.avatar_url ? <img src={profile.avatar_url} alt={profile.full_name} /> : initials}</div>
                <div className="profile-hero-copy">
                  <p className="thread-meta">{profile.role === "admin" ? "Administrator" : "Reader profile"}</p>
                  <h2>{profile.full_name}</h2>
                  <p>{profile.email}</p>
                  <div className="profile-stats-inline">
                    <span>{profile.discussion_count} discussions</span>
                    <span>{profile.reply_count} replies</span>
                    <span>{profile.unread_notification_count} unread notifications</span>
                  </div>
                </div>
              </section>

              <section className="glass panel profile-grid">
                <form className="profile-form" onSubmit={handleSave}>
                  <h3>Edit profile</h3>
                  <label>
                    Display name
                    <input value={fullName} onChange={(event) => setFullName(event.target.value)} required />
                  </label>
                  <label>
                    Avatar URL
                    <input value={avatarUrl} onChange={(event) => setAvatarUrl(event.target.value)} placeholder="https://..." />
                  </label>
                  <MarkdownEditor
                    label="Bio"
                    value={bio}
                    onChange={setBio}
                    placeholder="Tell people about your reading tastes, favorite genres, and current obsessions..."
                    rows={8}
                    hint="Your bio supports markdown, so the profile can be as plain or as polished as you like."
                    previewLabel="Preview bio"
                  />
                  <button type="submit" disabled={saving}>
                    {saving ? "Saving..." : "Save profile"}
                  </button>
                  {success ? <p className="success-text">{success}</p> : null}
                  {error ? <p className="error-text">{error}</p> : null}
                </form>

                <section className="profile-summary">
                  <h3>Bio preview</h3>
                  <div className="markdown-preview glass">
                    <MarkdownRenderer content={bio || "*No bio yet — this is your space to shine.*"} />
                  </div>

                  <div className="profile-cards">
                    <article className="glass profile-card">
                      <strong>{profile.reaction_count}</strong>
                      <span>Appreciations made</span>
                    </article>
                    <article className="glass profile-card">
                      <strong>{profile.notification_count}</strong>
                      <span>Notifications received</span>
                    </article>
                    <article className="glass profile-card">
                      <strong>{new Date(profile.created_at).toLocaleDateString()}</strong>
                      <span>Joined</span>
                    </article>
                  </div>
                </section>
              </section>
            </>
          ) : null}
        </div>
      </section>
    </main>
  );
}