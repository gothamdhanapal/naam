"""
Input and output models for the Context Decision Matrix.

These models are internal to deterministic context reasoning. The future
Context Agent will map `ContextDecision` outputs into `ContextResult`.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.context import (
    ContextParticipant,
    FollowUpAction,
    Scope,
    Visibility,
)
from app.schemas.identity import IdentityResult


class FamilyMemberRef(BaseModel):
    """Lightweight family member reference for deterministic rules."""

    family_member_id: UUID
    name: str | None = None
    role: str | None = None


class UnderstandingContext(BaseModel):
    """Structured understanding fields consumed by context policies."""

    type: str
    title: str
    entities: list[str] = Field(default_factory=list)
    due_date: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    scope_hint: Scope | None = None
    owner_id: UUID | None = None
    responsible_id: UUID | None = None
    about_member_id: UUID | None = None


class DecisionInput(BaseModel):
    """Combined input for context decision policies."""

    speaker: IdentityResult
    understanding: UnderstandingContext
    family_members: list[FamilyMemberRef] = Field(default_factory=list)


class ScopeDecision(BaseModel):
    """Scope determination for a conversation."""

    scope: Scope
    confidence: float = Field(ge=0.0, le=1.0)


class OwnershipDecision(BaseModel):
    """Ownership and responsibility determination."""

    owner_id: UUID | None = None
    responsible_person_id: UUID | None = None
    confidence: float = Field(ge=0.0, le=1.0)


class ParticipantDecision(BaseModel):
    """Participant and interest determination."""

    participants: list[ContextParticipant] = Field(default_factory=list)
    interested_member_ids: list[UUID] = Field(default_factory=list)


class VisibilityDecision(BaseModel):
    """Visibility determination for derived actions."""

    visibility: Visibility


class FollowUpDecision(BaseModel):
    """Follow-up recommendation for Naam."""

    action: FollowUpAction
    confidence: float = Field(ge=0.0, le=1.0)


class ContextDecision(BaseModel):
    """Full deterministic context decision produced by the matrix."""

    scope: ScopeDecision
    ownership: OwnershipDecision
    participants: ParticipantDecision
    visibility: VisibilityDecision
    follow_up: FollowUpDecision
