"""
Map ContextDecision outputs into ContextResult.
"""

from __future__ import annotations

from typing import Any

from app.context.models import ContextDecision
from app.schemas.context import ContextConfidence, ContextResult
from app.schemas.context_request import ContextRequest


def map_context_result(
    request: ContextRequest,
    decision: ContextDecision,
    related_entities: list[str],
) -> ContextResult:
    """
    Copy matrix decisions into a public ContextResult.

    Reason codes are copied verbatim from ContextDecision. Confidence
    preserves input and policy scores separately.
    """
    confidence = build_confidence(request, decision)
    metadata = build_metadata(request, decision, confidence)

    return ContextResult(
        speaker=request.identity,
        owner_id=decision.ownership.owner_id,
        responsible_id=decision.ownership.responsible_person_id,
        scope=decision.scope.scope,
        participants=list(decision.participants.participants),
        related_entities=list(related_entities),
        visibility=decision.visibility.visibility,
        follow_up_action=decision.follow_up.action,
        confidence=confidence,
        reason_codes=list(decision.reason_codes),
        metadata=metadata,
    )


def build_confidence(
    request: ContextRequest,
    decision: ContextDecision,
) -> ContextConfidence:
    """Assemble structured confidence from request and policy decisions."""
    scope = decision.scope.confidence
    ownership = decision.ownership.confidence
    follow_up = decision.follow_up.confidence
    overall = (scope + ownership + follow_up) / 3

    return ContextConfidence(
        identity=request.identity.confidence,
        understanding=request.understanding.confidence,
        scope=scope,
        ownership=ownership,
        follow_up=follow_up,
        overall=overall,
    )


def build_metadata(
    request: ContextRequest,
    decision: ContextDecision,
    confidence: ContextConfidence,
) -> dict[str, Any]:
    """Populate traceability metadata for downstream inspection."""
    metadata: dict[str, Any] = dict(request.metadata)

    if request.conversation_id is not None:
        metadata["conversation_id"] = str(request.conversation_id)
    if request.source is not None:
        metadata["source"] = request.source
    if request.received_at is not None:
        metadata["received_at"] = request.received_at.isoformat()
    if request.family_id is not None:
        metadata["family_id"] = str(request.family_id)

    metadata["identity_confidence"] = confidence.identity
    metadata["understanding_confidence"] = confidence.understanding
    metadata["policy_confidences"] = {
        "scope": confidence.scope,
        "ownership": confidence.ownership,
        "follow_up": confidence.follow_up,
        "overall": confidence.overall,
    }

    if decision.participants.interested_member_ids:
        metadata["interested_member_ids"] = [
            str(member_id)
            for member_id in decision.participants.interested_member_ids
        ]

    return metadata
