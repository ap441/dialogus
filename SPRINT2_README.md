# Dialogus Sprint 2 Implementation

This document summarizes everything implemented for Sprint 2.

## Sprint 2 Goals

- Timeline Feed
- Like and Appreciation System
- Discussion Thread Engine

## What Was Implemented

### 1. Timeline Feed

Backend:
- Added timeline endpoint to return discussions ordered by recency.
- Supports authenticated fetching and optional search query.
- Includes per-discussion reaction state and counts for the current user.

Frontend:
- Home experience now pulls a dedicated timeline feed.
- Timeline cards render title, excerpt, author, book tag, replies, and reactions.
- Timeline state updates immediately after interactions.

### 2. Social Appreciation System

The original single like action was upgraded to a social reaction model.

Backend:
- Reactions are stored in discussion_likes with a typed reaction field.
- Supported reactions:
  - like
  - dislike
  - recommend
- One reaction per user per discussion.
- Switching reactions updates counts correctly.
- Sending the same reaction again toggles it off.
- Added reaction summary fields to discussion payloads:
  - user_reaction
  - reaction_counts { like, dislike, recommend }

Frontend:
- Replaced text like action with icon reaction bar.
- Added icon-based controls for all 3 reaction types.
- Active reaction is highlighted.
- Counts update live after clicks.
- Applied to all discussion surfaces:
  - home feed cards
  - book detail discussions
  - full thread page

### 3. Discussion Thread Engine

Backend:
- Added thread post model with parent_post_id for nested replies.
- Added endpoints for:
  - creating a discussion under a book
  - retrieving a full discussion thread
  - posting replies to a thread
- Thread payload includes:
  - root discussion metadata
  - replies
  - reaction state and counts

Frontend:
- Added thread page with full conversation view.
- Supports posting replies.
- Supports reacting at thread level.
- Discussion cards navigate into full threads.

## Data Model Changes

- User
  - relationship support for authored discussions and posts
- Discussion
  - body
  - author_id
  - likes_count
- DiscussionLike
  - reaction_type (like, dislike, recommend)
  - unique user-discussion constraint
- DiscussionPost
  - discussion_id
  - author_id
  - parent_post_id
  - content

## API Additions and Updates

Implemented and wired:

- GET /api/discussions/timeline
- POST /api/books/{book_id}/discussions
- GET /api/discussions/{discussion_id}/thread
- POST /api/discussions/{discussion_id}/posts
- POST /api/discussions/{discussion_id}/reaction
- POST /api/discussions/{discussion_id}/like (backward-compatible wrapper)

Updated response models to include reaction metadata in discussion payloads.

## UI and UX Improvements

- Introduced reusable ReactionBar component.
- Upgraded discussion card visuals with stronger feed styling.
- Added author and context chips for better scannability.
- Improved consistency of interaction patterns across pages.

## Validation Completed

- Backend startup and health checks passed.
- End-to-end flow validated:
  - auth
  - timeline fetch
  - create discussion
  - create reply
  - reaction toggling and switching
  - thread fetch with reaction counts
- Dockerized local environment verified.

## Notes

- Current reactions are discussion-level, not post-level.
- Current timeline is server-returned list without infinite scrolling.
- Architecture remains modular monolith, with clear service and API boundaries.

## Related Files

Backend:
- backend/app/api/discussions.py
- backend/app/models.py
- backend/app/schemas.py
- backend/app/api/books.py
- backend/app/api/discovery.py
- backend/app/main.py
- backend/app/seed.py

Frontend:
- frontend/src/components/ReactionBar.tsx
- frontend/src/components/DiscussionCard.tsx
- frontend/src/app/home/page.tsx
- frontend/src/app/books/[id]/page.tsx
- frontend/src/app/discussions/[id]/page.tsx
- frontend/src/lib/api.ts
- frontend/src/app/globals.css

---

Sprint 2 status: Complete and integrated across backend, frontend, and data layer.
