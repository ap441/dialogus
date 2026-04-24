# FJ3 Maintenance Model Comparison (Dialogus)

## Project Context
Dialogus is a modular monolith (FastAPI + Next.js) with active feature growth across short sprints. Up to Sprint 2, the team has implemented:
- Sprint 1 baseline: authentication, book discovery, book detail
- Sprint 2: timeline feed, appreciation system, discussion thread engine, notification UI placeholder

The maintenance approach must support frequent change, low overhead, and safe incremental releases.

## Model Comparison

| Model | How It Works | Strengths | Weaknesses | Fit for Dialogus |
|---|---|---|---|---|
| Quick-Fix Model | Fix issues directly in existing code with minimal analysis/design updates | Very fast for urgent production bugs | Causes technical debt quickly, poor documentation discipline, fragile architecture over time | Poor long-term fit; only acceptable for hotfixes |
| Iterative Enhancement Model | Maintenance is handled in planned increments: analyze change request, design update, implement, test, release | Predictable quality, good traceability, architecture stays healthy, aligns with sprint process | Slightly slower than ad hoc fixes, needs process discipline | Best fit for current project workflow |
| Reengineering / Migration-Oriented Maintenance | Periodic restructuring and modernization (schema refactor, service split, framework changes) | Good for large legacy stabilization and scale transitions | Costly for early-stage products, overkill for small fast-moving teams | Useful later, not primary model now |

## Selected Model
**Selected model: Iterative Enhancement Maintenance Model**

## Justification for Selection
1. The project already runs in sprint cycles, so maintenance can be naturally planned as backlog items.
2. New features in Sprint 2 affected both backend and frontend contracts (timeline, reactions, thread replies). This type of cross-layer change needs controlled impact analysis.
3. The current architecture (modular monolith) benefits from continuous refactoring, not unstructured patching.
4. The team needs evidence-based academic reporting (risk, bugs, tests). Iterative enhancement produces auditable artifacts.
5. Notification work is currently partial (UI-level indicator only), and iterative enhancement allows phased completion without destabilizing core flows.

## How the Chosen Model Is Applied in Dialogus
1. **Change intake:** user stories, bug tickets, and support observations are logged.
2. **Impact analysis:** API contracts, models, UI components, and DB effects are reviewed.
3. **Planned implementation:** changes are grouped into sprint tasks (not random patching).
4. **Regression-focused validation:** test cases are updated for old and new behavior.
5. **Release + review:** release notes and bug history are updated; unresolved items move to next sprint.

## Conclusion
For Dialogus at its current maturity, Iterative Enhancement gives the best balance between speed and quality. It supports controlled growth, keeps maintenance visible, and avoids the long-term instability associated with quick-fix-only maintenance.
