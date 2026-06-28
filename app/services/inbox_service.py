from app.core.supabase import supabase
from app.services.processing_service import process_inbox_item


def create_inbox(data):

    response = (
        supabase
        .table("inbox_items")
        .insert(data)
        .execute()
    )

    inbox_item = response.data[0]

    print("INBOX ITEM:")
    print(inbox_item)

    process_inbox_item(
        inbox_item["id"],
        inbox_item["raw_content"]
    )

    return inbox_item