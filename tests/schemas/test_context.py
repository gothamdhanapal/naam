"""Unit tests for context schemas."""

from __future__ import annotations

from uuid import UUID

import pytest
from pydantic import ValidationError

from app.schemas.context import (
    ContextConfidence,
    ContextParticipant,
    ContextResult,
    FollowUpAction,
    Relationship,
    Scope,
    Visibility,
)
from app.schemas.identity import IdentityResult
from tests.conftest import MEMBER_ID


def sample_confidence(**overrides: float) -> ContextConfidence:
    values = {
        "identity": 1.0,
        "understanding": 0.97,
        "scope": 0.8,
        "ownership": 0.8,
        "follow_up": 0.75,
        "overall": 0.7833333333333333,
    }
    values.update(overrides)
    return ContextConfidence(**values)


@pytest.fixture
def speaker() -> IdentityResult:
    return IdentityResult(
        family_member_id=MEMBER_ID,
        name="Gowtham",
        role="parent",
        phone_number="15551234567",
        confidence=1.0,
    )


@pytest.fixture
def other_member_id() -> UUID:
    return UUID("990e8400-e29b-41d4-a716-446655440004")


@pytest.fixture
def sample_context(speaker: IdentityResult) -> ContextResult:
    return ContextResult(
        speaker=speaker,
        owner_id=MEMBER_ID,
        scope=Scope.FAMILY,
        participants=[
            ContextParticipant(
                family_member_id=MEMBER_ID,
                relationship=Relationship.OWNER,
            )
        ],
        related_entities=["Home", "Electricity"],
        visibility=Visibility.FAMILY,
        follow_up_action=FollowUpAction.NONE,
        confidence=sample_confidence(),
        reason_codes=["SCOPE_FAMILY_DEFAULT"],
        metadata={"source": "whatsapp"},
    )


class TestScope:
    def test_contains_intelligence_model_values(self) -> None:
        assert Scope.PERSONAL.value == "PERSONAL"
        assert Scope.FAMILY.value == "FAMILY"
        assert Scope.DEPENDENT.value == "DEPENDENT"
        assert Scope.EXTERNAL.value == "EXTERNAL"


class TestContextConfidence:
    def test_rejects_confidence_below_zero(self) -> None:
        with pytest.raises(ValidationError):
            sample_confidence(identity=-0.1)

    def test_is_frozen(self) -> None:
        confidence = sample_confidence()
        with pytest.raises(ValidationError):
            confidence.identity = 0.5


class TestContextResult:
    def test_constructs_with_all_required_fields(
        self,
        sample_context: ContextResult,
    ) -> None:
        assert sample_context.speaker.name == "Gowtham"
        assert sample_context.owner_id == MEMBER_ID
        assert sample_context.scope == Scope.FAMILY
        assert len(sample_context.participants) == 1
        assert sample_context.related_entities == ["Home", "Electricity"]
        assert sample_context.follow_up_action == FollowUpAction.NONE
        assert sample_context.confidence.identity == 1.0
        assert sample_context.reason_codes == ["SCOPE_FAMILY_DEFAULT"]

    def test_defaults_participants_and_related_entities_to_empty_lists(
        self,
        speaker: IdentityResult,
    ) -> None:
        context = ContextResult(
            speaker=speaker,
            scope=Scope.PERSONAL,
            visibility=Visibility.PRIVATE,
            confidence=sample_confidence(),
        )

        assert context.participants == []
        assert context.related_entities == []
        assert context.owner_id is None
        assert context.follow_up_action == FollowUpAction.NONE

    def test_is_frozen(self, sample_context: ContextResult) -> None:
        with pytest.raises(ValidationError):
            sample_context.scope = Scope.PERSONAL

    def test_supports_dependent_scope_with_responsible_id(
        self,
        speaker: IdentityResult,
        other_member_id: UUID,
    ) -> None:
        context = ContextResult(
            speaker=speaker,
            owner_id=other_member_id,
            responsible_id=MEMBER_ID,
            scope=Scope.DEPENDENT,
            visibility=Visibility.FAMILY,
            follow_up_action=FollowUpAction.WATCH,
            related_entities=["Daughter", "Dance School"],
            confidence=sample_confidence(),
        )

        assert context.responsible_id == MEMBER_ID
        assert context.follow_up_action == FollowUpAction.WATCH

    def test_serializes_to_json_compatible_dict(
        self,
        sample_context: ContextResult,
    ) -> None:
        payload = sample_context.model_dump(mode="json")

        assert payload["scope"] == Scope.FAMILY.value
        assert payload["related_entities"] == ["Home", "Electricity"]
        assert payload["confidence"]["overall"] == pytest.approx(0.7833333333333333)

    def test_deserializes_from_dict(
        self,
        speaker: IdentityResult,
        other_member_id: UUID,
    ) -> None:
        payload = {
            "speaker": speaker.model_dump(mode="json"),
            "owner_id": str(other_member_id),
            "scope": Scope.PERSONAL.value,
            "participants": [
                {
                    "family_member_id": str(MEMBER_ID),
                    "relationship": Relationship.OWNER.value,
                }
            ],
            "related_entities": ["Gym"],
            "visibility": Visibility.PRIVATE.value,
            "follow_up_action": FollowUpAction.REMIND_OWNER.value,
            "confidence": sample_confidence().model_dump(mode="json"),
            "reason_codes": ["SCOPE_PERSONAL_LANGUAGE"],
            "metadata": {},
        }

        context = ContextResult.model_validate(payload)

        assert context.scope == Scope.PERSONAL
        assert context.follow_up_action == FollowUpAction.REMIND_OWNER
        assert context.related_entities == ["Gym"]
