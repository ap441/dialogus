# FJ3 Presentation Outline (Dialogus)

## Slide 1: Title
- Dialogus SEPM FJ3 Assessment
- Team details
- Scope: Maintenance Model, RMMM, Test Cases and Bug History

Speaker note:
- Introduce project briefly and confirm this presentation covers progress up to Sprint 2.

## Slide 2: Sprint Coverage
- Sprint 1 baseline: auth + discovery + browse + book detail
- Sprint 2 additions:
  - Timeline feed
  - Like/Appreciation system
  - Discussion thread engine
  - Notification UI placeholder

Speaker note:
- Emphasize that deliverables are mapped to implemented code and tested behavior.

## Slide 3: Maintenance Models Compared
- Quick-Fix Model
- Iterative Enhancement Model
- Reengineering-Oriented Maintenance

Speaker note:
- Present one-line strengths and limitations for each model.

## Slide 4: Chosen Model and Why
- Selected: Iterative Enhancement
- Why:
  - Works with sprint cadence
  - Better traceability for academic review
  - Lower long-term debt than quick-fix strategy
  - Suitable for cross-layer changes in Sprint 2

Speaker note:
- Mention that this model helped control reaction/thread changes without destabilizing Sprint 1 flows.

## Slide 5: RMMM Framework
- Risk identification
- Risk scoring (Probability x Impact)
- Mitigation
- Monitoring
- Management/contingency

Speaker note:
- Explain that risks were tracked proactively, not only after defects occurred.

## Slide 6: Top Risks in Dialogus
- Session security and token handling
- Reaction counter consistency
- Timeline performance at scale
- Notification scope gap
- Regression quality risk

Speaker note:
- Highlight how these were selected from actual Sprint 2 behavior and backlog signals.

## Slide 7: RMMM Action Plan
- Sprint 2 closeout controls
- Sprint 3 planned controls (notifications backend, pagination, migration workflow)
- Ownership and review cadence

Speaker note:
- Mention owners and review frequency to show operational seriousness.

## Slide 8: Test Strategy
- Coverage split: Sprint 1 + Sprint 2
- Positive tests + edge tests + auth/session tests
- API and UI interaction validations

Speaker note:
- State that the report includes both expected pass paths and known limitations.

## Slide 9: Sprint 1 Test Summary
- Core authentication flow stable
- Protected-route behavior validated
- Discovery and browse search behavior validated

Speaker note:
- Keep this concise; focus on establishing baseline stability.

## Slide 10: Sprint 2 Test Summary
- Timeline retrieval and filtering validated
- Reaction toggle/switch paths validated
- Thread creation and nested reply validations completed
- Notification currently UI-level only

Speaker note:
- Be transparent on partial notification implementation.

## Slide 11: Bug History and Lessons
- Total bugs tracked: 8
- Closed: 7
- Open/planned: 1 (notification scope)
- Key lesson: reaction state transitions and nested reply validation need strong regression checks

Speaker note:
- Mention one or two concrete bugs and how they were fixed.

## Slide 12: Conclusion and Next Sprint Plan
- Chosen maintenance model supports sustainable growth
- RMMM has clear high-risk controls
- Test and bug history show measurable quality progress
- Next: full notifications, stronger DB migration discipline, performance hardening

Speaker note:
- End with confidence and a realistic roadmap.

## Quick Q&A Backup Points
- Why not quick-fix model?
  - Fast initially, but harms maintainability and evidence quality.
- Why is one bug still open?
  - It is a known planned enhancement (notification engine) rather than a silent failure.
- How do we ensure future quality?
  - Regression checklist, risk review cadence, and contract-aware testing.
