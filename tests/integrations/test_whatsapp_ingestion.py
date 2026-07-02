"""Integration tests for WhatsApp ingestion via InboxService."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.integrations.whatsapp.service import WhatsAppService
from app.models.inbox import InboxStatus
from app.schemas.inbox import InboxProcessResponse
from tests.conftest import FAMILY_ID, INBOX_ID


@pytest.mark.asyncio
async def test_whatsapp_uses_ingest_inbox() -> None:
    client = MagicMock()
    client.mark_as_read = AsyncMock(return_value={})
    inbox_item = {
        "id": str(INBOX_ID),
        "family_id": str(FAMILY_ID),
        "raw_content": "Pay the electricity bill tomorrow",
        "source_type": "whatsapp",
        "status": InboxStatus.PROCESSED.value,
    }
    ingest_mock = AsyncMock(
        return_value=InboxProcessResponse(
            inbox_item=inbox_item,
            understanding={"type": "TASK", "title": "Pay the electricity bill"},
            execution_plan={"actions": []},
            execution_results=[{"success": True}],
        )
    )
    service = WhatsAppService(
        client=client,
        default_family_id=str(FAMILY_ID),
        ingest_inbox=ingest_mock,
    )

    from app.integrations.whatsapp.models import WhatsAppIncomingMessage, WhatsAppTextBody

    message = WhatsAppIncomingMessage(
        **{
            "from": "15551234567",
            "id": "wamid.test",
            "timestamp": "1710000000",
            "type": "text",
            "text": WhatsAppTextBody(body="Pay the electricity bill tomorrow"),
        }
    )

    result = await service.handle_incoming_message(message)

    ingest_mock.assert_awaited_once()
    assert result.inbox_item == inbox_item
    assert result.understanding["type"] == "TASK"
    client.mark_as_read.assert_awaited_once_with("wamid.test")


@pytest.mark.asyncio
async def test_whatsapp_continues_when_processing_fails() -> None:
    client = MagicMock()
    client.mark_as_read = AsyncMock(return_value={})
    failed_item = {
        "id": str(INBOX_ID),
        "family_id": str(FAMILY_ID),
        "raw_content": "Pay the electricity bill tomorrow",
        "source_type": "whatsapp",
        "status": InboxStatus.FAILED.value,
    }
    ingest_mock = AsyncMock(
        return_value=InboxProcessResponse(
            inbox_item=failed_item,
            processing_error="OpenAI unavailable",
        )
    )
    service = WhatsAppService(
        client=client,
        default_family_id=str(FAMILY_ID),
        ingest_inbox=ingest_mock,
    )

    from app.integrations.whatsapp.models import WhatsAppIncomingMessage, WhatsAppTextBody

    message = WhatsAppIncomingMessage(
        **{
            "from": "15551234567",
            "id": "wamid.test",
            "timestamp": "1710000000",
            "type": "text",
            "text": WhatsAppTextBody(body="Pay the electricity bill tomorrow"),
        }
    )

    result = await service.handle_incoming_message(message)

    assert result.inbox_item["status"] == InboxStatus.FAILED.value
    assert result.processing_error == "OpenAI unavailable"
    client.mark_as_read.assert_awaited_once()
