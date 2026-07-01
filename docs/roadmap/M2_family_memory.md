# M2 — Family Memory

## Version

v0.5.0 (planned)

---

# Objective

Family Memory is Naam's long-term knowledge layer.

The Understanding Agent extracts meaning from incoming information. The Execution Engine performs actions. Family Memory preserves what Naam learns about a household over time so that context is available in future planning, assignment, and conversation.

Memory is not a separate product feature families manage manually. It is the accumulated understanding Naam builds as families use the system — schools, doctors, pets, preferences, and relationships that should inform future decisions without being re-explained.

---

# User Value

Families repeat the same context constantly: which school a child attends, who the family doctor is, where bills are paid, who handles groceries, what subscriptions renew each month.

Without memory, Naam would treat every message as if it were the first. Families would need to restate context repeatedly, and planning would remain shallow.

With Family Memory, Naam can:

- Recognize people, places, and routines already known to the household
- Produce more accurate plans because context is already available
- Reduce follow-up questions and repeated clarification
- Improve assignment, reminders, and digests over time

The result is a system that feels like it knows the family — not because users maintain a database, but because Naam remembers what it has already learned.

---

# Proposed Architecture

Family Memory sits between understanding and planning.

```text
Inbox
    ↓
Understanding Agent
    ↓
Memory Agent
    ↓
Knowledge Store
    ↓
Planning Agent (context-enriched)
    ↓
Execution Engine
```

High-level responsibilities:

- **Memory Agent** — Extract durable facts from structured understanding output and decide what should be remembered.
- **Knowledge Store** — Persist family memory through repositories; repositories remain the only database access layer.
- **Context Retrieval** — Supply relevant memory to the Planning Agent and future agents without exposing raw database access upstream.

Agents communicate through structured objects. Memory never bypasses services or repositories.

---

# Initial Scope

The first version of Family Memory should support structured knowledge about:

- Family Members
- Relationships
- Schools
- Doctors
- Pets
- Addresses
- Preferences
- Subscriptions

Each knowledge item belongs to a family and can be linked to the inbox items or understanding events that produced it.

---

# Acceptance Criteria

Milestone M2 is complete when:

1. **Knowledge persistence** — Family memory can be stored and retrieved per family through the repository layer.
2. **Memory extraction** — A Memory Agent can convert understanding output into structured knowledge candidates without writing to the database directly.
3. **Context enrichment** — The Planning Agent (or an upstream enrichment step) can receive relevant family memory when generating execution plans.
4. **Inbox integration** — Processing an inbox item can update family memory as part of the standard pipeline without bypassing agents, services, or repositories.
5. **Deterministic behavior** — Memory updates follow the same "AI decides, software executes" principle used by the Execution Engine.
6. **Test coverage** — Automated tests validate memory extraction, persistence, and retrieval without OpenAI or Supabase dependencies.
7. **Documentation** — Domain model, database design, and project status are updated to reflect the shipped memory capability.

---

# Implementation Tasks

_To be defined when M2 implementation begins._
