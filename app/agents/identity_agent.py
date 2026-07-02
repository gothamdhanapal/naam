"""
Identity Agent for Naam.

Deterministically resolves the sender of an incoming message to a
family member using the family_members table.

No AI is used. The agent performs lookup and normalization only.
"""

from __future__ import annotations

from uuid import UUID

from app.repositories.family_member_repository import FamilyMemberRepository
from app.schemas.identity import IdentityResult


class IdentityAgent:
    """
    Resolves phone numbers to known family members.

    Answers the first intelligence question: "Who is speaking?"
    """

    _MATCH_CONFIDENCE = 1.0
    _UNKNOWN_CONFIDENCE = 0.0

    def __init__(
        self,
        family_member_repository: FamilyMemberRepository | None = None,
    ) -> None:
        """
        Initialize the Identity Agent.

        Args:
            family_member_repository: Repository for family member lookup.
                Defaults to FamilyMemberRepository when not provided.
        """
        self._repository = family_member_repository or FamilyMemberRepository()

    def resolve(
        self,
        phone_number: str,
        family_id: str,
    ) -> IdentityResult:
        """
        Resolve a sender phone number to a family member.

        Args:
            phone_number: Phone number from the incoming message.
            family_id: Family context for the lookup.

        Returns:
            IdentityResult with member details when matched, otherwise
            an unknown identity with confidence 0.0.
        """
        member = self._repository.get_by_phone(
            family_id=family_id,
            phone_number=phone_number,
        )

        if member is None:
            return IdentityResult(
                phone_number=phone_number,
                confidence=self._UNKNOWN_CONFIDENCE,
            )

        return IdentityResult(
            family_member_id=UUID(member["id"]),
            name=member.get("name"),
            role=member.get("role"),
            phone_number=member.get("phone_number", phone_number),
            confidence=self._MATCH_CONFIDENCE,
        )
