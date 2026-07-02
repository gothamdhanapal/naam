"""
Ownership policy for the Context Decision Matrix.

Determines owner and responsible person using explicit hints first,
then scope-based defaults.

Ownership and responsibility are distinct:
- Owner — who the commitment belongs to
- Responsible — who is explicitly assigned to act

The speaker is never assumed responsible unless scope or input
provides explicit evidence.
"""

from __future__ import annotations

from app.context.models import DecisionInput, OwnershipDecision, ScopeDecision
from app.schemas.context import Scope


class OwnershipPolicy:
    """Determine ownership and responsibility for a conversation."""

    REASON_EXPLICIT = "OWNERSHIP_EXPLICIT"
    REASON_PERSONAL_SPEAKER = "OWNERSHIP_PERSONAL_SPEAKER"
    REASON_DEPENDENT_MEMBER = "OWNERSHIP_DEPENDENT_MEMBER"
    REASON_EXTERNAL_UNASSIGNED = "OWNERSHIP_EXTERNAL_UNASSIGNED"
    REASON_FAMILY_UNASSIGNED = "OWNERSHIP_FAMILY_UNASSIGNED"

    def evaluate(
        self,
        decision_input: DecisionInput,
        scope_decision: ScopeDecision,
    ) -> OwnershipDecision:
        """
        Evaluate ownership for the given input and scope.

        Priority:
            1. Explicit owner_id and/or responsible_id from understanding
            2. Scope-based owner defaults without inferring responsibility
        """
        understanding = decision_input.understanding
        speaker_id = decision_input.speaker.family_member_id

        if (
            understanding.owner_id is not None
            or understanding.responsible_id is not None
        ):
            return OwnershipDecision(
                owner_id=understanding.owner_id,
                responsible_person_id=understanding.responsible_id,
                confidence=1.0,
                reason_code=self.REASON_EXPLICIT,
            )

        if scope_decision.scope == Scope.PERSONAL:
            return OwnershipDecision(
                owner_id=speaker_id,
                responsible_person_id=speaker_id,
                confidence=0.9 if speaker_id else 0.5,
                reason_code=self.REASON_PERSONAL_SPEAKER,
            )

        if scope_decision.scope == Scope.DEPENDENT:
            return OwnershipDecision(
                owner_id=understanding.about_member_id,
                responsible_person_id=None,
                confidence=0.85 if understanding.about_member_id else 0.7,
                reason_code=self.REASON_DEPENDENT_MEMBER,
            )

        if scope_decision.scope == Scope.EXTERNAL:
            return OwnershipDecision(
                owner_id=None,
                responsible_person_id=None,
                confidence=0.75,
                reason_code=self.REASON_EXTERNAL_UNASSIGNED,
            )

        return OwnershipDecision(
            owner_id=None,
            responsible_person_id=None,
            confidence=0.8,
            reason_code=self.REASON_FAMILY_UNASSIGNED,
        )
