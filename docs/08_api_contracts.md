# Naam - API Contracts

## Version

v1.0

---

# Philosophy

APIs are the public interface of Naam.

Endpoints should remain stable even as internal implementations evolve.

Every endpoint must be predictable, versionable and documented.

---

# API Principles

- RESTful design
- JSON only
- Stateless requests
- UUIDs for resource identifiers
- UTC timestamps
- Consistent error responses

---

# Current APIs

## GET /

Purpose

Health check.

Response

{  
"status": "ok",  
"app": "Naam"  
}

---

## POST /inbox

Purpose

Receive new family information.

Request

{  
"family_id": "...",  
"source_type": "text",  
"raw_content": "Pay electricity bill tomorrow"  
}

Workflow

Create Inbox Item

↓

Understanding Agent

↓

Memory Update

↓

Execution Plan

↓

Execution Engine

↓

Task/Event Creation

Response

Inbox Item

---

# Future APIs

GET /tasks

POST /tasks

PATCH /tasks/{id}

GET /events

POST /events

GET /family

GET /digest/today

POST /whatsapp/webhook

POST /documents

GET /knowledge/search

---

# Error Format

{  
"success": false,  
"error": {  
"code": "VALIDATION_ERROR",  
"message": "...",  
"details": {}  
}  
}

---

# API Versioning

Current Version

v1

Future versions should remain backwards compatible whenever possible.