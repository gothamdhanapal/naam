"""
Business logic layer for Tasks.

Coordinates task workflows and owns all task-related rules and side
effects. Persistence is delegated to TaskRepository; this service
never communicates with Supabase directly.

The Execution Engine and API layer should call TaskService rather than
TaskRepository so that future capabilities (reminders, notifications,
audit logging, recurring task generation, knowledge updates) can be
added here without changing upstream callers.
"""

from __future__ import annotations

from uuid import UUID

from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """
    Application service for task operations.

    Accepts a TaskRepository via constructor injection so callers and
    tests can supply a real or mocked repository.
    """

    def __init__(self, repository: TaskRepository | None = None) -> None:
        """
        Initialize the service.

        Args:
            repository: Task persistence layer. Defaults to a new
                TaskRepository when not provided.
        """
        self._repository = repository or TaskRepository()

    def create_task(self, task: TaskCreate) -> Task:
        """
        Create a new task for a family.

        Args:
            task: Validated creation payload.

        Returns:
            The persisted Task domain model.

        Raises:
            RuntimeError: If persistence fails.
        """
        # Future: validate family membership, assignment rules, duplicates.
        created = self._repository.create(task)

        # Future: schedule reminders, send notifications, write audit log,
        # update family knowledge graph.
        return created

    def get_task(self, task_id: UUID) -> Task | None:
        """
        Retrieve a single active task by id.

        Args:
            task_id: Primary key of the task.

        Returns:
            The Task if found and not deleted, otherwise None.
        """
        return self._repository.get_by_id(task_id)

    def list_tasks(self, family_id: UUID) -> list[Task]:
        """
        List all active tasks for a family.

        Args:
            family_id: Family that owns the tasks.

        Returns:
            Active tasks ordered by creation time, newest first.
        """
        # Future: apply visibility filters, sorting preferences, pagination.
        return self._repository.list_by_family(family_id)

    def update_task(self, task_id: UUID, task: TaskUpdate) -> Task | None:
        """
        Update an existing task.

        Args:
            task_id: Primary key of the task to update.
            task: Fields to change. Unset fields are ignored.

        Returns:
            The updated Task if found and not deleted, otherwise None.
        """
        # Future: enforce status transitions, reassignment rules, completion side effects.
        updated = self._repository.update(task_id, task)

        # Future: reschedule reminders, notify assignee, write audit log.
        return updated

    def delete_task(self, task_id: UUID) -> Task | None:
        """
        Soft-delete a task.

        Args:
            task_id: Primary key of the task to delete.

        Returns:
            The soft-deleted Task if found and active, otherwise None.
        """
        deleted = self._repository.soft_delete(task_id)

        # Future: cancel reminders, notify stakeholders, write audit log.
        return deleted
