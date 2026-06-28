"""
Input schemas for Task persistence.

These schemas define the data shape accepted by the repository layer.
They are not API request/response models.
"""

from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    """Fields required or optionally supplied when creating a task."""

    family_id: UUID
    title: str = Field(min_length=1)
    description: str | None = None
    due_date: date | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.NEW
    assigned_member_id: UUID | None = None
    inbox_item_id: UUID | None = None


class TaskUpdate(BaseModel):
    """Partial update payload for an existing task."""

    title: str | None = Field(default=None, min_length=1)
    description: str | None = None
    due_date: date | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
    assigned_member_id: UUID | None = None
    inbox_item_id: UUID | None = None
