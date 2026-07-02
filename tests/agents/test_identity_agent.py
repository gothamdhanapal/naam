"""Unit tests for the Identity Agent."""

from __future__ import annotations

from unittest.mock import MagicMock
from uuid import UUID

import pytest

from app.agents.identity_agent import IdentityAgent
from app.repositories.family_member_repository import FamilyMemberRepository
from tests.conftest import FAMILY_ID, MEMBER_ID


@pytest.fixture
def sample_member_row() -> dict:
    return {
        "id": str(MEMBER_ID),
        "family_id": str(FAMILY_ID),
        "name": "Gowtham",
        "phone_number": "15551234567",
        "role": "parent",
    }


@pytest.fixture
def identity_agent(sample_member_row: dict) -> IdentityAgent:
    repository = MagicMock(spec=FamilyMemberRepository)
    repository.get_by_phone.return_value = sample_member_row
    return IdentityAgent(family_member_repository=repository)


def test_resolve_returns_identity_result_for_known_member(
    identity_agent: IdentityAgent,
    sample_member_row: dict,
) -> None:
    result = identity_agent.resolve(
        phone_number="15551234567",
        family_id=str(FAMILY_ID),
    )

    identity_agent._repository.get_by_phone.assert_called_once_with(
        family_id=str(FAMILY_ID),
        phone_number="15551234567",
    )
    assert result.family_member_id == MEMBER_ID
    assert result.name == "Gowtham"
    assert result.role == "parent"
    assert result.phone_number == "15551234567"
    assert result.confidence == 1.0


def test_resolve_returns_unknown_identity_when_member_not_found() -> None:
    repository = MagicMock(spec=FamilyMemberRepository)
    repository.get_by_phone.return_value = None
    agent = IdentityAgent(family_member_repository=repository)

    result = agent.resolve(
        phone_number="19998887777",
        family_id=str(FAMILY_ID),
    )

    assert result.family_member_id is None
    assert result.name is None
    assert result.role is None
    assert result.phone_number == "19998887777"
    assert result.confidence == 0.0
