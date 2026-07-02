"""Unit tests for ParticipantPolicy."""

from __future__ import annotations

from app.context.models import (
    OwnershipDecision,
    ScopeDecision,
    UnderstandingContext,
)
from app.context.policies.participant_policy import ParticipantPolicy
from app.schemas.context import Relationship, Scope
from tests.context.conftest import (
    CHILD_MEMBER_ID,
    MEMBER_ID,
    OTHER_MEMBER_ID,
    build_input,
)


def test_multiple_participants_include_owner_and_responsible(speaker, family_members) -> None:
    policy = ParticipantPolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="TASK",
            title="Pay school fees",
            owner_id=OTHER_MEMBER_ID,
            responsible_id=MEMBER_ID,
        ),
        family_members=family_members,
    )

    result = policy.evaluate(
        decision_input,
        ScopeDecision(scope=Scope.FAMILY, confidence=1.0),
        OwnershipDecision(
            owner_id=OTHER_MEMBER_ID,
            responsible_person_id=MEMBER_ID,
            confidence=1.0,
        ),
    )

    relationships = {
        participant.family_member_id: participant.relationship
        for participant in result.participants
    }

    assert relationships[MEMBER_ID] == Relationship.RESPONSIBLE
    assert relationships[OTHER_MEMBER_ID] == Relationship.OWNER
    assert CHILD_MEMBER_ID not in result.interested_member_ids
    assert len(result.participants) == 2


def test_dependent_scope_marks_speaker_as_caregiver(speaker, family_members) -> None:
    policy = ParticipantPolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="TASK",
            title="Pick up from dance class",
            about_member_id=CHILD_MEMBER_ID,
        ),
        family_members=family_members,
    )

    result = policy.evaluate(
        decision_input,
        ScopeDecision(scope=Scope.DEPENDENT, confidence=0.9),
        OwnershipDecision(
            owner_id=CHILD_MEMBER_ID,
            responsible_person_id=MEMBER_ID,
            confidence=0.85,
        ),
    )

    relationships = {
        participant.family_member_id: participant.relationship
        for participant in result.participants
    }

    assert relationships[MEMBER_ID] == Relationship.CAREGIVER
    assert relationships[CHILD_MEMBER_ID] == Relationship.OWNER


def test_personal_scope_has_no_interested_members(speaker, family_members) -> None:
    policy = ParticipantPolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="NOTE",
            title="Remind me to read",
        ),
        family_members=family_members,
    )

    result = policy.evaluate(
        decision_input,
        ScopeDecision(scope=Scope.PERSONAL, confidence=0.9),
        OwnershipDecision(
            owner_id=MEMBER_ID,
            responsible_person_id=MEMBER_ID,
            confidence=0.9,
        ),
    )

    assert result.interested_member_ids == []
