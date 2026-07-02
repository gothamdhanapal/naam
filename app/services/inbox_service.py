"""
Inbox domain service.

Single entry point for all incoming information. Persistence and AI
processing are orchestrated here; callers outside this service should
not bypass these methods.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from app.models.inbox import InboxStatus
import app.repositories.inbox_repository as inbox_repository
from app.schemas.inbox import InboxProcessResponse
from app.services.processing_service import process_inbox_item

logger = logging.getLogger(__name__)

ProcessInboxFn = Callable[..., Awaitable[dict[str, Any]]]


class InboxService:
    """
    Domain service for inbox persistence and processing.

    ``persist_inbox`` stores incoming information only.
    ``ingest_inbox`` stores and runs the full processing pipeline.
    """

    def __init__(
        self,
        process_inbox_item_fn: ProcessInboxFn | None = None,
    ) -> None:
        """
        Initialize the inbox service.

        Args:
            process_inbox_item_fn: Processing pipeline callable. Defaults
                to ``process_inbox_item`` when not provided.
        """
        self._process_inbox_item = process_inbox_item_fn or process_inbox_item

    async def persist_inbox(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Persist an inbox item without triggering AI processing.

        Args:
            data: Validated inbox creation payload.

        Returns:
            The persisted inbox item row with status RECEIVED.
        """
        payload = {
            **data,
            "status": InboxStatus.RECEIVED.value,
        }
        return inbox_repository.create(payload)

    async def ingest_inbox(self, data: dict[str, Any]) -> InboxProcessResponse:
        """
        Persist an inbox item and run the full processing pipeline.

        Processing failures are captured and returned without raising.
        The inbox item is marked FAILED when processing cannot complete.

        Args:
            data: Validated inbox creation payload.

        Returns:
            Inbox item, processing output, and optional processing error.
        """
        inbox_item = await self.persist_inbox(data)
        inbox_id = inbox_item["id"]

        try:
            inbox_repository.update_status(inbox_id, InboxStatus.PROCESSING)
            processing_result = await self._process_inbox_item(
                inbox_id=inbox_id,
                family_id=data["family_id"],
                content=data["raw_content"],
            )
            refreshed = inbox_repository.get_by_id(inbox_id)
            return InboxProcessResponse(
                inbox_item=refreshed or inbox_item,
                understanding=processing_result["understanding"],
                execution_plan=processing_result["execution_plan"],
                execution_results=processing_result["execution_results"],
            )
        except Exception as exc:
            logger.exception("Inbox processing failed: inbox_id=%s", inbox_id)
            failed_item = inbox_repository.update_status(
                inbox_id,
                InboxStatus.FAILED,
            )
            return InboxProcessResponse(
                inbox_item=failed_item or {
                    **inbox_item,
                    "status": InboxStatus.FAILED.value,
                },
                processing_error=str(exc),
            )


_default_inbox_service = InboxService()


async def persist_inbox(data: dict[str, Any]) -> dict[str, Any]:
    """Persist an inbox item using the default InboxService instance."""
    return await _default_inbox_service.persist_inbox(data)


async def ingest_inbox(data: dict[str, Any]) -> InboxProcessResponse:
    """Ingest and process an inbox item using the default InboxService instance."""
    return await _default_inbox_service.ingest_inbox(data)
