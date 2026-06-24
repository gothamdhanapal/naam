from fastapi import FastAPI
from app.core.supabase import supabase

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