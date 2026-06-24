from pydantic import BaseModel

class InboxCreate(BaseModel):
    family_id: str
    source_type: str
    raw_content: str