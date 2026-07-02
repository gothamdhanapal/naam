# Naam — Current Focus

> Session handover document for every ChatGPT / Cursor development session.

**Last updated:** v0.5.0 — First Intelligent Conversation

---

## What Naam Is

Naam (நாம் — *"We"* in Tamil) is an **AI Chief of Staff for families**.

It is not a task manager, calendar, or chatbot. Naam is a conversation-first operating layer that quietly understands family life, remembers context, plans actions, and executes deterministically.

**Core principle:** Intelligence before automation. Deterministic rules before AI inference. AI decides; software executes.

---

## Current Milestone

**M4 — Identity & Context Engine**

| PR | Status | Description |
|---|---|---|
| PR1 | ✅ Complete | Identity Agent — resolve sender from `family_members` |
| PR2 | ✅ Complete | Context Models — `ContextResult`, enums, participants |
| PR3 | ✅ Complete | Context Decision Matrix — deterministic scope/visibility rules |
| PR4 | ⏳ Next | Context Agent — produce `ContextResult` |
| PR5 | ⏳ Pending | Planning Agent v2 — consume context |

---

## Current Objective

**PR4 — Context Agent**

The Context Agent should consume

- `IdentityResult`
- Understanding output
- `ContextDecisionMatrix`

and produce

- `ContextResult`

without performing any persistence.

---

## What Is Already Working (v0.5.0)

The first intelligent conversation end-to-end:

```text
WhatsApp → Meta Webhook → InboxService → Understanding → Planning → Execution → Task
```

Completed foundation:

- FastAPI backend, Supabase, repository pattern
- Inbox pipeline with lifecycle statuses
- Understanding Agent (OpenAI)
- Planning Agent → Execution Engine → Task creation
- WhatsApp / Meta webhook integration
- Identity Agent (standalone, not wired)
- Context schemas and Context Decision Matrix (agent not built)

**91 automated tests passing.**

---

## Current Architecture

### Shipped pipeline

```text
WhatsAppService.handle_incoming_message()
    → InboxService.ingest_inbox()
        → persist_inbox()          [RECEIVED]
        → process_inbox_item()
            → understand_message()
            → PlanningAgent.plan()
            → ExecutionEngine.execute()
            → update_ai_result()   [PROCESSED]
```

### Target pipeline (M4)

```text
Ingest → IdentityAgent.resolve() → understand_message()
       → ContextAgent.build()     → PlanningAgent v2 → Execution
```

Layer rules (do not break):

```text
API → Services → Agents → Planning → Execution → Repositories → Supabase
```

---

## Next Implementation Steps

1. **PR4 — Context Agent**
   - Input: `IdentityResult`, understanding output, `ContextDecisionMatrix`
   - Output: `ContextResult`
   - Map matrix decisions to domain schema; no database writes

2. **PR5 — Planning Agent v2**
   - Accept optional `ContextResult`
   - Enrich task payloads with owner, scope, participants
   - Do not redesign Execution Engine

3. **Pipeline wiring**
   - Call `IdentityAgent` from processing path (after ingest, before understanding)
   - Call `ContextAgent` after understanding, before planning
   - Update tests; keep webhook resilience (persistence first, no HTTP 500 on AI failure)

---

## Engineering Principles

Read before every session:

- `docs/engineering/cursor_guidelines.md`
- `docs/engineering/coding_standards.md`
- `docs/13_naam_philosophy.md`
- `docs/14_naam_intelligence_model.md`

Non-negotiables:

- **Conversation-first** — families talk; Naam understands
- **Intelligence before automation** — understand and contextualize before acting
- **Deterministic rules before AI inference** — identity and context rules are code, not prompts
- **Repositories only touch Supabase** — agents never write to the database
- **Services own business logic** — agents produce structured output only
- **One PR, one concern** — no scope creep across milestones

---

## Do NOT Redesign

These are stable; extend, do not replace:

- Execution Engine and action registry
- Repository pattern and Supabase access rules
- Inbox lifecycle (`RECEIVED` → `PROCESSING` → `PROCESSED` / `FAILED`)
- WhatsApp webhook resilience model
- `InboxService` as single ingestion entry point
- Layer separation in `docs/02_system_architecture.md`

---

## Known Future Milestones

| Milestone | Focus |
|---|---|
| M2 | Family Memory — long-term knowledge graph |
| — | Event Creation |
| — | Routine Engine |
| — | Assignment Agent |
| — | Reminder Engine |
| — | Daily Digest |
| — | Flutter Mobile App |

See `docs/11_mvp_roadmap.md`.

---

## Start Every Session With

1. Read this document
2. Read `docs/03_project_status.md`
3. Read `docs/engineering/cursor_guidelines.md`
4. Check `todo.md` for remaining M4 work
5. Confirm the PR scope before writing code

**First prompt template:**

> I'm continuing development of Naam (AI Chief of Staff for families).
> Read `docs/16_current_focus.md` and `docs/03_project_status.md`.
> We are on M4 — Identity & Context Engine. Help me implement the next PR while keeping the architecture consistent.
