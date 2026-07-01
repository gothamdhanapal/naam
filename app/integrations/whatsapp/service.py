"""
WhatsApp business logic.

Receives incoming WhatsApp messages and ingests them into the inbox
without triggering AI processing.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

import httpx

from app.integrations.whatsapp.client import WhatsAppClient
from app.integrations.whatsapp.models import (
    WhatsAppIngestionResult,
    WhatsAppIncomingMessage,
    WhatsAppWebhookPayload,
)
from app.schemas.inbox import InboxCreate
from app.services.inbox_service import store_inbox as default_store_inbox


StoreInboxFn = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]

logger = logging.getLogger(__name__)


class WhatsAppService:
    """
    Orchestrates WhatsApp message ingestion.

    Converts incoming WhatsApp messages into inbox items via InboxService.
    No AI processing occurs in this layer.
    """

    def __init__(
        self,
        client: WhatsAppClient,
        default_family_id: str,
        store_inbox: StoreInboxFn | None = None,
    ) -> None:
        """
        Initialize the WhatsApp service.

        Args:
            client: WhatsApp Cloud API client.
            default_family_id: Family that receives ingested messages.
            store_inbox: Inbox persistence callable. Defaults to
                ``inbox_service.store_inbox`` when not provided.
        """
        self._client = client
        self._default_family_id = default_family_id
        self._store_inbox = store_inbox or default_store_inbox

    async def _safe_outbound_call(
        self,
        operation: str,
        call: Awaitable[Any],
        **context: Any,
    ) -> None:
        """
        Execute an outbound Graph API call without failing inbound processing.

        Outbound WhatsApp calls (mark_as_read, send_text, etc.) must not cause
        webhook failures once the inbox item has been stored.
        """
        try:
            await call
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            logger.error(
                "WhatsApp Graph API %s failed: status=%s body=%s context=%s",
                operation,
                status,
                exc.response.text,
                context,
            )
        except httpx.HTTPError:
            logger.exception(
                "WhatsApp Graph API %s request error: context=%s",
                operation,
                context,
            )

    async def handle_webhook_payload(
        self,
        payload: WhatsAppWebhookPayload,
    ) -> list[WhatsAppIngestionResult]:
        """
        Process a validated webhook payload.

        Args:
            payload: Parsed WhatsApp webhook payload.

        Returns:
            Ingestion results for each text message processed.
        """
        results: list[WhatsAppIngestionResult] = []

        for message in payload.extract_text_messages():
            result = await self.handle_incoming_message(message)
            results.append(result)

        return results

    async def handle_incoming_message(
        self,
        message: WhatsAppIncomingMessage,
    ) -> WhatsAppIngestionResult:
        """
        Ingest a single incoming WhatsApp text message.

        Args:
            message: Parsed incoming WhatsApp message.

        Returns:
            Ingestion result containing the stored inbox item.
        """
        text = message.extract_text()
        if text is None:
            raise ValueError("Only text WhatsApp messages are supported.")

        inbox_create = InboxCreate(
            family_id=self._default_family_id,
            raw_content=text,
            source_type="whatsapp",
        )

        inbox_item = await self._store_inbox(inbox_create.model_dump())

        await self._safe_outbound_call(
            "mark_as_read",
            self._client.mark_as_read(message.id),
            message_id=message.id,
        )

        return WhatsAppIngestionResult(
            message_id=message.id,
            inbox_item=inbox_item,
        )
