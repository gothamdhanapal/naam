"""
Input contract for the Context Agent.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.context.models import FamilyMemberRef
from app.schemas.identity import IdentityResult
from app.schemas.understanding import UnderstandingResult


class ContextRequest(BaseModel):
    """Combined input for ContextAgent.build()."""

    identity: IdentityResult
    understanding: UnderstandingResult
    family_members: list[FamilyMemberRef] = Field(default_factory=list)
    conversation_id: UUID | None = None
    source: str | None = None
    received_at: datetime | None = None
    family_id: UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
