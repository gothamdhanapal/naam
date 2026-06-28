"""Integration tests for the inbox processing pipeline."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.execution.actions.create_task import CreateTaskAction
from app.execution.engine import ExecutionEngine
from app.execution.models import ActionType
from app.execution.registry import ActionRegistry
from app.schemas.understanding import UnderstandingResult
from app.services.inbox_service import create_inbox
from app.services.processing_service import process_inbox_item
from app.services.task_service import TaskService
from tests.conftest import FAMILY_ID, INBOX_ID, sample_task


@pytest.fixture
def mock_task_service(sample_task) -> MagicMock:
    service = MagicMock(spec=TaskService)
    service.create_task.return_value = sample_task
    return service


@pytest.fixture
def execution_engine(mock_task_service: MagicMock) -> ExecutionEngine:
    registry = ActionRegistry()
    registry.register(ActionType.CREATE_TASK, CreateTaskAction)
    return ExecutionEngine(
        registry=registry,
        task_service=mock_task_service,
    )


@pytest.fixture
def understanding_result() -> UnderstandingResult:
    return UnderstandingResult(
        type="TASK",
        title="Pay the electricity bill",
        due_date="tomorrow",
        confidence=0.95,
    )


@pytest.mark.asyncio
@patch("app.services.processing_service.update_ai_result")
@patch("app.services.processing_service.create_execution_engine")
@patch("app.services.processing_service.understand_message")
async def test_inbox_processing_flow_creates_task(
    mock_understand_message,
    mock_create_execution_engine,
    mock_update_ai_result,
    execution_engine: ExecutionEngine,
    mock_task_service: MagicMock,
    understanding_result: UnderstandingResult,
    sample_task,
) -> None:
    mock_understand_message.return_value = understanding_result
    mock_create_execution_engine.return_value = execution_engine

    result = await process_inbox_item(
        inbox_id=str(INBOX_ID),
        family_id=str(FAMILY_ID),
        content="Pay the electricity bill tomorrow",
    )

    mock_understand_message.assert_called_once_with(
        "Pay the electricity bill tomorrow"
    )
    mock_create_execution_engine.assert_called_once()
    mock_update_ai_result.assert_called_once_with(
        str(INBOX_ID),
        understanding_result.model_dump(),
    )
    mock_task_service.create_task.assert_called_once()

    assert result["understanding"]["type"] == "TASK"
    assert result["understanding"]["title"] == "Pay the electricity bill"
    assert len(result["execution_plan"]["actions"]) == 1
    assert result["execution_plan"]["actions"][0]["type"] == ActionType.CREATE_TASK.value
    assert result["execution_results"][0]["success"] is True
    assert result["execution_results"][0]["resource_type"] == "task"
    assert result["execution_results"][0]["resource_id"] == str(sample_task.id)


@pytest.mark.asyncio
@patch("app.services.inbox_service.process_inbox_item", new_callable=AsyncMock)
@patch("app.services.inbox_service.create_inbox_item")
async def test_inbox_request_returns_full_processing_response(
    mock_create_inbox_item,
    mock_process_inbox_item,
    understanding_result: UnderstandingResult,
    sample_task,
) -> None:
    inbox_item = {
        "id": str(INBOX_ID),
        "family_id": str(FAMILY_ID),
        "source_type": "text",
        "raw_content": "Pay the electricity bill tomorrow",
    }
    mock_create_inbox_item.return_value = inbox_item
    mock_process_inbox_item.return_value = {
        "understanding": understanding_result.model_dump(),
        "execution_plan": {
            "actions": [
                {
                    "type": ActionType.CREATE_TASK.value,
                    "payload": {
                        "family_id": str(FAMILY_ID),
                        "title": "Pay the electricity bill",
                        "inbox_item_id": str(INBOX_ID),
                    },
                }
            ]
        },
        "execution_results": [
            {
                "success": True,
                "action_type": ActionType.CREATE_TASK.value,
                "resource_type": "task",
                "resource_id": str(sample_task.id),
                "message": "Task created successfully",
                "error": None,
                "metadata": {},
            }
        ],
    }

    response = await create_inbox(
        {
            "family_id": str(FAMILY_ID),
            "raw_content": "Pay the electricity bill tomorrow",
        }
    )

    mock_create_inbox_item.assert_called_once()
    mock_process_inbox_item.assert_awaited_once_with(
        inbox_id=str(INBOX_ID),
        family_id=str(FAMILY_ID),
        content="Pay the electricity bill tomorrow",
    )
    assert response.inbox_item == inbox_item
    assert response.understanding["type"] == "TASK"
    assert len(response.execution_plan["actions"]) == 1
    assert response.execution_results[0]["success"] is True
