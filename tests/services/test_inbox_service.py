"""Unit tests for InboxService."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.inbox import InboxStatus
from app.services.inbox_service import InboxService
from tests.conftest import FAMILY_ID, INBOX_ID


@pytest.fixture
def inbox_item() -> dict:
    return {
        "id": str(INBOX_ID),
        "family_id": str(FAMILY_ID),
        "source_type": "text",
        "raw_content": "Pay the electricity bill tomorrow",
        "status": InboxStatus.RECEIVED.value,
    }


@pytest.fixture
def inbox_service() -> InboxService:
    return InboxService()


@pytest.mark.asyncio
@patch("app.services.inbox_service.inbox_repository.create")
async def test_persist_inbox_sets_received_status(
    mock_create: MagicMock,
    inbox_service: InboxService,
    inbox_item: dict,
) -> None:
    mock_create.return_value = inbox_item

    result = await inbox_service.persist_inbox(
        {
            "family_id": str(FAMILY_ID),
            "raw_content": "Pay the electricity bill tomorrow",
            "source_type": "text",
        }
    )

    mock_create.assert_called_once_with(
        {
            "family_id": str(FAMILY_ID),
            "raw_content": "Pay the electricity bill tomorrow",
            "source_type": "text",
            "status": InboxStatus.RECEIVED.value,
        }
    )
    assert result == inbox_item


@pytest.mark.asyncio
@patch("app.services.inbox_service.inbox_repository.get_by_id")
@patch("app.services.inbox_service.inbox_repository.update_status")
@patch("app.services.inbox_service.inbox_repository.create")
async def test_ingest_inbox_runs_processing_lifecycle(
    mock_create: MagicMock,
    mock_update_status: MagicMock,
    mock_get_by_id: MagicMock,
    inbox_service: InboxService,
    inbox_item: dict,
) -> None:
    processed_item = {**inbox_item, "status": InboxStatus.PROCESSED.value}
    mock_create.return_value = inbox_item
    mock_get_by_id.return_value = processed_item
    process_mock = AsyncMock(
        return_value={
            "understanding": {"type": "TASK", "title": "Pay bill"},
            "execution_plan": {"actions": []},
            "execution_results": [],
        }
    )
    service = InboxService(process_inbox_item_fn=process_mock)

    response = await service.ingest_inbox(
        {
            "family_id": str(FAMILY_ID),
            "raw_content": "Pay the electricity bill tomorrow",
            "source_type": "text",
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
    assert response.inbox_item["status"] == InboxStatus.PROCESSED.value
    assert response.understanding["type"] == "TASK"
    assert response.processing_error is None


@pytest.mark.asyncio
@patch("app.services.inbox_service.inbox_repository.update_status")
@patch("app.services.inbox_service.inbox_repository.create")
async def test_ingest_inbox_marks_failed_without_raising(
    mock_create: MagicMock,
    mock_update_status: MagicMock,
    inbox_service: InboxService,
    inbox_item: dict,
) -> None:
    failed_item = {**inbox_item, "status": InboxStatus.FAILED.value}
    mock_create.return_value = inbox_item
    mock_update_status.return_value = failed_item
    process_mock = AsyncMock(side_effect=RuntimeError("OpenAI unavailable"))
    service = InboxService(process_inbox_item_fn=process_mock)

    response = await service.ingest_inbox(
        {
            "family_id": str(FAMILY_ID),
            "raw_content": "Pay the electricity bill tomorrow",
            "source_type": "text",
        }
    )

    mock_update_status.assert_any_call(str(INBOX_ID), InboxStatus.PROCESSING)
    mock_update_status.assert_any_call(str(INBOX_ID), InboxStatus.FAILED)
    assert response.inbox_item["status"] == InboxStatus.FAILED.value
    assert response.processing_error == "OpenAI unavailable"
    assert response.understanding == {}
    assert response.execution_results == []
