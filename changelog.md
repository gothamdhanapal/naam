# Changelog

## v0.5.0 — First Intelligent Conversation

### Added

- WhatsApp Cloud API integration (`app/integrations/whatsapp/`)
- Meta webhook verification and message ingestion (GET/POST `/webhooks/whatsapp`)
- Resilient webhook handling (inbox persistence succeeds first; AI failures never cause HTTP 500)
- `InboxService` as single domain entry point (`persist_inbox`, `ingest_inbox`)
- Inbox lifecycle status (`RECEIVED`, `PROCESSING`, `PROCESSED`, `FAILED`)
- Identity Agent — deterministic sender resolution from `family_members` (M4 PR1)
- `FamilyMemberRepository` with normalized phone matching
- Context domain models — `ContextResult`, `Scope`, `Visibility`, `Relationship` (M4 PR2)
- SQL migrations for `inbox_status` enum and `tasks` table alignment
- Session handover document (`docs/16_current_focus.md`)

### Changed

- WhatsApp ingestion now calls `InboxService.ingest_inbox()` (full AI pipeline)
- `POST /inbox` uses `ingest_inbox()` instead of persist-only flow
- Agent architecture updated with Identity Agent and Context Agent positions

### Fixed

- Inbox status enum mismatch blocking WhatsApp ingestion
- Missing `tasks` table columns blocking task creation from pipeline

### Milestone Outcome

First end-to-end intelligent conversation working:

```text
WhatsApp → Inbox → Understanding → Planning → Execution → Task in Supabase
```

### Testing

- 59 automated tests passing
- No OpenAI dependency for tests
- No Supabase dependency for tests

---

## v0.4.0 — Execution Engine Foundation

### Added

- Deterministic Execution Engine
- Execution Action Registry
- Execution Bootstrap
- Task Domain Model
- Task Repository
- Task Service
- Planning Agent
- CreateTaskAction
- End-to-End Inbox Processing
- Automated Test Suite

### Testing

- 27 automated tests passing
- No OpenAI dependency for tests
- No Supabase dependency for tests

---

## v0.3.0

### Added

- FastAPI backend
- Supabase integration
- OpenAI Understanding Agent
- AI Processing Pipeline
- Architecture Documentation
