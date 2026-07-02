"""Unit tests for FamilyMemberRepository."""

from __future__ import annotations

from app.repositories.family_member_repository import (
    FamilyMemberRepository,
    normalize_phone_number,
)
from tests.conftest import FAMILY_ID, MEMBER_ID, build_supabase_client, build_supabase_response


def test_normalize_phone_number_strips_formatting() -> None:
    assert normalize_phone_number("+1 (555) 123-4567") == "15551234567"
    assert normalize_phone_number("15551234567") == "15551234567"


def test_get_by_phone_returns_exact_match() -> None:
    member_row = {
        "id": str(MEMBER_ID),
        "family_id": str(FAMILY_ID),
        "name": "Gowtham",
        "phone_number": "15551234567",
        "role": "parent",
    }
    response = build_supabase_response([member_row])
    client = build_supabase_client(response)
    repository = FamilyMemberRepository(client=client)

    result = repository.get_by_phone(
        family_id=str(FAMILY_ID),
        phone_number="15551234567",
    )

    assert result == member_row
    client.table.assert_called_with("family_members")


def test_get_by_phone_matches_normalized_phone_numbers() -> None:
    member_row = {
        "id": str(MEMBER_ID),
        "family_id": str(FAMILY_ID),
        "name": "Gowtham",
        "phone_number": "+1-555-123-4567",
        "role": "parent",
    }
    response = build_supabase_response([member_row])
    client = build_supabase_client(response)
    repository = FamilyMemberRepository(client=client)

    result = repository.get_by_phone(
        family_id=str(FAMILY_ID),
        phone_number="15551234567",
    )

    assert result == member_row


def test_get_by_phone_returns_none_when_no_match() -> None:
    member_row = {
        "id": str(MEMBER_ID),
        "family_id": str(FAMILY_ID),
        "name": "Gowtham",
        "phone_number": "15551234567",
        "role": "parent",
    }
    response = build_supabase_response([member_row])
    client = build_supabase_client(response)
    repository = FamilyMemberRepository(client=client)

    result = repository.get_by_phone(
        family_id=str(FAMILY_ID),
        phone_number="19998887777",
    )

    assert result is None
