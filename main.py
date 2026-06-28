from fastapi import FastAPI

from app.agents.understanding_agent import understand_message
from app.core.supabase import supabase
from app.schemas.inbox import InboxCreate, InboxProcessResponse
from app.services.inbox_service import create_inbox

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
    return response.data


@app.post("/inbox", response_model=InboxProcessResponse)
async def create_inbox_item(payload: InboxCreate):
    return await create_inbox(payload.model_dump())


@app.get("/test-ai")
def test_ai():
    return understand_message(
        "Call dance school tomorrow"
    )
