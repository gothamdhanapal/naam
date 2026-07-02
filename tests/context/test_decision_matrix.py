"""Integration tests for ContextDecisionMatrix."""

from __future__ import annotations

from app.context.decision_matrix import ContextDecisionMatrix
from app.context.models import UnderstandingContext
from app.context.policies.followup_policy import FollowUpPolicy
from app.context.policies.ownership_policy import OwnershipPolicy
from app.context.policies.participant_policy import ParticipantPolicy
from app.context.policies.scope_policy import ScopePolicy
from app.context.policies.visibility_policy import VisibilityPolicy
from app.schemas.context import FollowUpAction, Relationship, Scope, Visibility
from tests.context.conftest import (
    CHILD_MEMBER_ID,
    MEMBER_ID,
    OTHER_MEMBER_ID,
    build_input,
    scope_decision,
)


def test_personal_reminder_scenario(speaker) -> None:
    matrix = ContextDecisionMatrix()
    decision = matrix.evaluate(
        build_input(
            speaker,
            UnderstandingContext(
                type="NOTE",
                title="Remind me to call the gym tomorrow",
                due_date="tomorrow",
            ),
        )
    )

    assert decision.scope.scope == Scope.PERSONAL
    assert decision.ownership.owner_id == MEMBER_ID
    assert decision.visibility.visibility == Visibility.OWNER_ONLY
    assert decision.follow_up.action == FollowUpAction.REMIND_OWNER
    assert decision.reason_codes == [
        ScopePolicy.REASON_PERSONAL_LANGUAGE,
        OwnershipPolicy.REASON_PERSONAL_SPEAKER,
        ParticipantPolicy.REASON_ASSIGNED,
        VisibilityPolicy.REASON_OWNER_ONLY,
        FollowUpPolicy.REASON_REMIND_OWNER,
    ]


def test_family_task_scenario(speaker, family_members) -> None:
    matrix = ContextDecisionMatrix()
    decision = matrix.evaluate(
        build_input(
            speaker,
            UnderstandingContext(
                type="TASK",
                title="Pay electricity bill",
                entities=["Home", "Electricity"],
            ),
            family_members=family_members,
        )
    )

    assert decision.scope.scope == Scope.FAMILY
    assert decision.ownership.owner_id is None
    assert decision.ownership.responsible_person_id is None
    assert decision.visibility.visibility == Visibility.FAMILY
    assert OTHER_MEMBER_ID in decision.participants.interested_member_ids
    assert decision.follow_up.action == FollowUpAction.NONE
    assert ScopePolicy.REASON_FAMILY_DEFAULT in decision.reason_codes
    assert OwnershipPolicy.REASON_FAMILY_UNASSIGNED in decision.reason_codes


def test_dependent_task_scenario(speaker, family_members) -> None:
    matrix = ContextDecisionMatrix()
    decision = matrix.evaluate(
        build_input(
            speaker,
            UnderstandingContext(
                type="TASK",
                title="Pick up Anya from dance class",
                entities=["Daughter", "Dance School"],
                about_member_id=CHILD_MEMBER_ID,
            ),
            family_members=family_members,
        )
    )

    assert decision.scope.scope == Scope.DEPENDENT
    assert decision.ownership.owner_id == CHILD_MEMBER_ID
    relationships = {
        participant.family_member_id: participant.relationship
        for participant in decision.participants.participants
    }
    assert relationships[MEMBER_ID] == Relationship.CAREGIVER
    assert decision.visibility.visibility == Visibility.FAMILY
    assert ParticipantPolicy.REASON_DEPENDENT_CAREGIVER in decision.reason_codes


def test_external_entity_scenario(speaker, family_members) -> None:
    matrix = ContextDecisionMatrix()
    decision = matrix.evaluate(
        build_input(
            speaker,
            UnderstandingContext(
                type="TASK",
                title="Pay utility bill",
                entities=["Electricity Board"],
            ),
            family_members=family_members,
        )
    )

    assert decision.scope.scope == Scope.EXTERNAL
    assert decision.follow_up.action == FollowUpAction.WATCH
    assert decision.visibility.visibility == Visibility.FAMILY
    assert ScopePolicy.REASON_EXTERNAL_ENTITY in decision.reason_codes
    assert FollowUpPolicy.REASON_WATCH in decision.reason_codes


def test_explicit_ownership_scenario(speaker, family_members) -> None:
    matrix = ContextDecisionMatrix()
    decision = matrix.evaluate(
        build_input(
            speaker,
            UnderstandingContext(
                type="TASK",
                title="Pay school fees",
                owner_id=OTHER_MEMBER_ID,
                responsible_id=MEMBER_ID,
            ),
            family_members=family_members,
        )
    )

    assert decision.ownership.owner_id == OTHER_MEMBER_ID
    assert decision.ownership.responsible_person_id == MEMBER_ID
    assert decision.ownership.confidence == 1.0
    assert OwnershipPolicy.REASON_EXPLICIT in decision.reason_codes


def test_shared_visibility_for_family_work(speaker, family_members) -> None:
    matrix = ContextDecisionMatrix()
    decision = matrix.evaluate(
        build_input(
            speaker,
            UnderstandingContext(
                type="TASK",
                title="Buy groceries",
            ),
            family_members=family_members,
        )
    )

    assert decision.visibility.visibility == Visibility.FAMILY


def test_wait_response_follow_up_for_question(speaker) -> None:
    matrix = ContextDecisionMatrix()
    decision = matrix.evaluate(
        build_input(
            speaker,
            UnderstandingContext(
                type="NOTE",
                title="Can you handle the plumber visit?",
            ),
        )
    )

    assert decision.follow_up.action == FollowUpAction.WAIT_RESPONSE
    assert FollowUpPolicy.REASON_WAIT_RESPONSE in decision.reason_codes


def test_matrix_supports_policy_injection(speaker) -> None:
    class FixedScopePolicy:
        def evaluate(self, decision_input):
            return scope_decision(Scope.PERSONAL, confidence=1.0)

    matrix = ContextDecisionMatrix(scope_policy=FixedScopePolicy())
    decision = matrix.evaluate(
        build_input(
            speaker,
            UnderstandingContext(
                type="TASK",
                title="Pay electricity bill",
            ),
        )
    )

    assert decision.scope.scope == Scope.PERSONAL
    assert len(decision.reason_codes) == 5
