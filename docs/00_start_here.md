# Naam - Start Here

## Welcome

Welcome to the Naam project.

Naam (நாம்) means **"We"** in Tamil.

Naam is an **AI Chief of Staff for families** — a conversation-first operating layer designed to reduce the invisible mental load of running a household.

The system transforms everyday conversations into organized actions, remembers important context, plans intelligently, coordinates responsibilities, and continuously learns how a family operates.

This document is the starting point for anyone contributing to the project.

---

# Project Status

Current Version

v0.5.0 — First Intelligent Conversation

Current Phase

First Intelligent Conversation Complete

Current Milestone

M4 — Identity & Context Engine

See `docs/03_project_status.md` for the full status report.

See `docs/16_current_focus.md` for session handover.

---

# Project Philosophy

Naam is **not** another productivity application.

Naam is an AI Chief of Staff — an operating layer for family life.

Every engineering decision should support one goal:

> Reduce the mental load of running a family.

Guiding principles:

- **Conversation-first** — families talk; Naam understands
- **Intelligence before automation** — understand and contextualize before acting
- **Deterministic rules before AI inference** — identity and context are resolved in code, not prompts

See `docs/13_naam_philosophy.md` and `docs/14_naam_intelligence_model.md`.

---

# Read These Documents First

The documentation is intentionally ordered.

Read them in sequence.

01_product_vision.md

02_system_architecture.md

03_project_status.md

04_agent_architecture.md

05_domain_model.md

06_execution_engine.md

07_database_design.md

08_api_contracts.md

09_backend_structure.md

10_engineering_principles.md

11_mvp_roadmap.md

12_family_operating_model.md

13_naam_philosophy.md

14_naam_intelligence_model.md

16_current_focus.md

### Engineering Playbook

docs/engineering/cursor_guidelines.md

docs/engineering/coding_standards.md

docs/engineering/review_checklist.md

docs/engineering/milestone_template.md

---

# Current Architecture

## Shipped (v0.5.0)

```text
WhatsApp → Meta Webhook → InboxService → Understanding → Planning → Execution → Task
```

## Target (M4)

```text
Inbox / WhatsApp
    ↓
Identity Agent          (deterministic)
    ↓
Understanding Agent     (AI)
    ↓
Context Agent           (deterministic rules)
    ↓
Planning Agent v2
    ↓
Execution Engine
    ↓
Repositories → Supabase
```

OpenAI provides reasoning for understanding.

Deterministic agents and rules handle identity and context.

The Planning Agent produces execution plans.

The Execution Engine performs deterministic actions.

Repositories are the only layer allowed to access the database.

---

# Current Capabilities

✅ FastAPI Backend

✅ Supabase Integration

✅ WhatsApp / Meta Webhook Integration

✅ Automatic Inbox Ingestion

✅ Inbox Lifecycle (RECEIVED → PROCESSING → PROCESSED / FAILED)

✅ OpenAI Understanding Agent

✅ Planning Agent

✅ Execution Engine

✅ Automatic Task Creation from WhatsApp

✅ Identity Agent (M4 PR1 — not yet wired to pipeline)

✅ Context Models (M4 PR2)

✅ End-to-End Intelligent Conversation

✅ Automated Test Suite (59 tests)

✅ Project Documentation

---

# Current Milestone

**M4 — Identity & Context Engine**

| PR | Status |
|---|---|
| PR1 Identity Agent | ✅ |
| PR2 Context Models | ✅ |
| PR3 Context Decision Matrix | ⏳ |
| PR4 Context Agent | ⏳ |
| PR5 Planning Agent v2 | ⏳ |

See `docs/16_current_focus.md` and `todo.md`.

---

# Engineering Workflow

Every feature follows the same lifecycle.

1. Design
2. Implement
3. Test
4. Review (use `docs/engineering/review_checklist.md`)
5. Commit
6. Update Documentation
7. Update Project Status

Repeat.

---

# Repository Structure

backend/

app/

docs/

docs/engineering/

docs/roadmap/

migrations/

tests/

requirements.txt

main.py

changelog.md

decisions.md

todo.md

readme.md (project root)

---

# Development Principles

- Conversation-first interface
- Intelligence before automation
- Deterministic rules before AI inference
- AI decides. Software executes.
- Repositories own persistence.
- Services own business logic.
- Agents own reasoning.
- Documentation is updated alongside code.
- Simplicity is preferred over cleverness.
- Every architectural decision should scale.

See `docs/engineering/cursor_guidelines.md` for permanent AI assistant instructions.

---

# Before Starting Any New Feature

Understand the user problem.

Review `docs/16_current_focus.md`.

Review the relevant architecture document.

Read `docs/engineering/cursor_guidelines.md`.

Design before coding.

Keep responsibilities separated.

Write readable code.

Test independently.

Commit meaningful milestones.

Update `docs/03_project_status.md`.

---

# Long-Term Vision

Naam becomes the trusted Chief of Staff for every family.

Rather than acting as another application, Naam quietly understands, remembers, plans, coordinates and learns so families can spend less time managing life and more time living it.

---

# First Prompt for Every New Chat

"I'm continuing development of Naam — an AI Chief of Staff for families.

Read `docs/16_current_focus.md`, `docs/00_start_here.md`, and `docs/engineering/cursor_guidelines.md`.

Check `docs/03_project_status.md` for the current milestone.

We are on M4 — Identity & Context Engine. Help me design, review and implement the next PR while keeping the architecture consistent."

---

Last Updated

v0.5.0 — First Intelligent Conversation complete  
M4 — Identity & Context Engine in progress
