# Naam - Agent Architecture

## Version

v1.1

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

Identity Agent

↓

Understanding Agent

↓

Context Agent

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
- Trigger Identity Agent

---

# 2. Identity Agent

Purpose

Resolve who is speaking.

Inputs

- phone_number
- family_id

Outputs

IdentityResult

Example

{
"family_member_id":"...",
"name":"Gowtham",
"role":"parent",
"phone_number":"15551234567",
"confidence":1.0
}

Responsibilities

- Look up sender in family_members
- Normalize phone numbers for deterministic matching
- Return unknown identity when no match exists

Design

- Deterministic only
- No OpenAI
- No database writes

---

# 3. Understanding Agent

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

# 4. Context Agent

Purpose

Explain what a conversation means for the family.

Inputs

- IdentityResult
- Understanding output
- Family context

Outputs

ContextResult

Example

{
"speaker": {
"family_member_id": "...",
"name": "Gowtham",
"role": "parent",
"phone_number": "15551234567",
"confidence": 1.0
},
"owner_id": "...",
"scope": "FAMILY",
"participants": [
{
"family_member_id": "...",
"relationship": "OWNER"
}
],
"entities": ["Home", "Electricity"],
"visibility": "FAMILY",
"follow_up_required": false,
"confidence": 0.92
}

Responsibilities

- Determine speaker context from identity
- Identify owner and participants
- Assign scope and visibility
- Extract related entities
- Flag when follow-up is required

Schema

- Scope — PERSONAL, FAMILY, DEPENDENT, EXTERNAL
- Visibility — PRIVATE, FAMILY, CAREGIVERS, EXTERNAL
- Relationship — OWNER, RESPONSIBLE, INTERESTED, PARTICIPANT, CAREGIVER

Design

- Structured output only in this milestone
- Agent implementation follows in a later PR

---

# 5. Memory Agent

Purpose

Persist understanding.

Responsibilities

- Store AI Output
- Update Inbox Status
- Connect Related Information
- Build Family Memory

---

# 6. Planning Agent

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

# 7. Assignment Agent

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

# 8. Reminder Agent

Purpose

Track work.

Responsibilities

- Due Today
- Upcoming
- Overdue
- Snoozed
- Completed

---

# 9. Daily Digest Agent

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

# 10. Learning Agent

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