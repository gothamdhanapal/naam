"""Unit tests for TaskRepository."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.models.task import TaskStatus
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate
from tests.conftest import (
    FAMILY_ID,
    TASK_ID,
    build_supabase_client,
    build_supabase_response,
    sample_task_row,
)


def test_create_inserts_task_and_returns_domain_model(sample_task_row) -> None:
    response = build_supabase_response([sample_task_row])
    client = build_supabase_client(response)
    repository = TaskRepository(client=client)

    task = repository.create(
        TaskCreate(
            family_id=FAMILY_ID,
            title="Pay electricity bill",
        )
    )

    assert task.id == TASK_ID
    assert task.title == "Pay electricity bill"
    client.table.assert_called_with("tasks")
    client.table.return_value.insert.assert_called_once()


def test_create_raises_when_supabase_returns_empty_data() -> None:
    response = build_supabase_response([])
    client = build_supabase_client(response)
    repository = TaskRepository(client=client)

    with pytest.raises(RuntimeError, match="Failed to create task"):
        repository.create(
            TaskCreate(
                family_id=FAMILY_ID,
                title="Pay electricity bill",
            )
        )


def test_get_by_id_returns_task_when_found(sample_task_row) -> None:
    response = build_supabase_response([sample_task_row])
    client = build_supabase_client(response)
    repository = TaskRepository(client=client)

    task = repository.get_by_id(TASK_ID)

    assert task is not None
    assert task.id == TASK_ID
    client.table.return_value.select.assert_called_once_with("*")
    client.table.return_value.eq.assert_called_with("id", str(TASK_ID))
    client.table.return_value.is_.assert_called_with("deleted_at", "null")


def test_get_by_id_returns_none_when_not_found() -> None:
    response = build_supabase_response([])
    client = build_supabase_client(response)
    repository = TaskRepository(client=client)

    task = repository.get_by_id(TASK_ID)

    assert task is None


def test_list_by_family_returns_active_tasks(sample_task_row) -> None:
    second_row = {
        **sample_task_row,
        "id": "880e8400-e29b-41d4-a716-446655440003",
        "title": "Buy groceries",
    }
    response = build_supabase_response([sample_task_row, second_row])
    client = build_supabase_client(response)
    repository = TaskRepository(client=client)

    tasks = repository.list_by_family(FAMILY_ID)

    assert len(tasks) == 2
    client.table.return_value.eq.assert_called_with("family_id", str(FAMILY_ID))
    client.table.return_value.order.assert_called_with("created_at", desc=True)


def test_update_applies_partial_changes(sample_task_row) -> None:
    updated_row = {
        **sample_task_row,
        "status": TaskStatus.IN_PROGRESS.value,
    }
    response = build_supabase_response([updated_row])
    client = build_supabase_client(response)
    repository = TaskRepository(client=client)

    task = repository.update(
        TASK_ID,
        TaskUpdate(status=TaskStatus.IN_PROGRESS),
    )

    assert task is not None
    assert task.status == TaskStatus.IN_PROGRESS
    client.table.return_value.update.assert_called_once()


def test_update_returns_none_when_task_not_found() -> None:
    response = build_supabase_response([])
    client = build_supabase_client(response)
    repository = TaskRepository(client=client)

    task = repository.update(
        TASK_ID,
        TaskUpdate(status=TaskStatus.COMPLETED),
    )

    assert task is None


def test_soft_delete_sets_deleted_at(sample_task_row) -> None:
    deleted_at = datetime(2026, 6, 28, 15, 0, 0, tzinfo=timezone.utc).isoformat()
    deleted_row = {
        **sample_task_row,
        "deleted_at": deleted_at,
    }
    response = build_supabase_response([deleted_row])
    client = build_supabase_client(response)
    repository = TaskRepository(client=client)

    task = repository.soft_delete(TASK_ID)

    assert task is not None
    assert task.deleted_at is not None
    update_payload = client.table.return_value.update.call_args[0][0]
    assert "deleted_at" in update_payload
    assert "updated_at" in update_payload


def test_soft_delete_returns_none_when_task_not_found() -> None:
    response = build_supabase_response([])
    client = build_supabase_client(response)
    repository = TaskRepository(client=client)

    task = repository.soft_delete(TASK_ID)

    assert task is None
