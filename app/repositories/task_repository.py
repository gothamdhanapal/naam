"""
Repository for Task persistence.

This is the only layer permitted to read from or write to the ``tasks``
table in Supabase. It performs CRUD operations and maps database rows
to domain models without embedding business rules.

Expected ``tasks`` table columns:

- id (uuid, primary key)
- family_id (uuid, foreign key)
- title (text)
- description (text, nullable)
- due_date (date, nullable)
- priority (text)
- status (text)
- assigned_member_id (uuid, nullable)
- inbox_item_id (uuid, nullable)
- created_at (timestamptz)
- updated_at (timestamptz)
- deleted_at (timestamptz, nullable)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from supabase import Client

from app.core.supabase import supabase
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskRepository:
    """
    Data access layer for tasks.

    Accepts a Supabase client via constructor injection so callers and
    tests can supply a real or mocked client without touching globals.
    """

    _TABLE = "tasks"

    def __init__(self, client: Client | None = None) -> None:
        """
        Initialize the repository.

        Args:
            client: Supabase client instance. Defaults to the application
                client when not provided.
        """
        self._client = client or supabase

    def create(self, task: TaskCreate) -> Task:
        """
        Insert a new task.

        Args:
            task: Validated creation payload.

        Returns:
            The persisted Task domain model.

        Raises:
            RuntimeError: If Supabase does not return the created row.
        """
        now = datetime.now(timezone.utc).isoformat()
        payload = {
            **task.model_dump(mode="json"),
            "created_at": now,
            "updated_at": now,
        }

        response = (
            self._client.table(self._TABLE)
            .insert(payload)
            .execute()
        )

        if not response.data:
            raise RuntimeError("Failed to create task: empty response from Supabase.")

        return Task.from_row(response.data[0])

    def get_by_id(self, task_id: UUID) -> Task | None:
        """
        Fetch a single active (non-deleted) task by id.

        Args:
            task_id: Primary key of the task.

        Returns:
            The Task if found and not soft-deleted, otherwise None.
        """
        response = (
            self._client.table(self._TABLE)
            .select("*")
            .eq("id", str(task_id))
            .is_("deleted_at", "null")
            .execute()
        )

        if not response.data:
            return None

        return Task.from_row(response.data[0])

    def list_by_family(self, family_id: UUID) -> list[Task]:
        """
        List all active tasks belonging to a family.

        Args:
            family_id: Family that owns the tasks.

        Returns:
            Tasks ordered by creation time, newest first.
        """
        response = (
            self._client.table(self._TABLE)
            .select("*")
            .eq("family_id", str(family_id))
            .is_("deleted_at", "null")
            .order("created_at", desc=True)
            .execute()
        )

        rows: list[dict[str, Any]] = response.data or []
        return [Task.from_row(row) for row in rows]

    def update(self, task_id: UUID, task: TaskUpdate) -> Task | None:
        """
        Apply a partial update to an active task.

        Args:
            task_id: Primary key of the task to update.
            task: Fields to change. Unset fields are ignored.

        Returns:
            The updated Task if found and not soft-deleted, otherwise None.
        """
        updates = task.model_dump(exclude_unset=True, mode="json")
        if not updates:
            return self.get_by_id(task_id)

        updates["updated_at"] = datetime.now(timezone.utc).isoformat()

        response = (
            self._client.table(self._TABLE)
            .update(updates)
            .eq("id", str(task_id))
            .is_("deleted_at", "null")
            .execute()
        )

        if not response.data:
            return None

        return Task.from_row(response.data[0])

    def soft_delete(self, task_id: UUID) -> Task | None:
        """
        Soft-delete a task by setting ``deleted_at``.

        Args:
            task_id: Primary key of the task to delete.

        Returns:
            The soft-deleted Task if found and active, otherwise None.
        """
        now = datetime.now(timezone.utc).isoformat()

        response = (
            self._client.table(self._TABLE)
            .update(
                {
                    "deleted_at": now,
                    "updated_at": now,
                }
            )
            .eq("id", str(task_id))
            .is_("deleted_at", "null")
            .execute()
        )

        if not response.data:
            return None

        return Task.from_row(response.data[0])
