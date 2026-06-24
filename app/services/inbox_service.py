from app.core.supabase import supabase

def create_inbox(data):

    response = (
        supabase
        .table("inbox_items")
        .insert(data)
        .execute()
    )

    return response.data