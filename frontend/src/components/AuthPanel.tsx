"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { GoogleLogin } from "@react-oauth/google";

import { login, signup, googleLogin } from "@/lib/api";

type Mode = "login" | "signup";

export function AuthPanel({ mode }: { mode: Mode }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");

    const formData = new FormData(event.currentTarget);
    const email = String(formData.get("email") || "");
    const password = String(formData.get("password") || "");

    try {
      if (mode === "signup") {
        const fullName = String(formData.get("fullName") || "");
        const confirmPassword = String(formData.get("confirmPassword") || "");
        if (password !== confirmPassword) {
          throw new Error("Passwords do not match");
        }
        const token = await signup(fullName, email, password);
        localStorage.setItem("dialogus_token", token.access_token);
        localStorage.setItem("userEmail", email);
      } else {
        const token = await login(email, password);
        localStorage.setItem("dialogus_token", token.access_token);
        localStorage.setItem("userEmail", email);
      }

      router.push("/home");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogleSuccess(credentialResponse: any) {
    setLoading(true);
    setError("");

    try {
      const token = await googleLogin(credentialResponse.credential);
      localStorage.setItem("dialogus_token", token.access_token);
      // Extract email from the JWT if needed, or fetch from /api/auth/me
      const decoded = JSON.parse(atob(credentialResponse.credential.split('.')[1]));
      localStorage.setItem("userEmail", decoded.email);
      router.push("/home");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Google sign-in failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="auth-panel glass" onSubmit={onSubmit}>
      <h1>{mode === "login" ? "Log In" : "Sign Up"}</h1>
      {mode === "signup" && <input name="fullName" placeholder="Full Name" required />}
      <input name="email" type="email" placeholder="Email" required />
      <input name="password" type="password" placeholder="Password" required />
      {mode === "signup" && <input name="confirmPassword" type="password" placeholder="Confirm Password" required />}

      <button type="submit" disabled={loading}>
        {loading ? "Please wait..." : mode === "login" ? "Log In" : "Create Account"}
      </button>

      <div className="google-signin-wrapper">
        <GoogleLogin
          onSuccess={handleGoogleSuccess}
          onError={() => setError("Google sign-in failed")}
        />
      </div>

      {error ? <p className="error-text">{error}</p> : null}
    </form>
  );
}
