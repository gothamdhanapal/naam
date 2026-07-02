"""Unit tests for context schemas."""

from __future__ import annotations

from uuid import UUID

import pytest
from pydantic import ValidationError

from app.schemas.context import (
    ContextParticipant,
    ContextResult,
    Relationship,
    Scope,
    Visibility,
)
from app.schemas.identity import IdentityResult
from tests.conftest import MEMBER_ID


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
        entities=["Home", "Electricity"],
        visibility=Visibility.FAMILY,
        follow_up_required=False,
        confidence=0.92,
    )


class TestScope:
    def test_contains_intelligence_model_values(self) -> None:
        assert Scope.PERSONAL.value == "PERSONAL"
        assert Scope.FAMILY.value == "FAMILY"
        assert Scope.DEPENDENT.value == "DEPENDENT"
        assert Scope.EXTERNAL.value == "EXTERNAL"

    def test_is_string_enum(self) -> None:
        assert isinstance(Scope.FAMILY, str)
        assert Scope.FAMILY == "FAMILY"


class TestVisibility:
    def test_contains_expected_values(self) -> None:
        assert Visibility.PRIVATE.value == "PRIVATE"
        assert Visibility.FAMILY.value == "FAMILY"
        assert Visibility.CAREGIVERS.value == "CAREGIVERS"
        assert Visibility.EXTERNAL.value == "EXTERNAL"


class TestRelationship:
    def test_contains_responsibility_model_values(self) -> None:
        assert Relationship.OWNER.value == "OWNER"
        assert Relationship.RESPONSIBLE.value == "RESPONSIBLE"
        assert Relationship.INTERESTED.value == "INTERESTED"
        assert Relationship.PARTICIPANT.value == "PARTICIPANT"
        assert Relationship.CAREGIVER.value == "CAREGIVER"


class TestContextParticipant:
    def test_requires_family_member_id_and_relationship(self) -> None:
        participant = ContextParticipant(
            family_member_id=MEMBER_ID,
            relationship=Relationship.RESPONSIBLE,
        )

        assert participant.family_member_id == MEMBER_ID
        assert participant.relationship == Relationship.RESPONSIBLE

    def test_rejects_invalid_uuid(self) -> None:
        with pytest.raises(ValidationError):
            ContextParticipant(
                family_member_id="not-a-uuid",
                relationship=Relationship.PARTICIPANT,
            )


class TestContextResult:
    def test_constructs_with_all_required_fields(
        self,
        sample_context: ContextResult,
    ) -> None:
        assert sample_context.speaker.name == "Gowtham"
        assert sample_context.owner_id == MEMBER_ID
        assert sample_context.scope == Scope.FAMILY
        assert len(sample_context.participants) == 1
        assert sample_context.participants[0].relationship == Relationship.OWNER
        assert sample_context.entities == ["Home", "Electricity"]
        assert sample_context.visibility == Visibility.FAMILY
        assert sample_context.follow_up_required is False
        assert sample_context.confidence == 0.92

    def test_defaults_participants_and_entities_to_empty_lists(
        self,
        speaker: IdentityResult,
    ) -> None:
        context = ContextResult(
            speaker=speaker,
            scope=Scope.PERSONAL,
            visibility=Visibility.PRIVATE,
            confidence=0.8,
        )

        assert context.participants == []
        assert context.entities == []
        assert context.owner_id is None
        assert context.follow_up_required is False

    def test_supports_multiple_participants(
        self,
        speaker: IdentityResult,
        other_member_id: UUID,
    ) -> None:
        context = ContextResult(
            speaker=speaker,
            owner_id=other_member_id,
            scope=Scope.FAMILY,
            participants=[
                ContextParticipant(
                    family_member_id=MEMBER_ID,
                    relationship=Relationship.RESPONSIBLE,
                ),
                ContextParticipant(
                    family_member_id=other_member_id,
                    relationship=Relationship.INTERESTED,
                ),
            ],
            entities=["School"],
            visibility=Visibility.FAMILY,
            confidence=0.88,
        )

        assert len(context.participants) == 2
        assert context.participants[1].relationship == Relationship.INTERESTED

    def test_supports_dependent_scope_with_caregiver_visibility(
        self,
        speaker: IdentityResult,
    ) -> None:
        context = ContextResult(
            speaker=speaker,
            scope=Scope.DEPENDENT,
            visibility=Visibility.CAREGIVERS,
            entities=["Daughter", "Dance School"],
            follow_up_required=True,
            confidence=0.75,
        )

        assert context.scope == Scope.DEPENDENT
        assert context.visibility == Visibility.CAREGIVERS
        assert context.follow_up_required is True

    def test_supports_external_scope(
        self,
        speaker: IdentityResult,
    ) -> None:
        context = ContextResult(
            speaker=speaker,
            scope=Scope.EXTERNAL,
            visibility=Visibility.EXTERNAL,
            entities=["Electricity Board"],
            confidence=0.6,
        )

        assert context.scope == Scope.EXTERNAL
        assert context.visibility == Visibility.EXTERNAL

    def test_rejects_confidence_below_zero(self, speaker: IdentityResult) -> None:
        with pytest.raises(ValidationError):
            ContextResult(
                speaker=speaker,
                scope=Scope.FAMILY,
                visibility=Visibility.FAMILY,
                confidence=-0.1,
            )

    def test_rejects_confidence_above_one(self, speaker: IdentityResult) -> None:
        with pytest.raises(ValidationError):
            ContextResult(
                speaker=speaker,
                scope=Scope.FAMILY,
                visibility=Visibility.FAMILY,
                confidence=1.1,
            )

    def test_serializes_to_json_compatible_dict(
        self,
        sample_context: ContextResult,
    ) -> None:
        payload = sample_context.model_dump(mode="json")

        assert payload["scope"] == Scope.FAMILY.value
        assert payload["visibility"] == Visibility.FAMILY.value
        assert payload["speaker"]["family_member_id"] == str(MEMBER_ID)
        assert payload["participants"][0]["relationship"] == Relationship.OWNER.value
        assert payload["entities"] == ["Home", "Electricity"]

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
            "entities": ["Gym"],
            "visibility": Visibility.PRIVATE.value,
            "follow_up_required": True,
            "confidence": 0.95,
        }

        context = ContextResult.model_validate(payload)

        assert context.scope == Scope.PERSONAL
        assert context.owner_id == other_member_id
        assert context.follow_up_required is True
        assert context.entities == ["Gym"]

    def test_accepts_unknown_speaker_in_nested_identity(
        self,
    ) -> None:
        unknown_speaker = IdentityResult(
            phone_number="19998887777",
            confidence=0.0,
        )
        context = ContextResult(
            speaker=unknown_speaker,
            scope=Scope.FAMILY,
            visibility=Visibility.FAMILY,
            confidence=0.5,
        )

        assert context.speaker.family_member_id is None
        assert context.speaker.confidence == 0.0

    def test_owner_id_may_be_none_for_unassigned_context(
        self,
        speaker: IdentityResult,
    ) -> None:
        context = ContextResult(
            speaker=speaker,
            owner_id=None,
            scope=Scope.FAMILY,
            visibility=Visibility.FAMILY,
            confidence=0.7,
        )

        assert context.owner_id is None
