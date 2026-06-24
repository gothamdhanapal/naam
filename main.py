from fastapi import FastAPI
from app.core.supabase import supabase
from app.schemas.inbox import InboxCreate
from app.services.inbox_service import create_inbox
# from app.agents.understanding_agent import understand

app = FastAPI(
    title="Naam API"
)

@app.get("/")
def health():
    return {
        "status": "ok",
        "app": "Naam"
    }

@app.get("/families")
def get_families():

    response = (
        supabase
        .table("families")
        .select("*")
        .execute()
    )
@app.post("/inbox")
def create_inbox_item(
    payload: InboxCreate
):
    return create_inbox(
        payload.model_dump()
    )
@app.get("/test-ai")
def test_ai():

    return understand(
        "Call dance school tomorrow"
    )

    return response.data