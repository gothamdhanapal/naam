# Naam - Agent Architecture

## Version

v1.0

---

# Philosophy

Naam is not powered by a single AI.

Naam is powered by a collection of specialized AI agents.

Each agent has one responsibility.

Agents communicate with each other through structured outputs rather than natural language.

This makes the system reliable, testable and scalable.

---

# Agent Flow

Incoming Information

↓

Intake Agent

↓

Understanding Agent

↓

Memory Agent

↓

Planning Agent

↓

Assignment Agent

↓

Reminder Agent

↓

Digest Agent

↓

Learning Agent

---

# 1. Intake Agent

Purpose

Receive incoming information.

Inputs

- Text
- Images
- PDFs
- Voice Notes
- WhatsApp Messages

Outputs

Inbox Item

Responsibilities

- Store incoming content
- Detect input type
- Create Inbox record
- Trigger Understanding Agent

---

# 2. Understanding Agent

Purpose

Understand incoming information.

Inputs

Inbox Item

Outputs

Structured JSON

Example

{  
"type":"TASK",  
"title":"Pay Electricity Bill",  
"due_date":"Tomorrow",  
"confidence":0.97  
}

Responsibilities

- Classification
- Entity Extraction
- Date Extraction
- Confidence Scoring

---

# 3. Memory Agent

Purpose

Persist understanding.

Responsibilities

- Store AI Output
- Update Inbox Status
- Connect Related Information
- Build Family Memory

---

# 4. Planning Agent

Purpose

Convert understanding into actions.

Possible Outputs

- Task
- Event
- Reminder
- Routine
- Document

Example

School Circular

↓

PTM Event

↓

Buy School Uniform Task

↓

Reminder

---

# 5. Assignment Agent

Purpose

Determine ownership.

Uses

- Family Members
- Historical Behaviour
- Context
- Preferences

Output

Assigned Family Member

---

# 6. Reminder Agent

Purpose

Track work.

Responsibilities

- Due Today
- Upcoming
- Overdue
- Snoozed
- Completed

---

# 7. Daily Digest Agent

Purpose

Generate daily planning.

Output

Morning Summary

Example

Good Morning

Today's Tasks

Today's Events

Upcoming Reminders

---

# 8. Learning Agent

Purpose

Improve over time.

Learns

Who usually performs tasks

Recurring activities

Family preferences

Frequently contacted businesses

School schedules

Medical history

Preferred reminder timings

The Learning Agent never modifies data directly.

It only produces recommendations for other agents.

---

# Communication Principle

Agents communicate only through structured objects.

Never through natural language.

---

# Design Principle

Each agent should be independently testable.

Replacing one agent should never require changes to the rest of the system.