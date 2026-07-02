from fastapi import FastAPI

from app.agents.understanding_agent import understand_message
from app.core.supabase import supabase
from app.integrations.whatsapp.webhook import router as whatsapp_webhook_router
from app.schemas.inbox import InboxCreate, InboxProcessResponse
from app.services.inbox_service import ingest_inbox

app = FastAPI(
    title="Naam API"
)

app.include_router(whatsapp_webhook_router)


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
    return await ingest_inbox(payload.model_dump())


@app.get("/test-ai")
def test_ai():
    return understand_message(
        "Call dance school tomorrow"
    )
