# Naam - Project Status

## Current Version

v0.5.0

---

# Current Phase

First Intelligent Conversation Complete

---

# Current Milestone

M4 — Identity & Context Engine

---

# Project Health

🟢 On Track

---

# M4 Progress

- ✅ PR1 — Identity Agent
- ✅ PR2 — Context Models
- ⏳ PR3 — Context Decision Matrix
- ⏳ PR4 — Context Agent
- ⏳ PR5 — Planning Agent v2

---

# Completed Milestones

- ✅ FastAPI Backend
- ✅ Supabase Integration
- ✅ Understanding Agent
- ✅ Execution Engine
- ✅ Planning Agent
- ✅ Repository Layer
- ✅ Service Layer
- ✅ End-to-End Inbox Processing
- ✅ WhatsApp Integration
- ✅ Meta Webhook Integration
- ✅ Automatic Inbox Ingestion
- ✅ Automatic Task Creation from WhatsApp
- ✅ Identity Agent (M4 PR1)
- ✅ Context Models (M4 PR2)
- ✅ Automated Test Suite

---

# Current Capabilities

✅ Receive WhatsApp messages via Meta webhook

✅ Ingest messages into Inbox automatically

✅ Resolve inbox lifecycle (RECEIVED → PROCESSING → PROCESSED / FAILED)

✅ Understand messages using GPT

✅ Plan executable actions deterministically

✅ Create tasks in Supabase from WhatsApp conversations

✅ Persist AI understanding on inbox items

✅ Resolve sender identity deterministically (Identity Agent — not yet wired to pipeline)

✅ Context domain models defined (Context Agent — not yet implemented)

✅ Run automated tests without external services

---

# Current Architecture

## Shipped Pipeline (v0.5.0)

The first end-to-end intelligent conversation is working:

```text
WhatsApp Message
    ↓
Meta Webhook
    ↓
WhatsAppService
    ↓
InboxService.ingest_inbox()
    ↓
Understanding Agent
    ↓
Planning Agent
    ↓
Execution Engine
    ↓
TaskService → TaskRepository
    ↓
Supabase (tasks)
```

Example: *"Pay electricity bill tomorrow"* → task created automatically.

## Target Architecture (M4)

Naam is an AI Chief of Staff for families. Intelligence comes before automation. Deterministic rules resolve identity and context before AI inference drives planning.

```text
WhatsApp / Inbox
    ↓
Intake
    ↓
Identity Agent          ← PR1 complete (not wired)
    ↓
Understanding Agent
    ↓
Context Agent           ← PR2 models complete; PR4 pending
    ↓
Planning Agent v2       ← PR5 pending
    ↓
Execution Engine
    ↓
Supabase
```

See `docs/04_agent_architecture.md` and `docs/14_naam_intelligence_model.md`.

---

# Current Technology Stack

Backend

- FastAPI

Database

- Supabase PostgreSQL

Storage

- Supabase Storage

AI

- OpenAI Responses API

Integrations

- WhatsApp Cloud API (Meta webhook)

Language

- Python

Version Control

- Git + GitHub

Testing

- pytest (59 automated tests)

Hosting (Planned)

- Railway

---

# Next Steps (M4)

1. PR3 — Context Decision Matrix (deterministic scope, visibility, ownership rules)
2. PR4 — Context Agent (produce `ContextResult` from identity + understanding)
3. PR5 — Planning Agent v2 (consume context in planning decisions)
4. Wire Identity Agent into the inbox pipeline

See `docs/16_current_focus.md` for session handover details.

---

# Upcoming Milestones (Post-M4)

- Family Memory (M2)
- Event Creation
- Routine Creation
- Assignment Agent
- Reminder Engine
- Daily Digest
- Flutter Mobile Application

See `docs/11_mvp_roadmap.md` for the complete roadmap.

---

# Current Engineering Workflow

Design

↓

Architecture Review

↓

Implementation

↓

Testing

↓

Git Commit

↓

Documentation Update

↓

Project Status Update

---

# Known Technical Debt

- Temporary debug logging in task-creation path (remove after M4 stabilizes)
- Identity Agent and Context Agent not yet wired into processing pipeline
- `docs/05_domain_model.md` inbox lifecycle prose predates M3 enum values

Priority is completing M4 before expanding scope.

---

# Session Handover

Every new development session should start with:

- `docs/00_start_here.md`
- `docs/16_current_focus.md`
- `docs/engineering/cursor_guidelines.md`
