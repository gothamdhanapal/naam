# Naam — Cursor Guidelines

Permanent instructions for Cursor and other AI coding assistants contributing to Naam.

Read this document at the start of every session before writing or modifying code.

---

## Project Philosophy

Naam is an AI-powered Family Chief of Staff.

Naam (நாம்) means **"We"** in Tamil.

**Primary goal:** Reduce the invisible mental load of running a family.

Naam is not another productivity app. It is an operating layer for family life that understands incoming information, remembers context, plans actions, and coordinates responsibilities.

Every feature should answer one question:

> Does this make family life simpler?

If the answer is no, it does not belong in Naam.

---

## Core Principle

**AI decides. Software executes.**

- AI agents propose structured understanding and execution plans.
- The Execution Engine performs deterministic actions.
- Repositories persist the results.

Never blur these responsibilities.

---

## Architecture Rules

```text
API
    ↓
Services
    ↓
Agents
    ↓
Planning
    ↓
Execution
    ↓
Repositories
    ↓
Supabase
```

### Rules

| Rule | Meaning |
|---|---|
| Never bypass repositories | All database reads and writes go through `app/repositories/` |
| Services own business logic | Validation, orchestration, and side effects live in `app/services/` |
| Agents never write to the database | Agents produce structured output only |
| Planning produces execution plans only | The Planning Agent returns `ExecutionPlan` objects — it does not execute |
| Execution performs deterministic actions | The Execution Engine runs registered handlers — it does not call OpenAI |
| Repositories are the only persistence layer | No Supabase imports outside repositories |
| Use dependency injection | Pass dependencies via constructors; avoid global state in business logic |
| Prefer composition over inheritance | Small, focused classes composed together |
| Keep responsibilities separated | One module, one purpose |

### What each layer does

- **API** — HTTP endpoints, request validation, response formatting. No business logic.
- **Services** — Workflow orchestration. Coordinates agents, execution, and repositories.
- **Agents** — AI reasoning. Returns structured Pydantic models or dicts.
- **Planning** — Converts understanding into `ExecutionPlan` actions.
- **Execution** — Runs actions deterministically via registered handlers.
- **Repositories** — CRUD and query operations against Supabase.

No layer may skip another layer.

---

## Coding Expectations

- **Type hints everywhere** — All function signatures and public attributes are typed.
- **Pydantic models** — Use Pydantic for schemas, domain models, and agent outputs.
- **Clear docstrings** — Public classes and methods include docstrings explaining purpose and behavior.
- **Small focused classes** — Prefer one responsibility per class or module.
- **SOLID principles** — Especially single responsibility and dependency inversion.
- **Readability over cleverness** — Code should be understandable by a new engineer within one day.
- **No duplicated logic** — Extract shared behavior; do not copy-paste across layers.
- **No business logic inside repositories** — Repositories map data; services decide.
- **Keep modules cohesive** — Files belong in the folder that matches their layer.

### File placement

| Folder | Purpose |
|---|---|
| `app/agents/` | AI agents |
| `app/services/` | Business logic and orchestration |
| `app/repositories/` | Database access |
| `app/execution/` | Execution engine, actions, bootstrap |
| `app/models/` | Domain models |
| `app/schemas/` | Input/output schemas |
| `app/core/` | Configuration, clients, shared infrastructure |
| `tests/` | Automated tests |

---

## Before Completing Any Task

Verify the following before marking work complete:

- [ ] **Tests pass** — Run `pytest` from `backend/`.
- [ ] **Imports are clean** — No unused imports.
- [ ] **No unused code** — Remove dead functions, variables, and files.
- [ ] **No debug statements** — Remove `print()`, temporary logging, and commented-out code.
- [ ] **Documentation updated** — If architecture, APIs, or milestones changed, update the relevant docs.

### Additional checks for architectural changes

- [ ] Repositories remain the only Supabase access point.
- [ ] New execution actions are registered in bootstrap.
- [ ] Services are injected — not instantiated inside agents or actions.
- [ ] Tests mock external dependencies (OpenAI, Supabase).

---

## Reference Documents

| Document | Purpose |
|---|---|
| `docs/engineering/coding_standards.md` | Detailed engineering standards |
| `docs/engineering/review_checklist.md` | Pre-merge review checklist |
| `docs/engineering/milestone_template.md` | Template for future milestones |
| `docs/16_current_focus.md` | Session handover — start every new chat here |
| `docs/00_start_here.md` | Project entry point |
| `docs/03_project_status.md` | Current version and milestone status |
| `docs/roadmap/` | Milestone specifications |

---

## Default Assumption for New Sessions

When starting a new chat:

1. Read `docs/16_current_focus.md` for session handover.
2. Read `docs/00_start_here.md` as the entry point.
3. Read `docs/engineering/cursor_guidelines.md` (this document).
4. Check `docs/03_project_status.md` for the current milestone.
5. Follow the architecture rules without being re-told.

Current version: **v0.5.0** — First Intelligent Conversation.

Current milestone: **M4 — Identity & Context Engine**.

See `docs/16_current_focus.md` and `todo.md` for remaining PRs.
