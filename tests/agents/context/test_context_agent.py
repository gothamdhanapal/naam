"""Unit tests for the Context Agent."""

from __future__ import annotations

from uuid import UUID

import pytest
from pydantic import ValidationError

from app.agents.context.context_agent import ContextAgent
from app.context.policies.followup_policy import FollowUpPolicy
from app.context.policies.ownership_policy import OwnershipPolicy
from app.context.policies.participant_policy import ParticipantPolicy
from app.context.policies.scope_policy import ScopePolicy
from app.context.policies.visibility_policy import VisibilityPolicy
from app.schemas.context import FollowUpAction, Relationship, Scope, Visibility
from app.schemas.context_request import ContextRequest
from app.schemas.identity import IdentityResult
from app.schemas.understanding import UnderstandingResult
from tests.agents.context.conftest import (
    CHILD_MEMBER_ID,
    MEMBER_ID,
    OTHER_MEMBER_ID,
    build_context_request,
)
from tests.conftest import FAMILY_ID


def test_personal_reminder_scenario(speaker) -> None:
    agent = ContextAgent()
    request = build_context_request(
        speaker,
        UnderstandingResult(
            type="NOTE",
            title="Remind me to call the gym tomorrow",
            due_date="tomorrow",
            confidence=0.97,
        ),
    )

    result = agent.build(request)

    assert result.scope == Scope.PERSONAL
    assert result.owner_id == MEMBER_ID
    assert result.responsible_id == MEMBER_ID
    assert result.visibility == Visibility.OWNER_ONLY
    assert result.follow_up_action == FollowUpAction.REMIND_OWNER
    assert ScopePolicy.REASON_PERSONAL_LANGUAGE in result.reason_codes
    assert result.speaker == speaker


def test_family_task_scenario(speaker, family_members) -> None:
    agent = ContextAgent()
    request = build_context_request(
        speaker,
        UnderstandingResult(
            type="TASK",
            title="Pay electricity bill",
            confidence=0.97,
        ),
        family_members=family_members,
        metadata={"entities": ["Home", "Electricity"]},
    )

    result = agent.build(request)

    assert result.scope == Scope.FAMILY
    assert result.owner_id is None
    assert result.responsible_id is None
    assert result.related_entities == ["Home", "Electricity"]
    assert result.follow_up_action == FollowUpAction.NONE
    assert OTHER_MEMBER_ID in [
        UUID(member_id)
        for member_id in result.metadata.get("interested_member_ids", [])
    ]


def test_dependent_task_scenario(speaker, family_members) -> None:
    agent = ContextAgent()
    request = build_context_request(
        speaker,
        UnderstandingResult(
            type="TASK",
            title="Pick up Anya from dance class",
            confidence=0.9,
        ),
        family_members=family_members,
        metadata={
            "entities": ["Daughter", "Dance School"],
            "about_member_id": str(CHILD_MEMBER_ID),
        },
    )

    result = agent.build(request)

    assert result.scope == Scope.DEPENDENT
    assert result.owner_id == CHILD_MEMBER_ID
    relationships = {
        participant.family_member_id: participant.relationship
        for participant in result.participants
    }
    assert relationships[MEMBER_ID] == Relationship.CAREGIVER


def test_unknown_identity_returns_partial_result_without_failure() -> None:
    agent = ContextAgent()
    request = build_context_request(
        IdentityResult(phone_number="19998887777", confidence=0.0),
        UnderstandingResult(
            type="TASK",
            title="Pay electricity bill",
            confidence=0.97,
        ),
    )

    result = agent.build(request)

    assert result.speaker.family_member_id is None
    assert result.confidence.identity == 0.0
    assert result.confidence.overall > 0.0


def test_low_understanding_confidence_does_not_reduce_overall_confidence(
    speaker,
) -> None:
    agent = ContextAgent()
    request = build_context_request(
        speaker,
        UnderstandingResult(
            type="TASK",
            title="Pay electricity bill",
            confidence=0.65,
        ),
        metadata={"entities": ["Home", "Electricity"]},
    )

    result = agent.build(request)

    assert result.confidence.understanding == 0.65
    assert result.confidence.overall == pytest.approx((0.8 + 0.8 + 0.75) / 3)


def test_explicit_ownership_via_metadata(speaker, family_members) -> None:
    agent = ContextAgent()
    request = build_context_request(
        speaker,
        UnderstandingResult(type="TASK", title="Pay school fees", confidence=0.95),
        family_members=family_members,
        metadata={
            "owner_id": str(OTHER_MEMBER_ID),
            "responsible_id": str(MEMBER_ID),
        },
    )

    result = agent.build(request)

    assert result.owner_id == OTHER_MEMBER_ID
    assert result.responsible_id == MEMBER_ID
    assert OwnershipPolicy.REASON_EXPLICIT in result.reason_codes


def test_context_result_is_immutable(speaker) -> None:
    agent = ContextAgent()
    request = build_context_request(
        speaker,
        UnderstandingResult(type="TASK", title="Pay electricity bill", confidence=0.9),
    )

    result = agent.build(request)

    with pytest.raises(ValidationError):
        result.scope = Scope.PERSONAL


def test_request_trace_fields_appear_in_metadata(speaker) -> None:
    conversation_id = UUID("bb0e8400-e29b-41d4-a716-446655440006")
    agent = ContextAgent()
    request = ContextRequest(
        identity=speaker,
        understanding=UnderstandingResult(
            type="TASK",
            title="Pay electricity bill",
            confidence=0.9,
        ),
        conversation_id=conversation_id,
        source="whatsapp",
        family_id=FAMILY_ID,
    )

    result = agent.build(request)

    assert result.metadata["conversation_id"] == str(conversation_id)
    assert result.metadata["source"] == "whatsapp"
    assert result.metadata["family_id"] == str(FAMILY_ID)
