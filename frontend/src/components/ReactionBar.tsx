type ReactionType = "like" | "dislike" | "recommend";

type ReactionCounts = {
  like: number;
  dislike: number;
  recommend: number;
};

type ReactionBarProps = {
  reactionCounts?: ReactionCounts;
  activeReaction?: ReactionType | null;
  onReact: (reactionType: ReactionType) => void;
  compact?: boolean;
};

const reactions: Array<{ type: ReactionType; icon: string; label: string }> = [
  { type: "like", icon: "❤", label: "Like" },
  { type: "dislike", icon: "▾", label: "Dislike" },
  { type: "recommend", icon: "★", label: "Recommend" }
];

export function ReactionBar({ reactionCounts, activeReaction, onReact, compact = false }: ReactionBarProps) {
  return (
    <div className={`reaction-bar ${compact ? "compact" : ""}`}>
      {reactions.map((reaction) => {
        const count = reactionCounts?.[reaction.type] ?? 0;
        const active = activeReaction === reaction.type;

        return (
          <button
            key={reaction.type}
            type="button"
            className={`reaction-btn ${reaction.type} ${active ? "active" : ""}`}
            onClick={(event) => {
              event.stopPropagation();
              onReact(reaction.type);
            }}
            aria-label={reaction.label}
            title={reaction.label}
          >
            <span className="reaction-icon">{reaction.icon}</span>
            <span className="reaction-count">{count}</span>
          </button>
        );
      })}
    </div>
  );
}
