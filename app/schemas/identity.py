"""
Structured output from the Identity Agent.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class IdentityResult(BaseModel):
    """Resolved identity for an incoming message sender."""

    family_member_id: UUID | None = None
    name: str | None = None
    role: str | None = None
    phone_number: str
    confidence: float = Field(ge=0.0, le=1.0)
