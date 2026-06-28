# Naam - Domain Model

## Version

v1.0

---

# Philosophy

Naam is built around domain objects rather than database tables.

Every piece of information entering the system eventually becomes one or more domain objects.

These objects represent the language spoken by every agent, service and API.

---

# Core Domain Objects

## Family

Represents a household using Naam.

Responsibilities

- Owns all information
- Defines timezone
- Defines preferences
- Defines members

Relationships

Family

├── Members

├── Inbox Items

├── Tasks

├── Events

├── Documents

├── Routines

└── Knowledge

---

## Family Member

Represents an individual within a family.

Attributes

- Name
- Phone Number
- Role
- Preferences
- Availability

Future Attributes

- Working Hours
- Notification Preferences
- Skills
- Interests

---

## Inbox Item

Represents every incoming piece of information.

Possible Sources

- WhatsApp
- Image
- PDF
- Voice Note
- Email
- Manual Entry

Lifecycle

Received

↓

Stored

↓

Understood

↓

Processed

↓

Archived

---

## Task

Represents an actionable activity.

Attributes

- Title
- Description
- Due Date
- Priority
- Assigned Member
- Status

Lifecycle

NEW

↓

ASSIGNED

↓

IN_PROGRESS

↓

COMPLETED

↓

ARCHIVED

---

## Event

Represents something occurring at a specific point in time.

Examples

- Parent Teacher Meeting
- Doctor Appointment
- Birthday Party

---

## Routine

Represents recurring work.

Examples

- Pay Maid Salary
- Grocery Shopping
- Dance Class
- Water Plants

Frequency

- Daily
- Weekly
- Monthly
- Custom

---

## Document

Represents an important family document.

Examples

- Passport
- Aadhaar
- Prescription
- School Circular
- Insurance Policy

---

## Knowledge

Represents structured understanding collected over time.

Examples

- Daughter attends dance school
- Electricity bill paid every month
- Preferred pediatrician
- Grocery store preference

Knowledge is never entered directly.

It is learned by the system.

---

# Relationships

Inbox Item

↓

Understanding

↓

Knowledge

↓

Planning

↓

Tasks

Events

Documents

Routines

---

# Design Principle

Every feature added to Naam should extend an existing domain object before introducing a new one.