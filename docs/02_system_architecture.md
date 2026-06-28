# Naam - System Architecture

## Version

v1.0

---

# High-Level Architecture

```
WhatsApp
      │
      ▼
FastAPI API
      │
      ▼
Services
      │
      ▼
AI Agents
      │
      ▼
Repositories
      │
      ▼
Supabase
      │
      ▼
OpenAI

```

---

# Technology Stack

Backend

- FastAPI

Database

- Supabase PostgreSQL

Object Storage

- Supabase Storage

Authentication

- Supabase Auth

AI

- OpenAI

Messaging

- WhatsApp Cloud API

Scheduling

- APScheduler

Queue

- Redis

Hosting

- Railway

Analytics

- PostHog

Monitoring

- Sentry

---

# Backend Layers

## API Layer

Responsibilities

- HTTP Endpoints
- Validation
- Authentication
- Response Formatting

---

## Service Layer

Responsibilities

- Business Logic
- Workflow Orchestration
- Calling AI Agents
- Calling Repositories

---

## Agent Layer

Responsibilities

- AI Understanding
- Planning
- Memory
- Assignment
- Learning

Agents never communicate directly with the database.

---

## Repository Layer

Responsibilities

- Read data
- Write data
- Update data

Repositories are the only layer that interacts with Supabase.

---

# Data Flow

Incoming Information

↓

Inbox

↓

Understanding Agent

↓

Memory Update

↓

Planning Agent

↓

Task/Event/Routine Creation

↓

Assignment

↓

Reminder Engine

↓

Completion

↓

Learning

---

# Core Objects

- Family
- Family Member
- Inbox Item
- Task
- Event
- Routine
- Document
- Notification

---

# Design Principles

- Small Services
- Single Responsibility
- AI as Independent Workers
- Repository Pattern
- Event Driven Workflows
- Stateless APIs
- Persistent Memory

