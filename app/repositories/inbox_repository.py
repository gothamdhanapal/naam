from datetime import datetime, timezone

from app.core.supabase import supabase


def update_ai_result(
    inbox_id: str,
    ai_result: dict
):
    response = (
        supabase
        .table("inbox_items")
        .update(
            {
                "ai_output": ai_result,
                "status": "PROCESSED",
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
        )
        .eq("id", inbox_id)
        .execute()
    )

    return response.data