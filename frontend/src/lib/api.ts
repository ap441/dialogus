export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type Discussion = {
  id: number;
  title: string;
  excerpt: string;
  replies: number;
  created_at: string;
};

export type BookCard = {
  id: number;
  title: string;
  author: string;
  genre: string;
  cover_url: string;
  rating: number;
};

export type BookDetail = BookCard & {
  description: string;
  publication_year: number;
  language: string;
  pages: number;
  discussions: Discussion[];
};

export type HomeData = {
  welcome_name: string;
  trending_discussions: Discussion[];
  recommended_books: BookCard[];
};

// Prefer same-origin API calls so Next.js rewrites can proxy to backend.
const API_BASE = process.env.NEXT_PUBLIC_API_URL?.trim() || "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("dialogus_token") : null;

  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });

  if (!res.ok) {
    const message = await res.text();
    throw new Error(message || "Request failed");
  }

  return res.json() as Promise<T>;
}

export function signup(full_name: string, email: string, password: string) {
  return request<TokenResponse>("/api/auth/signup", {
    method: "POST",
    body: JSON.stringify({ full_name, email, password })
  });
}

export function login(email: string, password: string) {
  return request<TokenResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password })
  });
}

export function googleLogin(token: string) {
  return request<TokenResponse>("/api/auth/google", {
    method: "POST",
    body: JSON.stringify({ token })
  });
}

export function getHomeData(query = "") {
  const suffix = query ? `?q=${encodeURIComponent(query)}` : "";
  return request<HomeData>(`/api/discovery/home${suffix}`);
}

export function getBook(bookId: number) {
  return request<BookDetail>(`/api/books/${bookId}`);
}

export function getBooks(query = "") {
  const suffix = query ? `?q=${encodeURIComponent(query)}` : "";
  return request<BookCard[]>(`/api/books${suffix}`);
}
