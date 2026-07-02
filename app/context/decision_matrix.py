"""
Context Decision Matrix for Naam.

Orchestrates deterministic context policies to produce a full
ContextDecision without AI inference or database access.
"""

from __future__ import annotations

from app.context.models import ContextDecision, DecisionInput
from app.context.policies.followup_policy import FollowUpPolicy
from app.context.policies.ownership_policy import OwnershipPolicy
from app.context.policies.participant_policy import ParticipantPolicy
from app.context.policies.scope_policy import ScopePolicy
from app.context.policies.visibility_policy import VisibilityPolicy


class ContextDecisionMatrix:
    """
    Deterministic reasoning engine for context decisions.

    Composes scope, ownership, participant, visibility, and follow-up
    policies. The future Context Agent will call this matrix and map
    the result into a ContextResult.
    """

    def __init__(
        self,
        scope_policy: ScopePolicy | None = None,
        ownership_policy: OwnershipPolicy | None = None,
        participant_policy: ParticipantPolicy | None = None,
        visibility_policy: VisibilityPolicy | None = None,
        follow_up_policy: FollowUpPolicy | None = None,
    ) -> None:
        """
        Initialize the matrix with injectable policy components.

        Args:
            scope_policy: Determines conversation scope.
            ownership_policy: Determines owner and responsible person.
            participant_policy: Determines participants and interested members.
            visibility_policy: Determines visibility recommendation.
            follow_up_policy: Determines follow-up action.
        """
        self._scope_policy = scope_policy or ScopePolicy()
        self._ownership_policy = ownership_policy or OwnershipPolicy()
        self._participant_policy = participant_policy or ParticipantPolicy()
        self._visibility_policy = visibility_policy or VisibilityPolicy()
        self._follow_up_policy = follow_up_policy or FollowUpPolicy()

    def evaluate(self, decision_input: DecisionInput) -> ContextDecision:
        """
        Run all context policies and return a combined decision.

        Args:
            decision_input: Speaker identity, understanding, and family refs.

        Returns:
            Full deterministic context decision.
        """
        scope_decision = self._scope_policy.evaluate(decision_input)
        ownership_decision = self._ownership_policy.evaluate(
            decision_input,
            scope_decision,
        )
        participant_decision = self._participant_policy.evaluate(
            decision_input,
            scope_decision,
            ownership_decision,
        )
        visibility_decision = self._visibility_policy.evaluate(
            decision_input,
            scope_decision,
            ownership_decision,
        )
        follow_up_decision = self._follow_up_policy.evaluate(
            decision_input,
            scope_decision,
            ownership_decision,
        )

        return ContextDecision(
            scope=scope_decision,
            ownership=ownership_decision,
            participants=participant_decision,
            visibility=visibility_decision,
            follow_up=follow_up_decision,
        )
