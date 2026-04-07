import { Discussion } from "@/lib/api";

type Props = {
  discussion: Discussion;
  onOpen?: (discussionId: number) => void;
  onLike?: (discussionId: number) => void;
};

export function DiscussionCard({ discussion, onOpen, onLike }: Props) {
  const likes = discussion.likes_count ?? 0;

  return (
    <article className="discussion-card glass" onClick={() => onOpen?.(discussion.id)}>
      <h4>{discussion.title}</h4>
      <p>{discussion.excerpt}</p>
      {discussion.book_title ? <small className="discussion-book">From {discussion.book_title}</small> : null}
      <div className="discussion-footer">
        <span>{discussion.replies} replies</span>
        <button
          type="button"
          className={`like-btn ${discussion.liked_by_me ? "liked" : ""}`}
          onClick={(event) => {
            event.stopPropagation();
            onLike?.(discussion.id);
          }}
        >
          {discussion.liked_by_me ? "Appreciated" : "Appreciate"} ({likes})
        </button>
      </div>
    </article>
  );
}
