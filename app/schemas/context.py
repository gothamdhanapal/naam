"""
Structured output from the Context Agent.

Context explains what a conversation means for the family — who is
involved, who owns it, and how widely it should be visible.
"""

from __future__ import annotations

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.identity import IdentityResult


class Scope(str, Enum):
    """The mental model a conversation belongs to."""

    PERSONAL = "PERSONAL"
    FAMILY = "FAMILY"
    DEPENDENT = "DEPENDENT"
    EXTERNAL = "EXTERNAL"


class Visibility(str, Enum):
    """Who may see or act on information derived from the conversation."""

    OWNER_ONLY = "OWNER_ONLY"
    PRIVATE = "PRIVATE"
    FAMILY = "FAMILY"
    CAREGIVERS = "CAREGIVERS"
    EXTERNAL = "EXTERNAL"


class FollowUpAction(str, Enum):
    """Recommended follow-up behaviour for a conversation."""

    NONE = "NONE"
    REMIND_OWNER = "REMIND_OWNER"
    WAIT_RESPONSE = "WAIT_RESPONSE"
    WATCH = "WATCH"
    ESCALATE = "ESCALATE"


class Relationship(str, Enum):
    """How a participant relates to a conversation or commitment."""

    OWNER = "OWNER"
    RESPONSIBLE = "RESPONSIBLE"
    INTERESTED = "INTERESTED"
    PARTICIPANT = "PARTICIPANT"
    CAREGIVER = "CAREGIVER"


class ContextParticipant(BaseModel):
    """A family member involved in the conversation context."""

    family_member_id: UUID
    relationship: Relationship


class ContextResult(BaseModel):
    """
    Structured context produced after understanding an incoming message.

    Answers: who is speaking, who owns it, who else is involved, what
    entities it relates to, and how visible it should be.
    """

    speaker: IdentityResult
    owner_id: UUID | None = None
    scope: Scope
    participants: list[ContextParticipant] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    visibility: Visibility
    follow_up_required: bool = False
    confidence: float = Field(ge=0.0, le=1.0)
