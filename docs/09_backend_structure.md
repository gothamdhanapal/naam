# Naam - Backend Structure

## Version

v1.0

---

# Philosophy

The backend is organized by responsibility, not by feature.

Each folder has one purpose.

---

# Folder Structure

backend/

app/

api/

agents/

services/

repositories/

schemas/

models/

core/

executors/

prompts/

memory/

utils/

---

# Layer Responsibilities

## API

HTTP endpoints.

No business logic.

---

## Services

Business workflows.

Coordinates repositories and agents.

---

## Agents

AI reasoning.

Produces structured outputs.

Never updates the database directly.

---

## Repositories

Database access.

Only layer communicating with Supabase.

---

## Executors

Execute AI-generated action plans.

Responsible for deterministic execution.

---

## Prompts

Prompt templates.

Version controlled.

Never embedded directly inside Python files.

---

## Memory

Knowledge graph.

Family memory.

Context retrieval.

---

## Utils

Small reusable helpers.

Should never contain business logic.

---

# Dependency Rules

API

↓

Services

↓

Agents

↓

Repositories

↓

Database

No layer may skip another layer.

---

# Testing Strategy

Every layer should be independently testable.

Unit Tests

Repository Tests

Integration Tests

AI Evaluation Tests