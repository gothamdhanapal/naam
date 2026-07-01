# Naam - Start Here

## Welcome

Welcome to the Naam project.

Naam (நாம்) means **"We"** in Tamil.

Naam is an AI-powered Family Chief of Staff designed to reduce the invisible mental load of running a family.

The system transforms everyday information into organized actions, remembers important context, plans actions, coordinates responsibilities, and continuously learns how a family operates.

This document is the starting point for anyone contributing to the project.

---

# Project Status

Current Version

v0.4.0

Current Phase

Foundation Complete

Current Milestone

Family Memory

See `docs/03_project_status.md` for the full status report.

---

# Project Philosophy

Naam is **not** another productivity application.

Naam is an operating layer for family life.

Every engineering decision should support one goal:

> Reduce the mental load of running a family.

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

### Engineering Playbook

docs/engineering/cursor_guidelines.md

docs/engineering/coding_standards.md

docs/engineering/review_checklist.md

docs/engineering/milestone_template.md

---

# Current Architecture

```text
Inbox
    ↓
Understanding Agent
    ↓
Planning Agent
    ↓
Execution Plan
    ↓
Execution Engine
    ↓
Services
    ↓
Repositories
    ↓
Supabase
```

OpenAI provides reasoning.

The Planning Agent produces execution plans.

The Execution Engine performs deterministic actions.

Repositories are the only layer allowed to access the database.

---

# Current Capabilities

✅ FastAPI Backend

✅ Supabase Integration

✅ Inbox API

✅ OpenAI Integration

✅ Understanding Agent

✅ Planning Agent

✅ Execution Engine

✅ Task Creation

✅ End-to-End Inbox Processing

✅ Automated Test Suite

✅ Project Documentation

---

# Current Milestone

**Family Memory (M2)**

Goal: Build Naam's long-term knowledge layer so context learned from one message is available for future planning and coordination.

See `docs/roadmap/M2_family_memory.md` for scope and acceptance criteria.

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

tests/

requirements.txt

main.py

changelog.md

decisions.md

todo.md

readme.md (project root)

---

# Development Principles

- AI decides.
- Software executes.
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

Naam becomes the trusted operational memory for every family.

Rather than acting as another application, Naam quietly understands, remembers, plans, coordinates and learns so families can spend less time managing life and more time living it.

---

# First Prompt for Every New Chat

"I'm continuing development of Naam.

Read `docs/00_start_here.md` and `docs/engineering/cursor_guidelines.md`.

Check `docs/03_project_status.md` for the current milestone.

We are currently working on the Family Memory milestone.

Help me design, review and implement the next feature while keeping the architecture consistent."

---

Last Updated

v0.4.0 — Execution Engine Foundation complete  
Family Memory milestone in progress
