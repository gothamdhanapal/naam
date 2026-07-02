# Context Agent Design

> Architectural specification for the Context Agent (M4 PR4).

Version: v0.2

Status: Design complete — PR4A

Milestone: M4 — Identity & Context Engine

Implementation: PR4B (not started)

---

# 1. Purpose

The Context Agent transforms conversational understanding into organizational understanding.

Understanding answers **"What did they say?"**

Context answers **"What does this mean for the family?"**

The Context Agent sits between AI interpretation and planning. It receives structured meaning from the Understanding Agent and structured identity from the Identity Agent, then produces a single organizational view — `ContextResult` — that downstream agents can rely on.

The Context Agent determines

- Who is speaking

- What scope the conversation belongs to

- Who owns the commitment

- Who is responsible (when explicitly known)

- Who participates or is interested

- How visible the information should be

- What follow-up strategy Naam should consider

It does **not** perform planning or execution.

It does **not** decide what tasks to create, when to remind, or how to persist data.

Context organizes. Planning decides. Execution executes.

---

# 2. Responsibilities

## The Context Agent MUST

- Validate incoming `ContextRequest` fields
- Assemble `DecisionInput` for the Context Decision Matrix
- Invoke `ContextDecisionMatrix.evaluate()`
- Map `ContextDecision` into `ContextResult`
- Merge identity from `IdentityResult`
- Merge entities and metadata from understanding and conversation context
- Return deterministic organizational context
- Prefer partial results with lower confidence over pipeline failure
- Remain independently testable with no external services

## The Context Agent MUST NOT

- Call OpenAI or any external AI service
- Write to the database
- Query repositories
- Execute actions
- Create tasks, events, or reminders
- Perform planning
- Update memory
- Schedule follow-ups
- Modify inbox or conversation records

All persistence, planning, and execution remain the responsibility of Services, the Planning Agent, and the Execution Engine.

---

# 3. Position in Architecture

## Pipeline placement

```text
Conversation
    ↓
Identity Agent          → IdentityResult
    ↓
Understanding Agent     → UnderstandingResult
    ↓
Context Agent           → ContextResult
    ↓
Planning Agent          → ExecutionPlan
    ↓
Execution Engine        → deterministic actions
```

## Why Context exists between Understanding and Planning

Understanding extracts meaning from language. It does not know how that meaning should be organized for a family.

Planning converts organizational context into actions. It should not re-derive scope, ownership, visibility, or participants — those are organizational decisions, not planning decisions.

Context is the boundary between **interpretation** and **action**.

Without Context, Planning would need to infer family structure, ownership, and visibility from raw understanding output. That would blur responsibilities and make the system harder to test.

Context ensures that

- AI interprets language (Understanding)
- Deterministic policies organize meaning (Context Decision Matrix)
- The Context Agent orchestrates and publishes the result (Context Agent)
- Planning consumes a complete organizational view (Planning Agent v2)

This matches the Policy Layer defined in `docs/14_naam_intelligence_model.md`.

---

# 4. Input Contract

## ContextRequest

The Context Agent accepts a single request object. Services assemble this object from upstream agents and conversation metadata before calling the Context Agent.

A single request object is preferred over multiple method parameters because

- The input surface grows as Naam matures (memory, calendar, preferences)
- Services can enrich the request without changing the agent signature
- Tests can construct one fixture object per scenario
- The agent API remains stable across PR4B and future intelligence layers

## Proposed fields

| Field | Type | Required | Description |
|---|---|---|---|
| `identity` | `IdentityResult` | Yes | Resolved speaker from Identity Agent |
| `understanding` | `UnderstandingResult` | Yes | Structured meaning from Understanding Agent |
| `family_members` | `list[FamilyMemberRef]` | No | Lightweight family roster for participant and scope rules |
| `conversation_id` | `UUID \| None` | No | Stable reference to the originating conversation or inbox item |
| `source` | `str \| None` | No | Channel origin (e.g. `whatsapp`, `email`, `manual`) |
| `received_at` | `datetime \| None` | No | When the message was received |
| `family_id` | `UUID \| None` | No | Family scope for future multi-tenant routing |
| `metadata` | `dict[str, Any]` | No | Opaque extension bag for future enrichment |

### IdentityResult

Resolved speaker identity. Defined in `app/schemas/identity.py`.

| Field | Description |
|---|---|
| `family_member_id` | Matched family member, or `None` if unknown |
| `name` | Display name when known |
| `role` | Family role (e.g. `parent`, `child`) when known |
| `phone_number` | Normalized sender phone number |
| `confidence` | Identity resolution confidence |

### UnderstandingResult

Structured meaning from the Understanding Agent. Defined in `app/schemas/understanding.py` today; may gain optional fields over time.

| Field | Description |
|---|---|
| `type` | Classification (`TASK`, `EVENT`, `NOTE`, etc.) |
| `title` | Human-readable summary of what was said |
| `due_date` | Extracted due date string, if any |
| `confidence` | Understanding confidence score |

**Mapping note:** The Context Agent maps `UnderstandingResult` into `UnderstandingContext` (internal to the Decision Matrix). Optional understanding fields not yet present on `UnderstandingResult` — such as `entities`, `scope_hint`, `owner_id`, `responsible_id`, `about_member_id` — may be supplied via `ContextRequest.metadata` until the Understanding Agent schema is extended. PR4B must document the adapter mapping explicitly.

### FamilyMemberRef

Lightweight family member reference for deterministic policies. Defined in `app/context/models.py`.

| Field | Description |
|---|---|
| `family_member_id` | Member UUID |
| `name` | Optional display name |
| `role` | Optional role string used by participant rules |

### Conversation metadata

`conversation_id`, `source`, `received_at`, and `family_id` are not consumed by the Decision Matrix today. They are carried on `ContextRequest` so the Context Agent can attach traceability metadata to `ContextResult` without querying repositories.

### Future extension points on ContextRequest

Future intelligence may add optional sections to `ContextRequest` without changing the agent method signature

- `memory_hints` — observational patterns from Family Memory
- `relationship_graph` — inferred relationships between members
- `calendar_context` — upcoming events affecting urgency
- `location_context` — place-based signals
- `routine_context` — recurring schedule matches
- `preference_context` — member or family preferences

These enrich `DecisionInput` construction or metadata only. They do not replace the Decision Matrix.

---

# 5. Output Contract

## ContextResult

The Context Agent produces `ContextResult` — the organizational view of a conversation for downstream planning.

PR2 introduced a baseline schema in `app/schemas/context.py`. PR4B extends it to the complete contract below while preserving existing enums and participant models.

## Complete contract

| Field | Type | Description |
|---|---|---|
| `speaker` | `IdentityResult` | Who sent the message |
| `scope` | `Scope` | Mental model: `PERSONAL`, `FAMILY`, `DEPENDENT`, `EXTERNAL` |
| `owner_id` | `UUID \| None` | Person who owns the commitment; `None` when family-owned or unassigned |
| `responsible_id` | `UUID \| None` | Person explicitly responsible for action; never inferred without evidence |
| `participants` | `list[ContextParticipant]` | Members involved with explicit `Relationship` roles |
| `visibility` | `Visibility` | Who may see derived information |
| `follow_up_action` | `FollowUpAction` | Recommended follow-up strategy from policy layer |
| `confidence` | `float` | Overall context confidence (0.0–1.0) |
| `reason_codes` | `list[str]` | Deterministic trace of policy outcomes for debugging and explainability |
| `related_entities` | `list[str]` | Entities the conversation relates to (Home, Daughter, Bruno, etc.) |
| `metadata` | `dict[str, Any]` | Traceability and extension data (conversation id, source, timestamps) |

### Field explanations

**speaker**

Copied from `ContextRequest.identity`. Context always preserves who spoke, even when identity confidence is low.

**scope**

From `ContextDecision.scope`. Determines which mental model applies — personal, family, dependent, or external.

**owner_id**

From `ContextDecision.ownership.owner_id`. When `None`, the commitment is family-owned or not yet assigned to a person. This is intentional and valid.

**responsible_id**

> **PR4B schema addition.** Not present on the PR2 `ContextResult` model today.

From `ContextDecision.ownership.responsible_person_id`. Distinct from ownership. A child may own a vaccination appointment while no responsible person is assigned unless explicitly known.

**participants**

From `ContextDecision.participants.participants`. Each entry pairs a `family_member_id` with a `Relationship` (`OWNER`, `RESPONSIBLE`, `INTERESTED`, `PARTICIPANT`, `CAREGIVER`).

Interested members identified by the Participant Policy may appear in `reason_codes` or a future `interested_member_ids` field; PR4B should preserve them in metadata if not promoted to first-class fields.

**visibility**

From `ContextDecision.visibility`. Uses the single domain `Visibility` enum (`OWNER_ONLY`, `PRIVATE`, `FAMILY`, `CAREGIVERS`, `EXTERNAL`).

**follow_up_action**

> **PR4B schema addition.** PR2 uses `follow_up_required: bool`; PR4B replaces this with the domain `FollowUpAction` enum.

From `ContextDecision.follow_up.action`. Values: `NONE`, `REMIND_OWNER`, `WAIT_RESPONSE`, `WATCH`, `ESCALATE`.

Planning and Reminder layers interpret this; Context does not schedule anything.

**confidence**

Aggregated score reflecting identity, understanding, and policy confidence. See Section 9.

**reason_codes**

> **PR4B schema addition.**

Stable string codes documenting why Context resolved the way it did. Examples

- `SCOPE_EXPLICIT_HINT`
- `SCOPE_FAMILY_DEFAULT`
- `OWNERSHIP_EXPLICIT`
- `OWNERSHIP_FAMILY_UNASSIGNED`
- `RESPONSIBLE_NOT_INFERRED`
- `VISIBILITY_SENSITIVE_PRIVATE`
- `FOLLOW_UP_ESCALATION_LANGUAGE`

Reason codes support testing, logging, and future explainability. They are not shown to families by default.

**related_entities**

Entity names extracted from understanding or passed via request metadata. Aligns with the Entity concept in the intelligence model. Maps from `UnderstandingContext.entities`.

**metadata**

Opaque output bag for traceability. Expected keys in PR4B

- `conversation_id`
- `source`
- `received_at`
- `understanding_confidence`
- `identity_confidence`
- `policy_confidences` (per-dimension breakdown)

## Why ContextResult contains no Tasks or Execution information

Context describes **organizational meaning**, not **operational intent**.

Tasks, events, reminders, and execution actions are planning and execution concerns. Including them in `ContextResult` would

- Blur the boundary between Context and Planning
- Force Context to anticipate implementation choices
- Make Context harder to test in isolation
- Couple organizational rules to the Execution Engine action registry

Planning Agent v2 consumes `ContextResult` and decides what to create. Execution Engine performs what Planning decided.

---

# 6. Context Immutability

A `ContextResult` represents Naam's organizational understanding at a specific point in time.

Once the Context Agent produces a `ContextResult`, it should be treated as **immutable**. Downstream agents and services consume the object but never modify it in place.

## Principles

- `ContextResult` captures what Naam understood about a conversation **at the moment Context ran**
- Consumers — Planning, Memory, Assignment, Reminder, and future agents — read `ContextResult` but never mutate it
- If new information becomes available (a follow-up message, corrected identity, enriched memory), Naam constructs a **new** `ContextResult` rather than updating an existing one
- The Context Agent itself produces a fresh `ContextResult` on each invocation; it does not maintain or revise prior results

## Why immutability matters

**Deterministic reasoning**

When `ContextResult` is immutable, every downstream decision is based on a fixed organizational snapshot. Agents cannot silently alter scope, ownership, or visibility mid-pipeline, which preserves the deterministic contract established by the Policy Layer.

**Reproducibility**

Given the same `ContextRequest`, the Context Agent produces the same `ContextResult`. If that result is never mutated, the full chain from Context through Planning can be replayed and verified against the original snapshot.

**Debugging**

When something goes wrong, engineers can inspect the exact `ContextResult` that Planning consumed. Immutable snapshots eliminate ambiguity about whether a field changed after Context ran.

**Future auditing**

Families and operators may need to understand why Naam acted a certain way. Immutable context records provide a trustworthy audit trail — each result is a permanent statement of organizational understanding at a point in time.

**Event sourcing compatibility**

Naam may eventually persist context snapshots as events in a conversation history. Immutable `ContextResult` objects map naturally to append-only event logs: new information appends a new event rather than overwriting prior state.

## Implementation guidance (PR4B)

- Model `ContextResult` as a frozen Pydantic model or treat instances as read-only after creation
- Downstream agents receive `ContextResult` by value or reference but must not assign to its fields
- Services that need enriched context re-invoke `ContextAgent.build()` with an updated `ContextRequest`

---

# 7. Lifecycle

## End-to-end flow

```text
Receive ContextRequest
    ↓
Validate
    ↓
Build DecisionInput
    ↓
Invoke ContextDecisionMatrix
    ↓
Merge Identity
    ↓
Merge Understanding
    ↓
Produce ContextResult
```

## Stage descriptions

### 1. Receive ContextRequest

The Service layer calls `ContextAgent.build(request: ContextRequest) -> ContextResult` after Identity and Understanding have completed.

The agent accepts the request object only. It does not fetch missing data.

### 2. Validate

Verify required fields are present and well-typed

- `identity` and `understanding` must exist
- Confidence values must fall within 0.0–1.0
- `family_members` entries must include valid UUIDs when provided

Validation failures that indicate corrupt input may raise structured errors to the Service layer. **Organizational uncertainty is not a validation failure.** Unknown speaker, unassigned owner, and empty participants are valid outcomes.

### 3. Build DecisionInput

Map `ContextRequest` into `DecisionInput`

| DecisionInput field | Source |
|---|---|
| `speaker` | `request.identity` |
| `understanding` | Adapted from `request.understanding` + optional metadata |
| `family_members` | `request.family_members` |

The adapter translates `UnderstandingResult` into `UnderstandingContext`, filling optional policy fields from metadata when the Understanding schema does not yet provide them.

### 4. Invoke ContextDecisionMatrix

Call `ContextDecisionMatrix.evaluate(decision_input)` to obtain `ContextDecision`.

The matrix runs, in order

1. `ScopePolicy`
2. `OwnershipPolicy`
3. `ParticipantPolicy`
4. `VisibilityPolicy`
5. `FollowUpPolicy`

The Context Agent does not invoke policies directly and does not embed business rules.

### 5. Merge Identity

Copy `request.identity` into `ContextResult.speaker` unchanged.

Identity is authoritative for who spoke. Context does not re-resolve identity.

### 6. Merge Understanding

Copy entity-related fields from the adapted understanding into `related_entities`.

Understanding confidence contributes to overall `ContextResult.confidence` and may appear in `metadata`.

### 7. Produce ContextResult

Map each dimension of `ContextDecision` into `ContextResult` fields, compute aggregated confidence, attach `reason_codes`, and populate `metadata` from request traceability fields.

Return `ContextResult` to the Service layer. No side effects.

---

# 8. Interaction with Context Decision Matrix

## Separation of concerns

| Component | Role |
|---|---|
| **Context Decision Matrix** | Owns deterministic business rules via composable policies |
| **Context Agent** | Orchestrates input assembly, matrix invocation, and output mapping |

The Decision Matrix is implemented in `app/context/` (M4 PR3). It is complete and must not be redesigned in PR4B.

Policies are independent

- `ScopePolicy` — scope only
- `OwnershipPolicy` — owner and responsible person only
- `ParticipantPolicy` — participants and interest only
- `VisibilityPolicy` — visibility only
- `FollowUpPolicy` — follow-up action only

The Context Agent

- Injects `ContextDecisionMatrix` via constructor (dependency injection)
- Calls `evaluate()` once per request
- Maps `ContextDecision` → `ContextResult`
- Does not duplicate policy logic
- Does not know policy implementation details beyond the public `DecisionInput` / `ContextDecision` models

If a rule changes, update the relevant policy and its tests. The Context Agent mapping layer should require minimal or no changes.

---

# 9. Confidence

## Principle

The Context Agent should **never fail the pipeline** because ownership, participants, or responsibility cannot be fully determined.

Partial organizational context with lower confidence is always preferable to aborting processing.

## Inputs to confidence

| Source | Field |
|---|---|
| Identity Agent | `identity.confidence` |
| Understanding Agent | `understanding.confidence` |
| Scope policy | `scope.confidence` |
| Ownership policy | `ownership.confidence` |
| Follow-up policy | `follow_up.confidence` |

Visibility and participant policies do not emit confidence today. Their outcomes are treated as deterministic given scope and ownership.

## Aggregation (PR4B default)

Use the **minimum** of contributing confidence scores as the overall `ContextResult.confidence`.

```text
confidence = min(
    identity.confidence,
    understanding.confidence,
    scope.confidence,
    ownership.confidence,
    follow_up.confidence,
)
```

When identity is unknown (`family_member_id is None`), confidence should reflect reduced certainty without blocking output.

When owner or responsible person is unassigned, confidence is lowered through ownership policy scores — not by raising errors.

## Metadata transparency

`metadata.policy_confidences` should record per-dimension scores so Services and future Learning Agent can inspect why confidence dropped.

---

# 10. Future Extension Points

Future intelligence enriches Context **before** the agent runs by expanding `ContextRequest`. The Context Agent API — `build(request) -> ContextResult` — remains stable.

## ContextRequestFactory (Future)

**Today**

Services assemble `ContextRequest` directly. The Service layer loads identity, understanding, family members, and conversation metadata, then passes a complete request to `ContextAgent.build()`.

**Future**

A dedicated `ContextRequestFactory` may build `ContextRequest` by aggregating inputs from multiple sources

- Identity
- Understanding
- Family Members
- Calendar
- Family Memory
- Relationships
- Preferences
- Location
- Time
- Routines

The factory owns data gathering and request composition. The Context Agent remains unaware of where this information originates — it receives a fully formed `ContextRequest` and returns a `ContextResult`.

This preserves the thin-agent design: enrichment grows in the factory layer; orchestration stays in the agent; rules stay in the Decision Matrix.

This is documentation only. PR4B does not implement `ContextRequestFactory`.

## Family Memory

Observational patterns (e.g. "Gowtham usually pays household bills") may arrive as `memory_hints` on the request. PR4B passes hints into metadata or a future policy input extension. Memory does not bypass the Decision Matrix.

## Relationship Graph

Inferred relationships may help Participant Policy in future policy versions. The Context Agent forwards enriched family data; policy changes happen in `app/context/policies/`.

## Calendar

Upcoming events may influence follow-up urgency in future policy versions. Calendar data enters via `ContextRequest`, not repository calls from the agent.

## Location

Place-based context (home, school, office) may enrich entity resolution. Passed as request metadata until policies consume it.

## Routines

Recurring schedule matches may inform scope or follow-up policies. Passed as `routine_context` on the request.

## Preferences

Member or family preferences may affect visibility or follow-up defaults in future policies. Never resolved inside the Context Agent directly.

## Extension rule

Extend `ContextRequest` optional fields and `DecisionInput` optional fields together. Do not add repository calls, AI calls, or planning logic to the Context Agent.

---

# 11. Non-goals

The Context Agent is explicitly **not** responsible for

| Non-goal | Owned by |
|---|---|
| Planning | Planning Agent |
| Execution | Execution Engine |
| Persistence | Services + Repositories |
| Memory updates | Memory Agent / Services |
| Reminder scheduling | Reminder Agent |
| Assignment decisions beyond policy output | Assignment Agent (future) |
| Identity resolution | Identity Agent |
| Language understanding | Understanding Agent |
| Task, event, or note creation | Planning + Execution |
| Inbox lifecycle | InboxService |

---

# 12. Design Principles

## Pipeline discipline

```text
Conversation → Understanding → Context → Planning → Execution
```

## Layer mantra

- **AI understands** — Understanding Agent interprets language
- **Policies organize** — Context Decision Matrix applies deterministic rules
- **Planning decides** — Planning Agent chooses actions
- **Execution executes** — Execution Engine runs handlers

## Agent design

- **Context should remain thin** — orchestration and mapping only
- **Context should orchestrate rather than decide** — no embedded business rules
- **Structured communication** — agents exchange Pydantic models, not natural language
- **Independent testability** — Context Agent tests mock nothing except injected matrix when needed
- **Deterministic context** — same `ContextRequest` always produces the same `ContextResult`
- **Context immutability** — `ContextResult` is read-only after creation; new information produces a new result (see Section 6)
- **Dependency injection** — `ContextDecisionMatrix` injected via constructor

## Alignment with intelligence model

- Ownership and responsibility remain distinct concepts
- Responsibility is never inferred without evidence
- Scope determines mental model, not task type
- Context is produced after Understanding and before Commitment/Task planning

---

# 13. Future PR Mapping

```text
PR4A — Context Agent Design (this document)
    ↓
PR4B — Context Agent Implementation
    ↓
PR5  — Planning Agent v2
```

## PR4A — Design only ✅

- Define input and output contracts
- Define lifecycle and matrix interaction
- Document confidence, immutability, extension points, and non-goals
- No production code

## PR4B — Context Agent implementation

Planned deliverables

- `app/agents/context_agent.py` — `ContextAgent.build()`
- `app/schemas/context_request.py` — `ContextRequest` model (or equivalent in `app/schemas/`)
- Extend `ContextResult` per Section 5 (`responsible_id`, `follow_up_action`, `reason_codes`, `metadata`)
- Adapter: `UnderstandingResult` → `UnderstandingContext`
- Mapper: `ContextDecision` → `ContextResult`
- Unit tests for validation, mapping, confidence, and partial-result scenarios
- No pipeline wiring, no OpenAI, no repositories

## PR5 — Planning Agent v2

- Accept optional `ContextResult` as a read-only input
- Enrich task and event payloads with owner, scope, participants, visibility
- Interpret `follow_up_action` when deciding reminder actions
- Do not re-derive context fields that policies already decided
- Do not mutate `ContextResult` in place

## Post-M4 — Pipeline wiring

Separate from PR4B

- Service calls Identity → Understanding → Context → Planning in order
- Context Agent remains side-effect free

---

# Appendix A — Mapping reference

## ContextDecision → ContextResult

| ContextDecision | ContextResult field |
|---|---|
| `scope.scope` | `scope` |
| `ownership.owner_id` | `owner_id` |
| `ownership.responsible_person_id` | `responsible_id` |
| `participants.participants` | `participants` |
| `visibility.visibility` | `visibility` |
| `follow_up.action` | `follow_up_action` |
| Aggregated policy confidences | `confidence` |
| Policy trace | `reason_codes` |
| Understanding entities | `related_entities` |
| Request trace fields | `metadata` |

## PR2 → PR4B schema evolution

| PR2 field | PR4B disposition |
|---|---|
| `entities` | Renamed to `related_entities` for intelligence model alignment |
| `follow_up_required: bool` | Replaced by `follow_up_action: FollowUpAction` |
| — | Added `responsible_id` |
| — | Added `reason_codes` |
| — | Added `metadata` |

PR4B implementation should update tests and downstream consumers. Planning Agent v2 (PR5) consumes the extended schema.

---

# Appendix B — Related documents

| Document | Relevance |
|---|---|
| `docs/13_naam_philosophy.md` | Coordination over conversation; trusted memory |
| `docs/14_naam_intelligence_model.md` | Context, Policy Layer, Ownership, Scope |
| `docs/16_current_focus.md` | Current milestone and PR status |
| `docs/04_agent_architecture.md` | Agent flow and Context Agent overview |
| `docs/engineering/cursor_guidelines.md` | Layer rules and agent constraints |
| `app/context/` | Context Decision Matrix (PR3, complete) |
| `app/schemas/context.py` | Domain enums and baseline ContextResult (PR2) |

---

# Appendix C — Assumptions

1. **Service assembly** — `InboxService` (or equivalent) loads `family_members` and conversation metadata before calling the Context Agent. The agent does not query the database. A future `ContextRequestFactory` may assume this role without changing the agent API.

2. **Understanding schema gap** — `UnderstandingResult` today lacks `entities` and explicit ownership hints. PR4B adapter reads optional fields from `ContextRequest.metadata` until Understanding Agent schema is extended.

3. **Interested members** — `ParticipantDecision.interested_member_ids` is not promoted to a top-level `ContextResult` field in PR4B unless PR5 requires it. Values may appear in `metadata` initially.

4. **Error vs partial result** — Malformed requests (missing required fields, invalid types) may raise validation errors. Organizational ambiguity always returns `ContextResult` with reduced confidence.

5. **No matrix redesign** — PR4B consumes the existing Decision Matrix as-is. Policy changes are separate PRs.

6. **Agent method name** — `ContextAgent.build()` aligns with `docs/16_current_focus.md` target pipeline notation.

7. **Memory Agent placement** — Per `docs/04_agent_architecture.md`, Memory Agent runs in the broader agent flow but is not invoked by Context Agent in M4. Context may receive memory hints via request enrichment in future milestones.
