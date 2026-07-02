"""Shared fixtures for Context Agent tests."""

from __future__ import annotations

from uuid import UUID

import pytest

from app.context.models import FamilyMemberRef
from app.schemas.context_request import ContextRequest
from app.schemas.identity import IdentityResult
from app.schemas.understanding import UnderstandingResult
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


def build_context_request(
    speaker: IdentityResult,
    understanding: UnderstandingResult,
    *,
    family_members: list[FamilyMemberRef] | None = None,
    metadata: dict | None = None,
) -> ContextRequest:
    return ContextRequest(
        identity=speaker,
        understanding=understanding,
        family_members=family_members or [],
        metadata=metadata or {},
    )
