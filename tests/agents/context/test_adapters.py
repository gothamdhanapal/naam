"""Unit tests for understanding adapters."""

from __future__ import annotations

from uuid import UUID

from app.context.models import FamilyMemberRef
from app.agents.context.adapters import adapt_understanding, build_decision_input
from app.schemas.context import Scope
from app.schemas.context_request import ContextRequest
from app.schemas.identity import IdentityResult
from app.schemas.understanding import UnderstandingResult
from tests.agents.context.conftest import CHILD_MEMBER_ID, MEMBER_ID, OTHER_MEMBER_ID


def test_adapt_understanding_maps_core_fields() -> None:
    result = adapt_understanding(
        UnderstandingResult(
            type="TASK",
            title="Pay electricity bill",
            due_date="tomorrow",
            confidence=0.95,
        )
    )

    assert result.type == "TASK"
    assert result.title == "Pay electricity bill"
    assert result.due_date == "tomorrow"
    assert result.confidence == 0.95
    assert result.entities == []


def test_adapt_understanding_reads_optional_fields_from_metadata() -> None:
    result = adapt_understanding(
        UnderstandingResult(type="TASK", title="Book vaccination", confidence=0.9),
        metadata={
            "entities": ["Daughter", "Dance School"],
            "scope_hint": Scope.DEPENDENT.value,
            "owner_id": str(CHILD_MEMBER_ID),
            "responsible_id": str(MEMBER_ID),
            "about_member_id": str(CHILD_MEMBER_ID),
        },
    )

    assert result.entities == ["Daughter", "Dance School"]
    assert result.scope_hint == Scope.DEPENDENT
    assert result.owner_id == CHILD_MEMBER_ID
    assert result.responsible_id == MEMBER_ID
    assert result.about_member_id == CHILD_MEMBER_ID


def test_build_decision_input_uses_request_identity_and_family_members() -> None:
    speaker = IdentityResult(
        family_member_id=MEMBER_ID,
        name="Gowtham",
        role="parent",
        phone_number="15551234567",
        confidence=1.0,
    )
    request = ContextRequest(
        identity=speaker,
        understanding=UnderstandingResult(
            type="TASK",
            title="Pay school fees",
            confidence=0.9,
        ),
        family_members=[
            FamilyMemberRef(
                family_member_id=OTHER_MEMBER_ID,
                name="Priya",
                role="parent",
            )
        ],
        metadata={"owner_id": str(OTHER_MEMBER_ID), "responsible_id": str(MEMBER_ID)},
    )

    decision_input = build_decision_input(request)

    assert decision_input.speaker == speaker
    assert len(decision_input.family_members) == 1
    assert decision_input.understanding.owner_id == OTHER_MEMBER_ID
