"""
Context Agent for Naam.

Transforms conversational understanding into organizational understanding
by orchestrating the Context Decision Matrix.
"""

from __future__ import annotations

from app.agents.context.adapters import adapt_understanding, build_decision_input
from app.agents.context.mapping import map_context_result
from app.context.decision_matrix import ContextDecisionMatrix
from app.schemas.context import ContextResult
from app.schemas.context_request import ContextRequest


class ContextAgent:
    """
    Produce ContextResult from identity and understanding inputs.

    Orchestrates validation, adaptation, matrix evaluation, and mapping.
    Contains no organizational business rules.
    """

    def __init__(
        self,
        decision_matrix: ContextDecisionMatrix | None = None,
    ) -> None:
        """
        Initialize the Context Agent.

        Args:
            decision_matrix: Deterministic context decision engine.
                Defaults to ContextDecisionMatrix when not provided.
        """
        self._decision_matrix = decision_matrix or ContextDecisionMatrix()

    def build(self, request: ContextRequest) -> ContextResult:
        """
        Build organizational context for a conversation.

        Args:
            request: Identity, understanding, and optional family context.

        Returns:
            Immutable ContextResult for downstream planning.
        """
        decision_input = build_decision_input(request)
        decision = self._decision_matrix.evaluate(decision_input)
        understanding = adapt_understanding(request.understanding, request.metadata)

        return map_context_result(
            request=request,
            decision=decision,
            related_entities=list(understanding.entities),
        )
