export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type Discussion = {
  id: number;
  book_id?: number | null;
  book_title?: string | null;
  title: string;
  excerpt: string;
  body?: string;
  replies: number;
  likes_count?: number;
  liked_by_me?: boolean;
  user_reaction?: ReactionType | null;
  reaction_counts?: ReactionCounts;
  author_name?: string;
  created_at: string;
};

export type ReactionType = "like" | "dislike" | "recommend";

export type ReactionCounts = {
  like: number;
  dislike: number;
  recommend: number;
};

export type ThreadPost = {
  id: number;
  discussion_id: number;
  parent_post_id: number | null;
  author_name: string;
  content: string;
  created_at: string;
  depth: number;
};

export type DiscussionThread = {
  id: number;
  book_id: number;
  book_title: string;
  title: string;
  excerpt: string;
  body: string;
  replies: number;
  likes_count: number;
  liked_by_me: boolean;
  user_reaction?: ReactionType | null;
  reaction_counts?: ReactionCounts;
  author_name: string;
  created_at: string;
  posts: ThreadPost[];
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

export function getTimeline(query = "") {
  const suffix = query ? `?q=${encodeURIComponent(query)}` : "";
  return request<Discussion[]>(`/api/discussions/timeline${suffix}`);
}

export function getBook(bookId: number) {
  return request<BookDetail>(`/api/books/${bookId}`);
}

export function getBooks(query = "") {
  const suffix = query ? `?q=${encodeURIComponent(query)}` : "";
  return request<BookCard[]>(`/api/books${suffix}`);
}

export function toggleDiscussionLike(discussionId: number) {
  return setDiscussionReaction(discussionId, "like");
}

export function setDiscussionReaction(discussionId: number, reactionType: ReactionType) {
  return request<{ discussion_id: number; reaction_type: ReactionType | null; likes_count: number; reaction_counts: ReactionCounts }>(
    `/api/discussions/${discussionId}/reaction`,
    {
      method: "POST",
      body: JSON.stringify({ reaction_type: reactionType })
    }
  );
}

export function toggleDiscussionReaction(discussionId: number, reactionType: ReactionType) {
  return setDiscussionReaction(discussionId, reactionType);
}

export function createDiscussion(bookId: number, payload: { title: string; excerpt: string; body: string }) {
  return request<Discussion>(`/api/books/${bookId}/discussions`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getDiscussionThread(discussionId: number) {
  return request<DiscussionThread>(`/api/discussions/${discussionId}/thread`);
}

export function createThreadReply(discussionId: number, payload: { content: string; parent_post_id?: number | null }) {
  return request<ThreadPost>(`/api/discussions/${discussionId}/posts`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
