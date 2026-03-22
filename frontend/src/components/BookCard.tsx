import Image from "next/image";
import Link from "next/link";

import { BookCard as BookCardType } from "@/lib/api";

export function BookCard({ book }: { book: BookCardType }) {
  return (
    <Link href={`/books/${book.id}`} className="book-card glass">
      <div className="book-cover-wrap">
        <Image src={book.cover_url} alt={book.title} width={160} height={220} className="book-cover" />
      </div>
      <div className="book-meta">
        <h4>{book.title}</h4>
        <p>by {book.author}</p>
        <span>{book.genre}</span>
        <small>{book.rating.toFixed(1)} / 5</small>
      </div>
    </Link>
  );
}
