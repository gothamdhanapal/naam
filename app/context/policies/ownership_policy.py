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
            )

        if scope_decision.scope == Scope.PERSONAL:
            return OwnershipDecision(
                owner_id=speaker_id,
                responsible_person_id=speaker_id,
                confidence=0.9 if speaker_id else 0.5,
            )

        if scope_decision.scope == Scope.DEPENDENT:
            return OwnershipDecision(
                owner_id=understanding.about_member_id,
                responsible_person_id=None,
                confidence=0.85 if understanding.about_member_id else 0.7,
            )

        if scope_decision.scope == Scope.EXTERNAL:
            return OwnershipDecision(
                owner_id=None,
                responsible_person_id=None,
                confidence=0.75,
            )

        return OwnershipDecision(
            owner_id=None,
            responsible_person_id=None,
            confidence=0.8,
        )
