# Naam Intelligence Model

> "Naam doesn't manage tasks.

> Naam understands people, relationships, responsibilities, and commitments."

Version: v1.0

Status: Living Design Document

---

# Purpose

This document defines how Naam understands the world.

It is **not** a database schema.

It is **not** an API specification.

It is the mental model that every AI agent inside Naam should use when interpreting conversations and deciding actions.

Whenever a design decision is unclear, this document takes precedence.

---

# First Principles

Naam is not a task manager.

Naam is not a calendar.

Naam is not a reminder app.

Naam is an AI Chief of Staff for a family.

Its job is to reduce the family's mental load by understanding conversations and quietly taking care of commitments.

---

# The Core Philosophy

Every conversation should answer five questions.

Who is speaking?

↓

What are they saying?

↓

Who or what is it about?

↓

Who owns the responsibility?

↓

What should Naam do?

Everything in Naam exists to answer these questions better.

---

# The Six Core Concepts

Naam understands only six fundamental concepts.

Everything else is built from them.

---

## 1. Person

A Person is an individual family member.

Examples

- Gowtham

- Wife

- Daughter

- Grandfather

A Person has

- Identity

- Responsibilities

- Preferences

- Routine

- Relationships

- Personal Memory

A Person is **not** a user account.

A Person is someone Naam understands.

---

## 2. Entity

Entities are things the family cares about.

Examples

Person

Child

Pet

Home

Vehicle

School

Office

Health

Finances

Project

Vacation

Every conversation relates to one or more Entities.

Examples

"Pay electricity bill"

Entity

→ Home

"Dance class"

Entity

→ Daughter

"Vet appointment"

Entity

→ Bruno (Pet)

"Architecture interview"

Entity

→ Gowtham

---

## 3. Conversation

Everything begins with a conversation.

Naam never receives Tasks.

Naam receives Conversations.

Each conversation contains

- Speaker

- Timestamp

- Source

- Message

- Family

The Understanding Agent transforms conversations into structured meaning.

---

## 4. Context

Context explains what a conversation means for the family.

Context is produced after Understanding.

It identifies

- Speaker

- Owner

- Participants

- Scope

- Entity

- Intent

- Urgency

- Confidence

Understanding answers

"What did they say?"

Context answers

"What does this mean?"

---

## 5. Commitment

A Commitment is a promise that should not be forgotten.

Examples

Pay electricity bill

Submit thesis

Book vaccination

Buy groceries

Commitments are more fundamental than Tasks.

Tasks are one possible implementation.

Every Commitment contains

- Owner

- Participants

- Entity

- Status

- Intent

- History

---

## 6. Memory

Memory is what Naam has learned.

Not everything the family has said.

Examples

"Gowtham usually pays household bills."

"Wife usually books doctor appointments."

"Daughter has dance class every Saturday."

"Bruno needs grooming every month."

Memory is observational.

It grows over time.

---

# Personal vs Family Intelligence

Naam maintains three independent mental models.

## Personal Mind

Every family member has their own personal assistant.

Example

Gowtham

- Work

- Career

- Gym

- Bills

- Reading

These are private unless explicitly shared.

---

## Family Mind

Shared responsibilities.

Examples

Groceries

Electricity

House

Finances

Vacation

School

Both parents participate.

---

## Dependent Mind

Family members who cannot communicate directly.

Examples

Daughter

Pet

Elderly Parent

Naam speaks with caregivers on their behalf.

---

# Ownership

Ownership is one of Naam's most important decisions.

Every commitment must answer

Who owns this?

Possible owners

- Person

- Family

Ownership determines

- Reminders

- Notifications

- Escalations

- Completion

---

# Responsibility

Responsibility is different from ownership.

Example

School Fees

Owner

→ Family

Responsible

→ Gowtham

Interested

→ Wife

Responsibilities evolve over time.

Naam should learn them automatically.

---

# Scope

Every conversation belongs to one scope.

PERSONAL

FAMILY

DEPENDENT

EXTERNAL

Scope determines visibility and behaviour.

---

# Natural Conversations

Naam should never require structured commands.

Preferred

"Remind me after lunch."

"I finished it."

"Let's do it tomorrow."

"I'll take care of this."

Avoid

Buttons

Forms

Complex configuration

Whenever possible, conversation should replace UI.

---

# Learning

Naam learns through observation.

Examples

Repeated behaviour

Repeated responsibility

Repeated schedules

Repeated participants

The family should rarely need to configure behaviour manually.

---

# Design Principles

## Conversation over Interface

Talking should always be easier than opening an app.

---

## Understand before Acting

Never execute actions without understanding context.

---

## Individual First

Every family member has unique routines.

Naam should never treat everyone identically.

---

## Family when Necessary

Shared responsibilities belong to the family.

Not every reminder needs every member.

---

## Learn Quietly

Naam should observe first.

Recommend second.

Automate last.

---

# Future Intelligence

This model enables future capabilities including

- Family Memory

- Smart Reminders

- Automatic Delegation

- Routine Learning

- Relationship Understanding

- Proactive Suggestions

- Contextual Planning

without changing the underlying philosophy.

---

# The North Star

Naam should feel less like software and more like a trusted Chief of Staff.

The family should feel like they are speaking with someone who understands their lives, rather than operating another productivity application.

If a future feature does not support this vision, it should be reconsidered.