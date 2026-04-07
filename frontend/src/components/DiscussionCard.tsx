import { Discussion } from "@/lib/api";
import { ReactionBar } from "@/components/ReactionBar";

type Props = {
  discussion: Discussion;
  onOpen?: (discussionId: number) => void;
  onReact?: (discussionId: number, reactionType: "like" | "dislike" | "recommend") => void;
};

export function DiscussionCard({ discussion, onOpen, onReact }: Props) {
  const reactionCounts = discussion.reaction_counts ?? {
    like: discussion.likes_count ?? 0,
    dislike: 0,
    recommend: 0,
  };

  return (
    <article className="discussion-card glass" onClick={() => onOpen?.(discussion.id)}>
      <div className="discussion-topline">
        <div>
          <p className="discussion-author">{discussion.author_name ?? "Community"}</p>
          <h4>{discussion.title}</h4>
        </div>
        {discussion.book_title ? <span className="discussion-book-tag">{discussion.book_title}</span> : null}
      </div>
      <p className="discussion-excerpt">{discussion.excerpt}</p>
      <div className="discussion-footer">
        <span className="reply-count">{discussion.replies} replies</span>
        <ReactionBar
          compact
          reactionCounts={reactionCounts}
          activeReaction={discussion.user_reaction ?? null}
          onReact={(reactionType) => onReact?.(discussion.id, reactionType)}
        />
      </div>
    </article>
  );
}
