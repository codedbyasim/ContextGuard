# ContextGuard — Requirements Traceability Matrix (RTM)

This matrix maps the requirements defined in the `ContextGuard_SRS_document.md` to the implemented software components and tests to verify coverage and compliance.

## Functional Requirements (FR)

| Req ID | Description | Status | Implemented In | Verification / Test |
|--------|-------------|--------|----------------|---------------------|
| **FR-1.1** | Connect to Google Workspace API to get OAuth apps | ⏳ Pending | `backend/google_workspace.py` (Stubbed) | Dashboard integration pending |
| **FR-1.2** | Extract app name, publisher, scopes, users | ⏳ Pending | `backend/google_workspace.py` | Dashboard integration pending |
| **FR-1.3** | Seed IOC list and flag CRITICAL apps | ✅ Complete | `backend/database.py` (`init_db`) | Verified via SQLite inspection |
| **FR-1.4** | Send app details to Gemini Risk Engine for score | ⏳ Pending | `backend/main.py` (`/api/scan`) | API endpoint created, frontend trigger pending |
| **FR-1.5** | Trigger re-scan on demand via dashboard | ⏳ Pending | `backend/main.py` | Requires Frontend F4 |
| **FR-1.6** | Allow admin to manually add new IOC entries | ⏳ Pending | `backend/main.py` | Requires Frontend F4 |
| **FR-1.7** | Automatic background scans on schedule | ⏳ Pending | Planned for `backend/main.py` | Requires Frontend F4 / Cron |

---

## Core Features (F)

| Feature ID | Name | Status | Implemented In | Verification / Test |
|------------|------|--------|----------------|---------------------|
| **F1** | OAuth Risk Scanner | ⏳ Partial | `backend/database.py`, `backend/main.py` | Database schema ready, scan loop pending. |
| **F2** | Lobster Trap DPI Layer | ✅ Complete | `lobster/configs/default_policy.yaml`, `lobster/webhook_bridge.py` | Verified via `simulate_traffic.py` & `test_dpi_pipeline.py`. 11/11 tests pass. |
| **F3** | Gemini Risk Engine | ✅ Complete | `backend/main.py` (`analyze_event_with_gemini`) | Verified. Successfully classifying and logging events to `dpi_events` table. |
| **F4** | Security Dashboard | ⏳ Pending | `frontend/` (React) | Not started. |

---

## Non-Functional Requirements (NFR)

| Req ID | Description | Target | Status | Implemented In | Verification |
|--------|-------------|--------|--------|----------------|--------------|
| **NFR-1.1** | Lobster Trap mean added latency per LLM call | < 200ms | ✅ Met | Lobster proxy binary | Verified ~15-25ms latency via `test_nfr_latency_under_200ms` |
| **NFR-1.2** | Gemini risk score returned per OAuth app | < 5s | ✅ Met | `backend/main.py` | Verified during simulated webhook processing |
| **NFR-1.3** | Dashboard data refresh cycle (polling) | 10s | ⏳ Pending | `frontend/src/` | Will verify when frontend is built |
| **NFR-1.4** | Compliance report generation time | < 15s | ⏳ Pending | `backend/main.py` | API endpoint exists, awaiting UI integration |
| **NFR-1.5** | OAuth scan completion for 50 apps | < 2m | ⏳ Pending | `backend/google_workspace.py` | Pending OAuth implementation |
| **NFR-1.6** | Dashboard initial page load time | < 3s | ⏳ Pending | `frontend/src/` | Pending frontend build |
