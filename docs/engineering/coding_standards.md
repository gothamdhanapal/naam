# Naam — Coding Standards

Engineering standards for the Naam backend.

These standards exist to keep the codebase consistent, testable, and understandable as the project grows from one milestone to the next.

---

## Python Style

**Why:** Consistent formatting reduces cognitive load and makes reviews faster.

- Follow **PEP 8** conventions.
- Use **`from __future__ import annotations`** in modules that use modern type syntax.
- Prefer **explicit imports** over wildcard imports.
- Keep lines readable; break long signatures and chains across lines.
- Use f-strings for string formatting.

**Example:**

```python
from __future__ import annotations

from uuid import UUID

from app.models.task import Task


def get_active_task(task_id: UUID) -> Task | None:
    """Return an active task or None if not found."""
    ...
```

**Avoid:**

```python
def get_active_task(task_id):  # missing type hints and docstring
    ...
```

---

## Naming Conventions

**Why:** Predictable names make navigation and search reliable across the codebase.

| Element | Convention | Example |
|---|---|---|
| Modules | `snake_case` | `task_repository.py` |
| Classes | `PascalCase` | `TaskRepository`, `PlanningAgent` |
| Functions / methods | `snake_case` | `create_task`, `list_by_family` |
| Constants | `UPPER_SNAKE_CASE` | `_TABLE = "tasks"` |
| Private members | Leading underscore | `_repository`, `_client` |
| Domain enums | `PascalCase` values | `TaskStatus.NEW` |
| Test files | `test_<module>.py` | `test_task_service.py` |
| Test functions | `test_<behavior>` | `test_create_task_delegates_to_repository` |

**Service methods** use business language (`delete_task`), while **repository methods** use persistence language (`soft_delete`).

---

## Folder Responsibilities

**Why:** Layer boundaries prevent architectural drift.

| Folder | Owns | Must not contain |
|---|---|---|
| `app/agents/` | AI reasoning, structured outputs | Database access, business workflows |
| `app/services/` | Business logic, orchestration | Direct Supabase calls |
| `app/repositories/` | CRUD, query mapping | Business rules, AI calls |
| `app/execution/` | Deterministic action execution | OpenAI calls, business logic |
| `app/models/` | Domain objects | HTTP or database transport details |
| `app/schemas/` | Input/output payloads | Business logic |
| `app/core/` | Config, shared clients | Feature-specific logic |
| `tests/` | Automated tests | Production code |

**Example — correct placement:**

```python
# app/services/task_service.py — business logic
class TaskService:
    def create_task(self, task: TaskCreate) -> Task:
        return self._repository.create(task)

# app/repositories/task_repository.py — persistence only
class TaskRepository:
    def create(self, task: TaskCreate) -> Task:
        response = self._client.table("tasks").insert(...).execute()
        return Task.from_row(response.data[0])
```

---

## Error Handling

**Why:** Naam separates AI uncertainty from deterministic execution. Errors must be handled at the right layer.

| Layer | Approach |
|---|---|
| **Agents** | Return structured output; let callers handle incomplete results |
| **Planning** | Return empty plans for unsupported input — do not raise |
| **Execution actions** | Return `ActionResult(success=False, ...)` for validation failures |
| **Services** | Raise domain-appropriate exceptions for unrecoverable failures |
| **Repositories** | Raise on empty persistence responses; return `None` for not-found |
| **API** | Translate exceptions into consistent HTTP error responses |

**Example — execution action (in-band failure):**

```python
try:
    task_create = TaskCreate.model_validate(action.payload)
except ValidationError as exc:
    return ActionResult(
        success=False,
        action_type=ActionType.CREATE_TASK,
        error="Invalid CREATE_TASK payload.",
        metadata={"validation_errors": exc.errors()},
    )
```

**Example — repository (persistence failure):**

```python
if not response.data:
    raise RuntimeError("Failed to create task: empty response from Supabase.")
```

---

## Dependency Injection

**Why:** Injection makes layers testable and keeps wiring centralized.

- Pass dependencies through **constructors**.
- Use **optional defaults** that resolve to production implementations.
- Wire dependencies in **bootstrap** or **service factories** — not inside agents.
- Tests inject **mocks** via the same constructor parameters.

**Example:**

```python
class TaskService:
    def __init__(self, repository: TaskRepository | None = None) -> None:
        self._repository = repository or TaskRepository()


class CreateTaskAction(BaseAction):
    def _get_task_service(self) -> TaskService | None:
        service = self.dependencies.get("task_service")
        if not isinstance(service, TaskService):
            return None
        return service
```

**Avoid:**

```python
from app.core.supabase import supabase  # inside a service or agent

class TaskService:
    def create_task(self, task):
        supabase.table("tasks").insert(...)  # bypasses repository
```

---

## Testing Expectations

**Why:** Naam's architecture is designed for independent layer testing.

- Use **pytest** with **pytest-asyncio** for async code.
- **Mock repositories and external services** — no real OpenAI or Supabase in unit tests.
- Organize tests to mirror source structure:

```text
tests/
├── execution/
├── services/
└── integration/
```

- Each layer gets **unit tests**; cross-layer flows get **integration tests**.
- Tests must be **deterministic** — no network calls, no randomness.
- Name tests after **behavior**, not implementation.

**Example:**

```python
def test_create_task_delegates_to_repository(
    task_service: TaskService,
    mock_repository: MagicMock,
) -> None:
    payload = TaskCreate(family_id=FAMILY_ID, title="Pay bill")
    task_service.create_task(payload)
    mock_repository.create.assert_called_once_with(payload)
```

Run tests from `backend/`:

```bash
pytest
```

---

## Logging

**Why:** Family workflows span multiple layers. Traceability matters for debugging production issues.

- Log at **service and execution** boundaries — not inside repositories.
- Include **action type**, **resource id**, and **family id** where relevant.
- Use structured, readable messages.
- Do not log secrets, tokens, or full message content in production paths.
- Prefer Python's `logging` module over `print()`.

**Example:**

```python
logger.info("Executing plan with %d actions", len(plan.actions))
```

**Avoid:**

```python
print("DEBUG:", result)  # remove before merging
```

---

## Configuration

**Why:** Secrets and environment-specific values must never be hardcoded.

- All configuration lives in `app/core/config.py` via **Pydantic Settings**.
- Secrets are loaded from **environment variables** or `.env` (local only).
- Never commit `.env`, API keys, or Supabase service role keys.
- Access settings through the shared `settings` object — not `os.environ` scattered across modules.

**Example:**

```python
from app.core.config import settings

client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
```

---

## Database Access

**Why:** A single persistence layer prevents inconsistent data access and makes testing possible.

- **Only repositories** import Supabase or execute SQL.
- Repositories return **domain models**, not raw dicts, whenever possible.
- Use **soft deletes** (`deleted_at`) instead of hard deletes unless explicitly required.
- All timestamps in **UTC**.
- Primary keys are **UUIDs**.
- Schema changes require **version-controlled SQL migrations** — never manual production edits.

**Example:**

```python
class TaskRepository:
    def soft_delete(self, task_id: UUID) -> Task | None:
        response = (
            self._client.table("tasks")
            .update({"deleted_at": now, "updated_at": now})
            .eq("id", str(task_id))
            .is_("deleted_at", "null")
            .execute()
        )
        ...
```

---

## Documentation Standards

**Why:** Naam is built by humans and AI assistants. Documentation is the shared contract.

- Update docs **alongside code**, not after.
- Architecture changes require updates to `docs/03_project_status.md`.
- New milestones use `docs/engineering/milestone_template.md`.
- Releases update `backend/changelog.md`.
- Public APIs are documented in `docs/08_api_contracts.md`.
- Docstrings explain **why** for non-obvious behavior, not what is already clear from the code.

**When to update documentation:**

| Change | Update |
|---|---|
| New execution action | Bootstrap, changelog, project status |
| New agent | Agent architecture doc, roadmap |
| New API endpoint | API contracts, readme |
| Milestone complete | Changelog, project status, roadmap |
| Architectural decision | `decisions.md` |

---

## Summary

These standards exist so Naam remains:

- **Predictable** — same patterns everywhere
- **Testable** — every layer mocked independently
- **Safe** — AI proposes, software executes, repositories persist
- **Readable** — a new contributor understands the system quickly

When in doubt, read `docs/engineering/cursor_guidelines.md` and follow the layer that matches your change.
