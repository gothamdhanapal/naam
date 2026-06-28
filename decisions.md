# Architectural Decisions

## Decision-001

Title

AI never writes directly to the database.

Status

Accepted

Reason

Keeps execution deterministic.

---

## Decision-002

Repositories are the only layer that access Supabase.

Status

Accepted

Reason

Separation of concerns.

---

## Decision-003

Prompts live outside business logic whenever possible.

Status

Accepted