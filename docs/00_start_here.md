# Naam - Start Here

## Welcome

Welcome to the Naam project.

Naam (நாம்) means **"We"** in Tamil.

Naam is an AI-powered Family Chief of Staff designed to reduce the invisible mental load of running a family.

The system transforms everyday information into organized actions, remembers important context, coordinates responsibilities, and continuously learns how a family operates.

This document is the starting point for anyone contributing to the project.

---

# Project Status

Current Version

v0.3.0

Current Phase

Execution Phase

Current Milestone

Execution Engine & Automatic Task Creation

Project Status

Architecture Complete

Implementation In Progress

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

---

# Current Architecture

FastAPI

↓

Services

↓

AI Agents

↓

Execution Engine

↓

Repositories

↓

Supabase

OpenAI provides reasoning.

The Execution Engine performs deterministic actions.

Repositories are the only layer allowed to access the database.

---

# Current Capabilities

✅ FastAPI Backend

✅ Supabase Integration

✅ Git Repository

✅ Inbox API

✅ OpenAI Integration

✅ Understanding Agent

✅ AI Output Persistence

✅ Project Documentation

---

# Immediate Next Goal

Build the Execution Engine.

The Execution Engine converts AI decisions into deterministic application actions.

Example

Inbox Message

↓

Understanding Agent

↓

Planning Agent

↓

Execution Plan

↓

Execution Engine

↓

Create Task

↓

Assign Owner

↓

Store Results

---

# Engineering Workflow

Every feature follows the same lifecycle.

1. Design
2. Implement
3. Test
4. Review
5. Commit
6. Update Documentation
7. Update Project Status

Repeat.

---

# Repository Structure

backend/

docs/

prompts/

tests/

scripts/

README.md

CHANGELOG.md

DECISIONS.md

TODO.md

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

---

# Before Starting Any New Feature

Understand the user problem.

Review the relevant architecture document.

Design before coding.

Keep responsibilities separated.

Write readable code.

Test independently.

Commit meaningful milestones.

Update PROJECT_STATUS.md.

---

# Long-Term Vision

Naam becomes the trusted operational memory for every family.

Rather than acting as another application, Naam quietly understands, remembers, plans, coordinates and learns so families can spend less time managing life and more time living it.

---

# Current Sprint

Execution Engine

Primary Deliverables

- Planning Agent
- Execution Engine
- Automatic Task Creation
- Event Creation
- Routine Generation

---

# First Prompt for Every New Chat

"I'm continuing development of Naam.

Read `docs/00_start_here.md` and use it as the entry point.

Assume all referenced documentation is available.

We are currently working on the Execution Engine milestone.

Help me design, review and implement the next feature while keeping the architecture consistent."

---

Last Updated

Architecture Foundation Complete  
Execution Phase Started