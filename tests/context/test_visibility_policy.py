"""Unit tests for VisibilityPolicy."""

from __future__ import annotations

from app.context.models import UnderstandingContext
from app.context.policies.visibility_policy import VisibilityPolicy
from app.schemas.context import Scope, Visibility
from tests.context.conftest import MEMBER_ID, build_input, ownership_decision, scope_decision


def test_personal_scope_is_owner_only(speaker) -> None:
    policy = VisibilityPolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="NOTE",
            title="Remind me to call the gym",
        ),
    )

    result = policy.evaluate(
        decision_input,
        scope_decision(Scope.PERSONAL, confidence=0.9),
        ownership_decision(owner_id=MEMBER_ID, responsible_person_id=MEMBER_ID, confidence=0.9),
    )

    assert result.visibility == Visibility.OWNER_ONLY
    assert result.reason_code == VisibilityPolicy.REASON_OWNER_ONLY


def test_family_scope_is_shared(speaker) -> None:
    policy = VisibilityPolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="TASK",
            title="Pay electricity bill",
            entities=["Home"],
        ),
    )

    result = policy.evaluate(
        decision_input,
        scope_decision(Scope.FAMILY, confidence=0.8),
        ownership_decision(owner_id=None, responsible_person_id=None, confidence=0.8),
    )

    assert result.visibility == Visibility.FAMILY
    assert result.reason_code == VisibilityPolicy.REASON_FAMILY


def test_sensitive_personal_content_is_private(speaker) -> None:
    policy = VisibilityPolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="NOTE",
            title="Schedule therapy session",
            entities=["Health"],
        ),
    )

    result = policy.evaluate(
        decision_input,
        scope_decision(Scope.PERSONAL, confidence=0.9),
        ownership_decision(owner_id=MEMBER_ID, responsible_person_id=MEMBER_ID, confidence=0.9),
    )

    assert result.visibility == Visibility.PRIVATE
    assert result.reason_code == VisibilityPolicy.REASON_SENSITIVE_PRIVATE
