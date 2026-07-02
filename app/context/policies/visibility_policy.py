"""
Visibility policy for the Context Decision Matrix.

Determines who may see information derived from a conversation.
"""

from __future__ import annotations

from app.context.models import (
    DecisionInput,
    OwnershipDecision,
    ScopeDecision,
    VisibilityDecision,
)
from app.schemas.context import Scope, Visibility


class VisibilityPolicy:
    """Determine visibility for derived context."""

    REASON_SENSITIVE_PRIVATE = "VISIBILITY_SENSITIVE_PRIVATE"
    REASON_OWNER_ONLY = "VISIBILITY_OWNER_ONLY"
    REASON_FAMILY = "VISIBILITY_FAMILY"

    _PRIVATE_ENTITY_MARKERS = (
        "health",
        "medical",
        "therapy",
        "salary",
        "finance",
        "password",
    )

    def evaluate(
        self,
        decision_input: DecisionInput,
        scope_decision: ScopeDecision,
        _ownership_decision: OwnershipDecision,
    ) -> VisibilityDecision:
        """
        Evaluate visibility from scope, ownership, and content signals.

        Rules:
            - Sensitive personal content -> PRIVATE
            - Personal scope -> OWNER_ONLY
            - Family, dependent, external shared work -> FAMILY visibility
        """
        if self._is_sensitive_personal_content(decision_input):
            return VisibilityDecision(
                visibility=Visibility.PRIVATE,
                reason_code=self.REASON_SENSITIVE_PRIVATE,
            )

        if scope_decision.scope == Scope.PERSONAL:
            return VisibilityDecision(
                visibility=Visibility.OWNER_ONLY,
                reason_code=self.REASON_OWNER_ONLY,
            )

        return VisibilityDecision(
            visibility=Visibility.FAMILY,
            reason_code=self.REASON_FAMILY,
        )

    def _is_sensitive_personal_content(self, decision_input: DecisionInput) -> bool:
        understanding = decision_input.understanding
        searchable_text = " ".join(
            [
                understanding.title.lower(),
                *[entity.lower() for entity in understanding.entities],
            ]
        )
        return any(marker in searchable_text for marker in self._PRIVATE_ENTITY_MARKERS)
