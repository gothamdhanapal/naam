from app.repositories.inbox_repository import create as create_inbox_item
from app.schemas.inbox import InboxProcessResponse
from app.services.processing_service import process_inbox_item


async def store_inbox(data: dict) -> dict:
    """
    Persist an inbox item without triggering AI processing.

    Used by ingestion paths such as WhatsApp webhooks that store
    messages for later processing.

    Args:
        data: Validated inbox creation payload.

    Returns:
        The persisted inbox item row.
    """
    return create_inbox_item(data)


async def create_inbox(data: dict) -> InboxProcessResponse:
    """
    Persist an inbox item and run the full processing pipeline.

    Args:
        data: Validated inbox creation payload.

    Returns:
        Inbox item, understanding output, execution plan, and results.
    """
    inbox_item = create_inbox_item(data)

    processing_result = await process_inbox_item(
        inbox_id=inbox_item["id"],
        family_id=data["family_id"],
        content=data["raw_content"],
    )

    return InboxProcessResponse(
        inbox_item=inbox_item,
        understanding=processing_result["understanding"],
        execution_plan=processing_result["execution_plan"],
        execution_results=processing_result["execution_results"],
    )
