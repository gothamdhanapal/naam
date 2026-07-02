"""
Follow-up policy for the Context Decision Matrix.

Determines whether Naam should remind, wait, watch, or escalate.
"""

from __future__ import annotations

from app.context.models import (
    DecisionInput,
    FollowUpDecision,
    OwnershipDecision,
    ScopeDecision,
)
from app.schemas.context import FollowUpAction, Scope


class FollowUpPolicy:
    """Determine recommended follow-up behaviour."""

    _ESCALATION_MARKERS = ("urgent", "asap", "overdue", "immediately")
    _QUESTION_MARKERS = ("?", "should we", "can you", "what do you think")

    def evaluate(
        self,
        decision_input: DecisionInput,
        scope_decision: ScopeDecision,
        _ownership_decision: OwnershipDecision,
    ) -> FollowUpDecision:
        """
        Evaluate follow-up action from scope, urgency, and message shape.

        Rules:
            - Escalation language -> ESCALATE
            - Questions or low understanding confidence -> WAIT_RESPONSE
            - Personal reminders with due dates -> REMIND_OWNER
            - External entities -> WATCH
            - Otherwise -> NONE
        """
        understanding = decision_input.understanding
        title = understanding.title.strip().lower()

        if any(marker in title for marker in self._ESCALATION_MARKERS):
            return FollowUpDecision(action=FollowUpAction.ESCALATE, confidence=0.95)

        if self._looks_like_question(title) or understanding.confidence < 0.6:
            return FollowUpDecision(action=FollowUpAction.WAIT_RESPONSE, confidence=0.85)

        if (
            scope_decision.scope == Scope.PERSONAL
            and (
                understanding.due_date is not None
                or "remind" in title
            )
        ):
            return FollowUpDecision(action=FollowUpAction.REMIND_OWNER, confidence=0.9)

        if scope_decision.scope == Scope.EXTERNAL:
            return FollowUpDecision(action=FollowUpAction.WATCH, confidence=0.8)

        return FollowUpDecision(action=FollowUpAction.NONE, confidence=0.75)

    def _looks_like_question(self, title: str) -> bool:
        if title.endswith("?"):
            return True
        return any(marker in title for marker in self._QUESTION_MARKERS)
