# Naam — Review Checklist

Use this checklist before every merge.

Designed to be completed in **under five minutes** for a typical pull request.

---

## Architecture

- [ ] Repositories are the only database layer
- [ ] Services contain business logic
- [ ] Agents produce structured output only — no database writes
- [ ] Planning Agent produces execution plans only — no execution
- [ ] Execution Engine performs actions — no OpenAI calls
- [ ] No layer bypasses another layer
- [ ] Dependencies are injected, not hardcoded
- [ ] New execution actions are registered in bootstrap

---

## Code Quality

- [ ] Type hints on all public functions and methods
- [ ] Pydantic models used for structured data
- [ ] Docstrings on public classes and methods
- [ ] No duplicated logic
- [ ] No business logic in repositories
- [ ] Small, focused modules
- [ ] No debug statements (`print`, temporary logs)
- [ ] No unused imports or dead code
- [ ] Readability over cleverness

---

## Testing

- [ ] Tests added or updated for the change
- [ ] `pytest` passes locally
- [ ] External dependencies mocked (OpenAI, Supabase)
- [ ] Tests are deterministic — no network calls
- [ ] Integration tests cover cross-layer flows where applicable

---

## Documentation

- [ ] Documentation updated if architecture changed
- [ ] Milestone documentation updated if milestone work completed
- [ ] API contracts updated if endpoints changed
- [ ] Changelog updated for releases
- [ ] No outdated version or milestone references introduced

---

## Security

- [ ] No secrets committed (`.env`, API keys, tokens)
- [ ] No credentials in logs or error messages
- [ ] Environment variables used for configuration
- [ ] No direct database access outside repositories

---

## Performance

- [ ] No unnecessary database round-trips
- [ ] No blocking calls in async paths without reason
- [ ] No unbounded queries (missing filters or limits where needed)

---

## Database

- [ ] Schema changes use version-controlled migrations
- [ ] Soft deletes preferred over hard deletes
- [ ] UUIDs used as primary keys
- [ ] Timestamps stored in UTC
- [ ] Repository methods return domain models

---

## API Compatibility

- [ ] Existing endpoints remain backward compatible
- [ ] Request/response schemas are documented
- [ ] Error responses follow the standard format
- [ ] No breaking changes without version discussion

---

## Quick Reject Criteria

Reject immediately if any of the following are true:

- Supabase accessed outside repositories
- Agent writes directly to the database
- Execution action contains business logic that belongs in a service
- Secrets or `.env` files in the diff
- Tests skipped for new behavior
- `print()` debug statements left in production code

---

## Reviewer Notes

| PR type | Focus areas |
|---|---|
| New execution action | Bootstrap registration, service injection, ActionResult handling, tests |
| New agent | Structured output only, no DB access, planning integration |
| New repository | CRUD mapping, domain models, mocked Supabase tests |
| New service | Business logic placement, repository delegation, DI |
| API change | Schema validation, no business logic in routes, API contracts doc |
| Milestone release | Changelog, project status, roadmap, readme |

---

**Reviewer:** _________________

**Date:** _________________

**Approved:** ☐ Yes  ☐ Changes requested
