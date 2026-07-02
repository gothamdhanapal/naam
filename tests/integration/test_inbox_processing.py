"""Integration tests for the inbox processing pipeline."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.execution.actions.create_task import CreateTaskAction
from app.execution.engine import ExecutionEngine
from app.execution.models import ActionType
from app.execution.registry import ActionRegistry
from app.models.inbox import InboxStatus
from app.schemas.understanding import UnderstandingResult
from app.services.inbox_service import InboxService, ingest_inbox
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
@patch("app.services.inbox_service.inbox_repository.get_by_id")
@patch("app.services.inbox_service.inbox_repository.update_status")
@patch("app.services.inbox_service.inbox_repository.create")
async def test_ingest_inbox_returns_full_processing_response(
    mock_create,
    mock_update_status,
    mock_get_by_id,
    understanding_result: UnderstandingResult,
    sample_task,
) -> None:
    inbox_item = {
        "id": str(INBOX_ID),
        "family_id": str(FAMILY_ID),
        "source_type": "text",
        "raw_content": "Pay the electricity bill tomorrow",
        "status": InboxStatus.RECEIVED.value,
    }
    processed_item = {**inbox_item, "status": InboxStatus.PROCESSED.value}
    mock_create.return_value = inbox_item
    mock_get_by_id.return_value = processed_item

    process_mock = AsyncMock(
        return_value={
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
    )
    service = InboxService(process_inbox_item_fn=process_mock)

    response = await service.ingest_inbox(
        {
            "family_id": str(FAMILY_ID),
            "raw_content": "Pay the electricity bill tomorrow",
        }
    )

    mock_create.assert_called_once()
    mock_update_status.assert_called_once_with(
        str(INBOX_ID),
        InboxStatus.PROCESSING,
    )
    process_mock.assert_awaited_once_with(
        inbox_id=str(INBOX_ID),
        family_id=str(FAMILY_ID),
        content="Pay the electricity bill tomorrow",
    )
    assert response.inbox_item == processed_item
    assert response.understanding["type"] == "TASK"
    assert len(response.execution_plan["actions"]) == 1
    assert response.execution_results[0]["success"] is True


@pytest.mark.asyncio
@patch("app.services.inbox_service._default_inbox_service.ingest_inbox", new_callable=AsyncMock)
async def test_ingest_inbox_module_helper_delegates_to_service(
    mock_ingest_inbox,
) -> None:
    mock_ingest_inbox.return_value = MagicMock()

    payload = {
        "family_id": str(FAMILY_ID),
        "raw_content": "Pay the electricity bill tomorrow",
    }

    await ingest_inbox(payload)

    mock_ingest_inbox.assert_awaited_once_with(payload)
