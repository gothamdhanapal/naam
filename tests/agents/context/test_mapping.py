"""Unit tests for ContextDecision mapping."""

from __future__ import annotations

from uuid import UUID

import pytest

from app.agents.context.mapping import build_confidence, map_context_result
from app.context.models import (
    ContextDecision,
    FollowUpDecision,
    OwnershipDecision,
    ParticipantDecision,
    ScopeDecision,
    VisibilityDecision,
)
from app.context.policies.followup_policy import FollowUpPolicy
from app.context.policies.ownership_policy import OwnershipPolicy
from app.context.policies.participant_policy import ParticipantPolicy
from app.context.policies.scope_policy import ScopePolicy
from app.context.policies.visibility_policy import VisibilityPolicy
from app.schemas.context import FollowUpAction, Scope, Visibility
from app.schemas.context_request import ContextRequest
from app.schemas.identity import IdentityResult
from app.schemas.understanding import UnderstandingResult
from tests.conftest import MEMBER_ID


def _decision(**overrides) -> ContextDecision:
    defaults = ContextDecision(
        scope=ScopeDecision(
            scope=Scope.FAMILY,
            confidence=0.8,
            reason_code=ScopePolicy.REASON_FAMILY_DEFAULT,
        ),
        ownership=OwnershipDecision(
            owner_id=None,
            responsible_person_id=None,
            confidence=0.8,
            reason_code=OwnershipPolicy.REASON_FAMILY_UNASSIGNED,
        ),
        participants=ParticipantDecision(
            interested_member_ids=[],
            reason_code=ParticipantPolicy.REASON_ASSIGNED,
        ),
        visibility=VisibilityDecision(
            visibility=Visibility.FAMILY,
            reason_code=VisibilityPolicy.REASON_FAMILY,
        ),
        follow_up=FollowUpDecision(
            action=FollowUpAction.NONE,
            confidence=0.75,
            reason_code=FollowUpPolicy.REASON_NONE,
        ),
        reason_codes=[
            ScopePolicy.REASON_FAMILY_DEFAULT,
            OwnershipPolicy.REASON_FAMILY_UNASSIGNED,
            ParticipantPolicy.REASON_ASSIGNED,
            VisibilityPolicy.REASON_FAMILY,
            FollowUpPolicy.REASON_NONE,
        ],
    )
    return defaults.model_copy(update=overrides)


def _request(
    identity_confidence: float = 1.0,
    understanding_confidence: float = 0.97,
) -> ContextRequest:
    return ContextRequest(
        identity=IdentityResult(
            family_member_id=MEMBER_ID,
            name="Gowtham",
            role="parent",
            phone_number="15551234567",
            confidence=identity_confidence,
        ),
        understanding=UnderstandingResult(
            type="TASK",
            title="Pay electricity bill",
            confidence=understanding_confidence,
        ),
        source="whatsapp",
    )


def test_map_context_result_copies_reason_codes_verbatim() -> None:
    decision = _decision()
    request = _request()

    result = map_context_result(
        request=request,
        decision=decision,
        related_entities=["Home", "Electricity"],
    )

    assert result.reason_codes == decision.reason_codes
    assert result.reason_codes == [
        ScopePolicy.REASON_FAMILY_DEFAULT,
        OwnershipPolicy.REASON_FAMILY_UNASSIGNED,
        ParticipantPolicy.REASON_ASSIGNED,
        VisibilityPolicy.REASON_FAMILY,
        FollowUpPolicy.REASON_NONE,
    ]


def test_build_confidence_preserves_input_and_policy_scores_separately() -> None:
    decision = _decision()
    request = _request(identity_confidence=0.0, understanding_confidence=0.5)

    confidence = build_confidence(request, decision)

    assert confidence.identity == 0.0
    assert confidence.understanding == 0.5
    assert confidence.scope == 0.8
    assert confidence.ownership == 0.8
    assert confidence.follow_up == 0.75
    assert confidence.overall == pytest.approx((0.8 + 0.8 + 0.75) / 3)


def test_map_context_result_populates_metadata() -> None:
    interested_id = UUID("990e8400-e29b-41d4-a716-446655440004")
    decision = _decision(
        participants=ParticipantDecision(
            interested_member_ids=[interested_id],
            reason_code=ParticipantPolicy.REASON_SHARED_INTEREST,
        )
    )
    request = _request()

    result = map_context_result(request, decision, related_entities=[])

    assert result.metadata["source"] == "whatsapp"
    assert result.metadata["interested_member_ids"] == [str(interested_id)]
    assert result.metadata["policy_confidences"]["overall"] == result.confidence.overall
