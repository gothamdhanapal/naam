"""Unit tests for TaskService."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.models.task import TaskStatus
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskService
from tests.conftest import FAMILY_ID, TASK_ID, sample_task


@pytest.fixture
def mock_repository(sample_task) -> MagicMock:
    repository = MagicMock(spec=TaskRepository)
    repository.create.return_value = sample_task
    repository.get_by_id.return_value = sample_task
    repository.list_by_family.return_value = [sample_task]
    repository.update.return_value = sample_task
    repository.soft_delete.return_value = sample_task
    return repository


@pytest.fixture
def task_service(mock_repository: MagicMock) -> TaskService:
    return TaskService(repository=mock_repository)


def test_create_task_delegates_to_repository(
    task_service: TaskService,
    mock_repository: MagicMock,
) -> None:
    payload = TaskCreate(
        family_id=FAMILY_ID,
        title="Pay electricity bill",
    )

    result = task_service.create_task(payload)

    mock_repository.create.assert_called_once_with(payload)
    assert result.title == "Pay electricity bill"


def test_get_task_delegates_to_repository(
    task_service: TaskService,
    mock_repository: MagicMock,
) -> None:
    result = task_service.get_task(TASK_ID)

    mock_repository.get_by_id.assert_called_once_with(TASK_ID)
    assert result is not None


def test_list_tasks_delegates_to_repository(
    task_service: TaskService,
    mock_repository: MagicMock,
) -> None:
    results = task_service.list_tasks(FAMILY_ID)

    mock_repository.list_by_family.assert_called_once_with(FAMILY_ID)
    assert len(results) == 1


def test_update_task_delegates_to_repository(
    task_service: TaskService,
    mock_repository: MagicMock,
) -> None:
    update = TaskUpdate(status=TaskStatus.IN_PROGRESS)

    result = task_service.update_task(TASK_ID, update)

    mock_repository.update.assert_called_once_with(TASK_ID, update)
    assert result is not None


def test_delete_task_delegates_to_repository(
    task_service: TaskService,
    mock_repository: MagicMock,
) -> None:
    result = task_service.delete_task(TASK_ID)

    mock_repository.soft_delete.assert_called_once_with(TASK_ID)
    assert result is not None
