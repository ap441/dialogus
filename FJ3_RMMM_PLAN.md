# FJ3 RMMM Plan (Dialogus, Through Sprint 2)

## 1. Project Snapshot
- Project: Dialogus
- Stack: FastAPI, SQLAlchemy, Next.js, TypeScript, SQLite/Postgres-ready
- Current scope baseline: Sprint 1 + Sprint 2
- Sprint 2 feature set in scope for this plan:
  - Timeline feed
  - Like/Appreciation system
  - Discussion thread engine
  - Notification UI entry point (full notification engine pending)

## 2. RMMM Objective
This RMMM plan identifies key risks that can affect functionality, delivery, quality, and maintainability, and defines concrete actions to reduce probability and impact.

## 3. Risk Scoring Method
- Probability (P): 1 (very low) to 5 (very high)
- Impact (I): 1 (very low) to 5 (very high)
- Exposure (RE): P x I
- Priority bands:
  - High: RE >= 15
  - Medium: RE 8 to 14
  - Low: RE <= 7

## 4. Risk Register

| Risk ID | Category | Risk Description | P | I | RE | Early Triggers | Mitigation Plan | Monitoring Plan | Management / Contingency |
|---|---|---|---:|---:|---:|---|---|---|---|
| R-01 | Security | JWT misuse or leakage from local storage can enable session hijack | 3 | 5 | 15 | Unexpected multi-IP usage, auth anomalies | Reduce token lifetime, strengthen XSS hygiene, secure logout cleanup, plan cookie migration | Weekly auth log review and error pattern checks | Force token invalidation strategy and emergency secret rotation |
| R-02 | Data Integrity | Reaction counters diverge from reaction rows under edge toggles/switches | 3 | 4 | 12 | Count mismatch in UI versus DB state | Keep toggle logic centralized, add consistency checks in tests | Compare aggregate reaction rows to counters in test runs | Run corrective recount script and patch endpoint logic |
| R-03 | Performance | Timeline and discovery queries degrade with data growth | 3 | 4 | 12 | Increased response time, slower page load | Add indexes and pagination limits, optimize queries | Track endpoint latency in staging smoke checks | Enable pagination-first mode and defer heavy enrichments |
| R-04 | Functional Scope | Notifications are only partially implemented (UI icon without full service) | 4 | 3 | 12 | User expectation mismatch, repeated support queries | Mark clearly as partial scope in release notes and sprint goals | Review backlog and stakeholder feedback each sprint | Move full notifications to Sprint 3 with explicit acceptance criteria |
| R-05 | Integration | Frontend-backend contract drift for thread/reaction payloads | 3 | 4 | 12 | Runtime undefined fields, parsing errors | Keep shared API contract checklist before merge | API contract review on each PR touching schemas | Add adapter fallback and hotfix serialization |
| R-06 | Usability | Nested thread replies may become hard to read at large depth | 2 | 3 | 6 | User complaints about thread readability | Cap visual indent depth, improve thread UX cues | UX review after sprint demo feedback | Introduce collapsible subthreads |
| R-07 | Reliability | External Open Library ingestion failure can create inconsistent expectations | 2 | 3 | 6 | Empty enrichment in some runs | Keep ingestion best-effort and non-blocking | Startup logs review and fallback seed checks | Disable ingestion in unstable periods and rely on local seed |
| R-08 | Quality | Incomplete regression tests after sprint feature merges | 3 | 4 | 12 | Reopened bugs after release | Maintain sprint-level regression checklist for auth, timeline, thread, reactions | Test report review at sprint closure | Release patch window with rollback-ready build |
| R-09 | Deployment | Environment mismatch (CORS/API URL/env) breaks login/data calls | 3 | 4 | 12 | 401/CORS errors in QA, blank data cards | Standardize env templates and startup docs | Pre-demo smoke checklist for env variables | Quick environment rollback and config correction |
| R-10 | Team Process | Over-reliance on urgent fixes bypasses maintenance discipline | 2 | 4 | 8 | Frequent direct patches without tickets | Enforce ticket-first maintenance process | Weekly review of direct commits | Convert ad hoc fixes into tracked backlog items |
| R-11 | DB Evolution | Schema growth for threads/reactions without migrations risks data drift | 3 | 4 | 12 | Local DB mismatch between team members | Introduce migration scripts/versioning practice | Validate schema version in startup checklist | Provide migration fallback guide and DB reset protocol |
| R-12 | Privacy/Compliance | Notification feature expansion may introduce unreviewed user data exposure | 2 | 4 | 8 | New notification payloads include excess personal fields | Define minimum data policy before implementation | Review payload fields in API review | Roll back notification endpoints until sanitized |

## 5. Top Priority Risks (Immediate Attention)
1. R-01 (Security session risk)
2. R-02 (Reaction data consistency)
3. R-03 (Timeline/discovery performance)
4. R-04 (Notification scope gap)
5. R-08 (Regression quality risk)

## 6. Sprint-Wise RMMM Execution Plan

### Sprint 2 Closeout Actions
- Lock reaction regression tests (toggle, switch, counters)
- Validate thread reply depth rendering and creation flow
- Publish notification feature status clearly as partial
- Audit auth flow for token handling edge cases

### Sprint 3 Planned Risk Actions
- Implement full notification backend model + APIs
- Add migration/versioning workflow for schema updates
- Add pagination to timeline feed for scale safety
- Strengthen auth hardening and session handling

## 7. Roles and Ownership
- Risk owner (overall): Project lead
- Security risk owner: Backend lead
- UI/UX and contract drift owner: Frontend lead
- Test and bug history owner: QA/documentation lead

## 8. RMMM Review Cadence
- Weekly risk review during sprint
- Formal update at sprint end
- Immediate update when any high-risk trigger is observed

## 9. Summary
The project is currently in a growth-heavy phase where functionality evolves quickly. This RMMM plan focuses on controlled incremental maintenance, preventing sprint velocity from reducing product quality, and keeping risks visible and actionable.
