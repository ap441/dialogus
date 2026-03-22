import { Discussion } from "@/lib/api";

export function DiscussionCard({ discussion }: { discussion: Discussion }) {
  return (
    <article className="discussion-card glass">
      <h4>{discussion.title}</h4>
      <p>{discussion.excerpt}</p>
      <div className="discussion-footer">
        <span>{discussion.replies} replies</span>
      </div>
    </article>
  );
}
