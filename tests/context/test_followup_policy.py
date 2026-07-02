"""Unit tests for FollowUpPolicy."""

from __future__ import annotations

from app.context.models import UnderstandingContext
from app.context.policies.followup_policy import FollowUpPolicy
from app.schemas.context import FollowUpAction, Scope
from tests.context.conftest import MEMBER_ID, build_input, ownership_decision, scope_decision


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
        scope_decision(Scope.PERSONAL, confidence=0.9),
        ownership_decision(owner_id=MEMBER_ID, responsible_person_id=MEMBER_ID, confidence=0.9),
    )

    assert result.action == FollowUpAction.REMIND_OWNER
    assert result.reason_code == FollowUpPolicy.REASON_REMIND_OWNER


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
        scope_decision(Scope.FAMILY, confidence=0.8),
        ownership_decision(owner_id=None, responsible_person_id=MEMBER_ID, confidence=0.8),
    )

    assert result.action == FollowUpAction.WAIT_RESPONSE
    assert result.reason_code == FollowUpPolicy.REASON_WAIT_RESPONSE


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
        scope_decision(Scope.EXTERNAL, confidence=0.9),
        ownership_decision(owner_id=None, responsible_person_id=MEMBER_ID, confidence=0.75),
    )

    assert result.action == FollowUpAction.WATCH
    assert result.reason_code == FollowUpPolicy.REASON_WATCH


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
        scope_decision(Scope.FAMILY, confidence=0.8),
        ownership_decision(owner_id=None, responsible_person_id=MEMBER_ID, confidence=0.8),
    )

    assert result.action == FollowUpAction.ESCALATE
    assert result.reason_code == FollowUpPolicy.REASON_ESCALATION
