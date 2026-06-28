"""
Domain models for Task.

These models represent the Task domain object used across services,
agents, and the execution engine. They are independent of API or
database transport concerns.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Lifecycle status of a task."""

    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class TaskPriority(str, Enum):
    """Relative urgency of a task."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Task(BaseModel):
    """
    A task represents actionable work within a family.

    Maps to the ``tasks`` table in Supabase.
    """

    id: UUID
    family_id: UUID
    title: str
    description: str | None = None
    due_date: date | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.NEW
    assigned_member_id: UUID | None = None
    inbox_item_id: UUID | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> Task:
        """
        Build a Task from a Supabase row dictionary.

        Args:
            row: Raw row returned by Supabase.

        Returns:
            A validated Task domain model.
        """
        return cls.model_validate(row)
