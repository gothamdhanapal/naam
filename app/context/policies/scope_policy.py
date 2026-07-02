"""
Scope policy for the Context Decision Matrix.

Determines whether a conversation belongs to a personal, family,
dependent, or external scope using deterministic rules only.
"""

from __future__ import annotations

from app.context.models import DecisionInput, ScopeDecision, UnderstandingContext
from app.schemas.context import Scope


def _entities_contain_markers(entities: list[str], markers: tuple[str, ...]) -> bool:
    """Return True when any entity text contains a marker phrase."""
    normalized_entities = [entity.strip().lower() for entity in entities]
    return any(
        marker in entity
        for entity in normalized_entities
        for marker in markers
    )


class ScopePolicy:
    """Determine conversation scope from identity and understanding."""

    REASON_EXPLICIT_HINT = "SCOPE_EXPLICIT_HINT"
    REASON_DEPENDENT_SIGNAL = "SCOPE_DEPENDENT_SIGNAL"
    REASON_EXTERNAL_ENTITY = "SCOPE_EXTERNAL_ENTITY"
    REASON_PERSONAL_LANGUAGE = "SCOPE_PERSONAL_LANGUAGE"
    REASON_FAMILY_DEFAULT = "SCOPE_FAMILY_DEFAULT"
    REASON_FAMILY_FALLBACK = "SCOPE_FAMILY_FALLBACK"

    _PERSONAL_TITLE_MARKERS = (
        "remind me",
        "my ",
        "for me",
        "i need to",
    )
    _DEPENDENT_ENTITY_MARKERS = (
        "daughter",
        "son",
        "child",
        "kid",
        "pet",
        "bruno",
        "dependent",
        "elderly",
    )
    _EXTERNAL_ENTITY_MARKERS = (
        "electricity board",
        "utility",
        "vendor",
        "external",
        "school office",
        "insurance",
        "bank",
    )
    _ACTIONABLE_TYPES = frozenset({"TASK", "EVENT", "NOTE"})
    _PERSONAL_ENTITIES = frozenset({"gym", "work", "career", "reading"})

    def evaluate(self, decision_input: DecisionInput) -> ScopeDecision:
        """
        Evaluate scope for the given decision input.

        Priority:
            1. Explicit scope hint
            2. Dependent signals (entity or about_member)
            3. External entity signals
            4. Personal language markers
            5. Default to FAMILY for actionable types
        """
        understanding = decision_input.understanding

        if understanding.scope_hint is not None:
            return ScopeDecision(
                scope=understanding.scope_hint,
                confidence=1.0,
                reason_code=self.REASON_EXPLICIT_HINT,
            )

        if self._has_dependent_signal(understanding):
            return ScopeDecision(
                scope=Scope.DEPENDENT,
                confidence=0.9,
                reason_code=self.REASON_DEPENDENT_SIGNAL,
            )

        if _entities_contain_markers(
            understanding.entities,
            self._EXTERNAL_ENTITY_MARKERS,
        ):
            return ScopeDecision(
                scope=Scope.EXTERNAL,
                confidence=0.9,
                reason_code=self.REASON_EXTERNAL_ENTITY,
            )

        if self._is_personal_conversation(understanding):
            return ScopeDecision(
                scope=Scope.PERSONAL,
                confidence=0.85,
                reason_code=self.REASON_PERSONAL_LANGUAGE,
            )

        if understanding.type.strip().upper() in self._ACTIONABLE_TYPES:
            return ScopeDecision(
                scope=Scope.FAMILY,
                confidence=0.8,
                reason_code=self.REASON_FAMILY_DEFAULT,
            )

        return ScopeDecision(
            scope=Scope.FAMILY,
            confidence=0.7,
            reason_code=self.REASON_FAMILY_FALLBACK,
        )

    def _has_dependent_signal(self, understanding: UnderstandingContext) -> bool:
        if understanding.about_member_id is not None:
            return True

        return _entities_contain_markers(
            understanding.entities,
            self._DEPENDENT_ENTITY_MARKERS,
        )

    def _is_personal_conversation(self, understanding: UnderstandingContext) -> bool:
        title = understanding.title.strip().lower()

        if any(marker in title for marker in self._PERSONAL_TITLE_MARKERS):
            return True

        normalized_entities = {
            entity.strip().lower() for entity in understanding.entities
        }
        if normalized_entities & self._PERSONAL_ENTITIES:
            return True

        if understanding.type.strip().upper() == "NOTE" and not understanding.entities:
            return True

        return False
