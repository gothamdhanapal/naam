# Naam - Database Design

## Version

v1.0

---

# Database Philosophy

The database is the long-term memory of Naam.

AI generates knowledge.

The database preserves knowledge.

---

# Primary Tables

## families

Purpose

Represents a household.

Relationships

One Family

↓

Many Members

Many Inbox Items

Many Tasks

Many Events

Many Documents

Many Routines

---

## family_members

Purpose

Represents individuals within a family.

Future Columns

- avatar_url
- notification_preferences
- availability
- timezone

---

## inbox_items

Purpose

Stores all incoming information.

Key Fields

- content
- input_type
- ai_output
- status
- processed_at

---

## tasks

Purpose

Stores actionable work.

Relationships

Created From

↓

Inbox Item

Assigned To

↓

Family Member

---

## events

Purpose

Stores scheduled activities.

Future Integrations

Google Calendar

Apple Calendar

Outlook Calendar

---

## routines

Purpose

Stores recurring work.

Future Engine

Routine Scheduler

↓

Task Generator

↓

Reminder Engine

---

## documents

Purpose

Stores metadata for uploaded files.

Files remain in Supabase Storage.

Database stores references.

---

## knowledge

Purpose

Represents long-term family memory.

Examples

Schools

Doctors

Pets

Preferences

Businesses

Addresses

Subscriptions

Knowledge should grow continuously over the lifetime of the family.

---

# Database Principles

Single Source of Truth

Every object has one owner.

Soft Deletes preferred over Hard Deletes.

All timestamps stored in UTC.

UUIDs used as primary keys.

Relationships enforced using foreign keys.

Indexes added only after measuring query performance.

---

# Migration Strategy

Every schema modification must be introduced through version-controlled SQL migration files.

Database changes must never be performed manually in production.