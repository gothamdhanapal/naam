"""Unit tests for the CREATE_TASK execution action."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.execution.actions.create_task import CreateTaskAction
from app.execution.models import ActionType, ExecutionAction
from app.services.task_service import TaskService
from tests.conftest import FAMILY_ID, sample_task


@pytest.fixture
def mock_task_service(sample_task) -> MagicMock:
    service = MagicMock(spec=TaskService)
    service.create_task.return_value = sample_task
    return service


@pytest.mark.asyncio
async def test_successfully_creates_task_using_mocked_task_service(
    mock_task_service: MagicMock,
    sample_task,
) -> None:
    action_handler = CreateTaskAction(task_service=mock_task_service)
    action = ExecutionAction(
        type=ActionType.CREATE_TASK,
        payload={
            "family_id": str(FAMILY_ID),
            "title": "Pay electricity bill",
        },
    )

    result = await action_handler.execute(action)

    assert result.success is True
    assert result.action_type == ActionType.CREATE_TASK
    assert result.resource_type == "task"
    assert result.resource_id == sample_task.id
    assert result.message == "Task created successfully"
    mock_task_service.create_task.assert_called_once()


@pytest.mark.asyncio
async def test_returns_failed_action_result_for_invalid_payload(
    mock_task_service: MagicMock,
) -> None:
    action_handler = CreateTaskAction(task_service=mock_task_service)
    action = ExecutionAction(
        type=ActionType.CREATE_TASK,
        payload={"title": "Missing family id"},
    )

    result = await action_handler.execute(action)

    assert result.success is False
    assert result.error == "Invalid CREATE_TASK payload."
    assert "validation_errors" in result.metadata
    mock_task_service.create_task.assert_not_called()


@pytest.mark.asyncio
async def test_returns_failed_action_result_when_task_service_missing() -> None:
    action_handler = CreateTaskAction()
    action = ExecutionAction(
        type=ActionType.CREATE_TASK,
        payload={
            "family_id": str(FAMILY_ID),
            "title": "Pay electricity bill",
        },
    )

    result = await action_handler.execute(action)

    assert result.success is False
    assert result.error == "Missing or invalid 'task_service' dependency."
