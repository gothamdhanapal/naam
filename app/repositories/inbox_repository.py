from datetime import datetime, timezone
from typing import Any

from app.core.supabase import supabase


def create(data: dict[str, Any]) -> dict[str, Any]:
    """
    Insert a new inbox item.

    Args:
        data: Inbox fields to persist.

    Returns:
        The created inbox item row.

    Raises:
        RuntimeError: If Supabase does not return the created row.
    """
    response = (
        supabase
        .table("inbox_items")
        .insert(data)
        .execute()
    )

    if not response.data:
        raise RuntimeError("Failed to create inbox item: empty response from Supabase.")

    return response.data[0]


def update_ai_result(
    inbox_id: str,
    ai_result: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Persist AI understanding output on an inbox item.

    Args:
        inbox_id: Primary key of the inbox item.
        ai_result: Structured understanding output.

    Returns:
        Updated inbox item rows returned by Supabase.
    """
    response = (
        supabase
        .table("inbox_items")
        .update(
            {
                "ai_output": ai_result,
                "status": "PROCESSED",
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        .eq("id", inbox_id)
        .execute()
    )

    return response.data
