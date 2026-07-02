"""
Adapt Context Agent inputs into Context Decision Matrix models.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.context.models import UnderstandingContext
from app.schemas.context import Scope
from app.schemas.context_request import ContextRequest
from app.schemas.understanding import UnderstandingResult


def adapt_understanding(
    understanding: UnderstandingResult,
    metadata: dict[str, Any] | None = None,
) -> UnderstandingContext:
    """
    Map UnderstandingResult and optional metadata into UnderstandingContext.

    Optional policy fields not yet on UnderstandingResult are read from
    metadata using the same field names as UnderstandingContext.
    """
    request_metadata = metadata or {}

    return UnderstandingContext(
        type=understanding.type,
        title=understanding.title,
        entities=_coerce_string_list(request_metadata.get("entities")),
        due_date=understanding.due_date,
        confidence=understanding.confidence,
        scope_hint=_coerce_scope(request_metadata.get("scope_hint")),
        owner_id=_coerce_uuid(request_metadata.get("owner_id")),
        responsible_id=_coerce_uuid(request_metadata.get("responsible_id")),
        about_member_id=_coerce_uuid(request_metadata.get("about_member_id")),
    )


def build_decision_input(request: ContextRequest):
    """Build DecisionInput from a ContextRequest."""
    from app.context.models import DecisionInput

    return DecisionInput(
        speaker=request.identity,
        understanding=adapt_understanding(
            request.understanding,
            request.metadata,
        ),
        family_members=request.family_members,
    )


def _coerce_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _coerce_uuid(value: Any) -> UUID | None:
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    return UUID(str(value))


def _coerce_scope(value: Any) -> Scope | None:
    if value is None:
        return None
    if isinstance(value, Scope):
        return value
    return Scope(str(value))
