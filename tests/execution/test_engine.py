"""Unit tests for the Execution Engine."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.execution.actions.create_task import CreateTaskAction
from app.execution.engine import ExecutionEngine
from app.execution.models import ActionResult, ActionType, ExecutionAction, ExecutionPlan
from app.execution.registry import ActionRegistry
from app.services.task_service import TaskService
from tests.conftest import FAMILY_ID


@pytest.fixture
def registry() -> ActionRegistry:
    action_registry = ActionRegistry()
    action_registry.register(ActionType.CREATE_TASK, CreateTaskAction)
    return action_registry


@pytest.fixture
def mock_task_service(sample_task) -> MagicMock:
    service = MagicMock(spec=TaskService)
    service.create_task.return_value = sample_task
    return service


@pytest.fixture
def engine(registry: ActionRegistry, mock_task_service: MagicMock) -> ExecutionEngine:
    return ExecutionEngine(
        registry=registry,
        task_service=mock_task_service,
    )


@pytest.mark.asyncio
async def test_executes_create_task_successfully(
    engine: ExecutionEngine,
    mock_task_service: MagicMock,
    sample_task,
) -> None:
    plan = ExecutionPlan(
        actions=[
            ExecutionAction(
                type=ActionType.CREATE_TASK,
                payload={
                    "family_id": str(FAMILY_ID),
                    "title": "Pay electricity bill",
                },
            )
        ]
    )

    results = await engine.execute(plan)

    assert len(results) == 1
    assert results[0].success is True
    assert results[0].action_type == ActionType.CREATE_TASK
    assert results[0].resource_type == "task"
    assert results[0].resource_id == sample_task.id
    assert results[0].message == "Task created successfully"
    mock_task_service.create_task.assert_called_once()


@pytest.mark.asyncio
async def test_returns_action_result_on_success(engine: ExecutionEngine) -> None:
    plan = ExecutionPlan(
        actions=[
            ExecutionAction(
                type=ActionType.CREATE_TASK,
                payload={
                    "family_id": str(FAMILY_ID),
                    "title": "Buy groceries",
                },
            )
        ]
    )

    results = await engine.execute(plan)

    assert isinstance(results[0], ActionResult)
    assert results[0].success is True


@pytest.mark.asyncio
async def test_continues_after_one_action_fails(
    engine: ExecutionEngine,
    mock_task_service: MagicMock,
) -> None:
    plan = ExecutionPlan(
        actions=[
            ExecutionAction(
                type=ActionType.CREATE_TASK,
                payload={"title": "Missing family id"},
            ),
            ExecutionAction(
                type=ActionType.CREATE_TASK,
                payload={
                    "family_id": str(FAMILY_ID),
                    "title": "Valid task",
                },
            ),
        ]
    )

    results = await engine.execute(plan)

    assert len(results) == 2
    assert results[0].success is False
    assert results[0].error == "Invalid CREATE_TASK payload."
    assert results[1].success is True
    mock_task_service.create_task.assert_called_once()


@pytest.mark.asyncio
async def test_returns_failed_action_result_when_no_handler_registered() -> None:
    engine = ExecutionEngine(registry=ActionRegistry())

    plan = ExecutionPlan(
        actions=[
            ExecutionAction(
                type=ActionType.CREATE_EVENT,
                payload={"title": "School meeting"},
            )
        ]
    )

    results = await engine.execute(plan)

    assert len(results) == 1
    assert results[0].success is False
    assert results[0].action_type == ActionType.CREATE_EVENT
    assert "No handler registered" in (results[0].error or "")
