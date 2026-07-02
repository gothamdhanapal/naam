"""Shared fixtures for context decision tests."""

from __future__ import annotations

from uuid import UUID

import pytest

from app.context.models import DecisionInput, FamilyMemberRef, UnderstandingContext
from app.schemas.context import Scope
from app.schemas.identity import IdentityResult
from tests.conftest import MEMBER_ID

OTHER_MEMBER_ID = UUID("990e8400-e29b-41d4-a716-446655440004")
CHILD_MEMBER_ID = UUID("aa0e8400-e29b-41d4-a716-446655440005")


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
def spouse_member() -> FamilyMemberRef:
    return FamilyMemberRef(
        family_member_id=OTHER_MEMBER_ID,
        name="Priya",
        role="parent",
    )


@pytest.fixture
def child_member() -> FamilyMemberRef:
    return FamilyMemberRef(
        family_member_id=CHILD_MEMBER_ID,
        name="Anya",
        role="child",
    )


@pytest.fixture
def family_members(spouse_member: FamilyMemberRef, child_member: FamilyMemberRef):
    return [spouse_member, child_member]


def build_input(
    speaker: IdentityResult,
    understanding: UnderstandingContext,
    family_members: list[FamilyMemberRef] | None = None,
) -> DecisionInput:
    return DecisionInput(
        speaker=speaker,
        understanding=understanding,
        family_members=family_members or [],
    )
