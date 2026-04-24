# FJ3 Test Case Report and Bug History (Sprint 1 + Sprint 2)

## 1. Scope
This report covers functional testing done for Dialogus up to Sprint 2.

- Sprint 1:
  - Signup and login
  - Home discovery
  - Browse and book detail
  - Basic access control
- Sprint 2:
  - Timeline feed
  - Appreciation reactions (like, dislike, recommend)
  - Discussion thread and nested replies
  - Notification icon (UI placeholder)

## 2. Test Environment
- Frontend: Next.js local dev setup
- Backend: FastAPI local run and Docker run
- Database: SQLite seeded data
- Browser used: Chrome

## 3. Functional Test Cases Summary

Detailed entries are in the Excel file:
- documents/FJ3_Functional_Test_Cases.xlsx

Quick summary:
- Sprint 1 test cases executed: 10
- Sprint 2 test cases executed: 11
- Main focus in Sprint 2 testing: timeline updates, reaction switching, nested thread replies

## 4. Bug History Report

Note: Bug IDs are kept exactly the same as in the Excel sheet.

| Bug ID | Sprint | Title | Module | Root Cause | Fix | Status |
|---|---|---|---|---|---|---|
| BUG_001 | Sprint 1 | Signup duplicate validation issue | Signup | Duplicate-email flow was not handled cleanly in one path | Added strict duplicate check before user creation | Closed |
| BUG_002 | Sprint 1 | Login auth mismatch | Login | Verification branch failed for a valid credential scenario | Fixed auth verification logic and session setup | Closed |
| BUG_003 | Sprint 1 | Discovery payload inconsistency | Home discovery | Frontend mapping mismatch for one response case | Aligned response mapping and UI fallback | Closed |
| BUG_004 | Sprint 1 | Browse search stale state | Browse | Query state refresh issue in one flow | Updated state handling on query changes | Closed |
| BUG_005 | Sprint 2 | Timeline stale render | Timeline feed | One render path did not refresh after search update | Unified timeline state update logic | Closed |
| BUG_006 | Sprint 2 | Reaction switch count mismatch | Appreciation system | Counter update logic missed one switch path | Centralized reaction switching and counter update | Closed |
| BUG_007 | Sprint 2 | Nested reply depth issue | Thread engine | Parent-depth calculation was incomplete | Added proper parent-chain depth calculation | Closed |

## 5. Defect Trend Summary
- Total bugs tracked till Sprint 2: 7
- Closed: 7
- Open: 0
- Most common issue area in Sprint 2: state update edge cases

## 6. Screenshot Handling

For submission, do this simple approach:

1. Take screenshots only for failed runs and retest pass runs.
2. Use filenames exactly like the Excel sheet format: SS_001.png, SS_002.png, SS_003.png.
3. Create one folder named documents/test_case_screenshots and keep all images there.
4. In the Excel Screenshot column, enter only filename (example: SS_005.png), not full path.
5. If a test case passed directly with no bug, you can keep Screenshot cell as N/A.

## 7. Conclusion
Sprint 1 baseline features are stable. Sprint 2 features are integrated and tested, with reaction and thread issues fixed during development and verified in retest.
