"""
Repository for family member persistence.

This is the only layer permitted to read from the ``family_members``
table in Supabase.

Expected ``family_members`` table columns:

- id (uuid, primary key)
- family_id (uuid, foreign key)
- name (text)
- phone_number (text)
- role (text, nullable)
"""

from __future__ import annotations

import re
from typing import Any, Optional

from supabase import Client

from app.core.supabase import supabase


def normalize_phone_number(phone_number: str) -> str:
    """
    Normalize a phone number for deterministic comparison.

    Strips whitespace and non-digit characters except a leading plus sign,
    then returns digits only.
    """
    stripped = phone_number.strip()
    if stripped.startswith("+"):
        stripped = stripped[1:]
    return re.sub(r"\D", "", stripped)


class FamilyMemberRepository:
    """
    Data access layer for family members.

    Accepts a Supabase client via constructor injection so callers and
    tests can supply a real or mocked client without touching globals.
    """

    _TABLE = "family_members"

    def __init__(self, client: Client | None = None) -> None:
        """
        Initialize the repository.

        Args:
            client: Supabase client instance. Defaults to the application
                client when not provided.
        """
        self._client = client or supabase

    def get_by_phone(
        self,
        family_id: str,
        phone_number: str,
    ) -> Optional[dict[str, Any]]:
        """
        Find a family member by phone number within a family.

        Matching is deterministic: exact string match first, then
        normalized digit-only comparison.

        Args:
            family_id: Family that owns the member record.
            phone_number: Sender phone number to resolve.

        Returns:
            The matching family member row if found, otherwise None.
        """
        response = (
            self._client.table(self._TABLE)
            .select("*")
            .eq("family_id", family_id)
            .execute()
        )

        rows: list[dict[str, Any]] = response.data or []
        normalized_input = normalize_phone_number(phone_number)

        for row in rows:
            stored_phone = row.get("phone_number")
            if not isinstance(stored_phone, str):
                continue

            if stored_phone == phone_number:
                return row

            if normalize_phone_number(stored_phone) == normalized_input:
                return row

        return None
