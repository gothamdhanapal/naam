"""
Participant policy for the Context Decision Matrix.

Determines who participates in a conversation and who is interested
based on scope and ownership decisions.
"""

from __future__ import annotations

from uuid import UUID

from app.context.models import (
    DecisionInput,
    OwnershipDecision,
    ParticipantDecision,
    ScopeDecision,
)
from app.schemas.context import ContextParticipant, Relationship, Scope


class ParticipantPolicy:
    """Determine participants and interested members."""

    REASON_DEPENDENT_CAREGIVER = "PARTICIPANTS_DEPENDENT_CAREGIVER"
    REASON_SHARED_INTEREST = "PARTICIPANTS_SHARED_INTEREST"
    REASON_ASSIGNED = "PARTICIPANTS_ASSIGNED"

    _PARENT_ROLES = frozenset({"parent", "guardian", "caregiver"})
    _RELATIONSHIP_PRIORITY = {
        Relationship.OWNER: 4,
        Relationship.CAREGIVER: 3,
        Relationship.RESPONSIBLE: 2,
        Relationship.PARTICIPANT: 1,
    }

    def evaluate(
        self,
        decision_input: DecisionInput,
        scope_decision: ScopeDecision,
        ownership_decision: OwnershipDecision,
    ) -> ParticipantDecision:
        """
        Build participant and interest lists from scope and ownership.

        The speaker is always included. Owner and responsible person receive
        explicit relationships. Other family members may be marked interested
        for shared family scope.
        """
        relationships: dict[UUID, Relationship] = {}

        self._register(
            relationships,
            decision_input.speaker.family_member_id,
            Relationship.PARTICIPANT,
        )
        self._register(
            relationships,
            ownership_decision.owner_id,
            Relationship.OWNER,
        )
        self._register(
            relationships,
            ownership_decision.responsible_person_id,
            Relationship.RESPONSIBLE,
        )
        self._register(
            relationships,
            decision_input.understanding.about_member_id,
            Relationship.PARTICIPANT,
        )

        is_dependent_scope = scope_decision.scope == Scope.DEPENDENT
        if is_dependent_scope:
            self._register(
                relationships,
                decision_input.speaker.family_member_id,
                Relationship.CAREGIVER,
            )

        participants = [
            ContextParticipant(
                family_member_id=member_id,
                relationship=relationship,
            )
            for member_id, relationship in relationships.items()
        ]

        interested_member_ids: list[UUID] = []
        if scope_decision.scope in {Scope.FAMILY, Scope.DEPENDENT, Scope.EXTERNAL}:
            interested_member_ids = self._collect_interested_members(
                decision_input=decision_input,
                participant_ids=set(relationships.keys()),
            )

        if is_dependent_scope:
            reason_code = self.REASON_DEPENDENT_CAREGIVER
        elif interested_member_ids:
            reason_code = self.REASON_SHARED_INTEREST
        else:
            reason_code = self.REASON_ASSIGNED

        return ParticipantDecision(
            participants=participants,
            interested_member_ids=interested_member_ids,
            reason_code=reason_code,
        )

    def _register(
        self,
        relationships: dict[UUID, Relationship],
        member_id: UUID | None,
        relationship: Relationship,
    ) -> None:
        if member_id is None:
            return

        current = relationships.get(member_id)
        if current is None:
            relationships[member_id] = relationship
            return

        if (
            self._RELATIONSHIP_PRIORITY[relationship]
            > self._RELATIONSHIP_PRIORITY[current]
        ):
            relationships[member_id] = relationship

    def _collect_interested_members(
        self,
        decision_input: DecisionInput,
        participant_ids: set[UUID],
    ) -> list[UUID]:
        interested: list[UUID] = []

        for member in decision_input.family_members:
            if member.family_member_id in participant_ids:
                continue

            role = (member.role or "").strip().lower()
            if role in self._PARENT_ROLES:
                interested.append(member.family_member_id)

        return interested
