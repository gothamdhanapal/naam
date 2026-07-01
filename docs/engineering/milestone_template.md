# Milestone Template

Reusable template for Naam milestones.

Copy this file into `docs/roadmap/` and rename it (for example, `M3_event_creation.md`) when starting a new milestone.

---

# Milestone

**ID:** M_  
**Version:** v0._._ (planned)  
**Status:** Planned | In Progress | Complete

---

# Vision

Describe what this milestone enables for Naam and for families.

What capability exists after this milestone that did not exist before?

---

# User Value

Explain how this milestone reduces the mental load of running a family.

What becomes easier, faster, or more automatic for the user?

---

# Problem Statement

What problem does this milestone solve?

Why is it the right next step after the previous milestone?

---

# Success Criteria

Define the measurable outcomes that indicate success.

Examples:

- A specific user action produces a specific system result
- A pipeline stage is fully wired end-to-end
- Test coverage exists for the new capability

---

# Architecture

Describe the high-level architecture for this milestone.

Include a diagram showing where the new capability fits in the existing pipeline.

```text
[Existing flow]
    ↓
[New component]
    ↓
[Existing flow continues]
```

Rules:

- No implementation details in this section
- Show layer placement (agent, service, repository, execution)
- Identify which existing components are extended vs. newly created

---

# Deliverables

List the concrete outputs of this milestone.

Examples:

- New agent
- New repository
- New execution action
- New service
- API endpoint
- Test suite
- Documentation updates

---

# Tasks

Break the milestone into implementation tasks.

Leave empty until implementation begins.

- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

---

# Risks

Identify risks and mitigations.

| Risk | Impact | Mitigation |
|---|---|---|
| Example: AI output inconsistency | Plans fail validation | Strict schema validation, graceful empty plans |
| | | |

---

# Testing Strategy

Define how this milestone will be tested.

- Unit tests per layer
- Integration tests for end-to-end flows
- Mocking strategy (OpenAI, Supabase)
- Acceptance test scenarios

---

# Acceptance Criteria

Define what makes the milestone **complete**.

Use checkboxes that can be verified objectively.

1. [ ] Criterion 1
2. [ ] Criterion 2
3. [ ] Criterion 3
4. [ ] Automated tests pass without external services
5. [ ] Documentation updated

---

# Documentation Updates

List the documents that must be updated when this milestone ships.

- [ ] `backend/changelog.md`
- [ ] `docs/03_project_status.md`
- [ ] `readme.md`
- [ ] Relevant architecture docs
- [ ] API contracts (if applicable)
- [ ] Roadmap (mark complete, define next milestone)

---

# Release Notes

Draft release notes for the changelog.

### Added

- Item 1
- Item 2

### Testing

- N automated tests passing
- No OpenAI dependency for tests
- No Supabase dependency for tests

---

# Future Extensions

Describe capabilities this milestone enables but does not implement.

What becomes possible after this milestone is complete?

What should **not** be built in this milestone to keep scope focused?
