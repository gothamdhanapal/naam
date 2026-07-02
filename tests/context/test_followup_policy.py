"""Unit tests for FollowUpPolicy."""

from __future__ import annotations

from app.context.models import OwnershipDecision, ScopeDecision, UnderstandingContext
from app.context.policies.followup_policy import FollowUpPolicy
from app.schemas.context import FollowUpAction, Scope
from tests.context.conftest import MEMBER_ID, build_input


def test_personal_reminder_requests_owner_reminder(speaker) -> None:
    policy = FollowUpPolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="NOTE",
            title="Remind me to pay the credit card",
            due_date="tomorrow",
        ),
    )

    result = policy.evaluate(
        decision_input,
        ScopeDecision(scope=Scope.PERSONAL, confidence=0.9),
        OwnershipDecision(owner_id=MEMBER_ID, responsible_person_id=MEMBER_ID, confidence=0.9),
    )

    assert result.action == FollowUpAction.REMIND_OWNER


def test_question_triggers_wait_response(speaker) -> None:
    policy = FollowUpPolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="NOTE",
            title="Should we book the vacation this week?",
            confidence=0.95,
        ),
    )

    result = policy.evaluate(
        decision_input,
        ScopeDecision(scope=Scope.FAMILY, confidence=0.8),
        OwnershipDecision(owner_id=None, responsible_person_id=MEMBER_ID, confidence=0.8),
    )

    assert result.action == FollowUpAction.WAIT_RESPONSE


def test_external_scope_is_watched(speaker) -> None:
    policy = FollowUpPolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="TASK",
            title="Follow up with utility company",
            entities=["Electricity Board"],
        ),
    )

    result = policy.evaluate(
        decision_input,
        ScopeDecision(scope=Scope.EXTERNAL, confidence=0.9),
        OwnershipDecision(owner_id=None, responsible_person_id=MEMBER_ID, confidence=0.75),
    )

    assert result.action == FollowUpAction.WATCH


def test_urgent_language_escalates(speaker) -> None:
    policy = FollowUpPolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="TASK",
            title="Pay electricity bill urgently",
        ),
    )

    result = policy.evaluate(
        decision_input,
        ScopeDecision(scope=Scope.FAMILY, confidence=0.8),
        OwnershipDecision(owner_id=None, responsible_person_id=MEMBER_ID, confidence=0.8),
    )

    assert result.action == FollowUpAction.ESCALATE
