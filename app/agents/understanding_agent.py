from pydantic import BaseModel
from typing import Optional

def understand_message(content: str):

    print("CONTENT RECEIVED:")
    print(content)

class UnderstandingResult(BaseModel):
    type: str
    title: str
    due_date: Optional[str] = None
    confidence: float

import json

from app.core.openai_client import client
from app.schemas.understanding import UnderstandingResult


def understand_message(
    content: str
) -> UnderstandingResult:

    prompt = f"""
You are an AI assistant for a Family Operating System.

Convert the message into JSON.

Allowed types:
- TASK
- EVENT
- NOTE

Return ONLY JSON.

Message:
{content}

Example:

{{
    "type": "TASK",
    "title": "Call dance school",
    "due_date": "tomorrow",
    "confidence": 0.95
}}
"""

    response = client.responses.create(
        model="gpt-5",
        input=prompt
    )
    print("GPT RESPONSE:")
    print(response.output_text)

    result = json.loads(
        response.output_text
    )

    return UnderstandingResult(
        **result
    )