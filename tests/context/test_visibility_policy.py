"""Unit tests for VisibilityPolicy."""

from __future__ import annotations

from app.context.models import OwnershipDecision, ScopeDecision, UnderstandingContext
from app.context.policies.visibility_policy import VisibilityPolicy
from app.schemas.context import Scope, Visibility
from tests.context.conftest import MEMBER_ID, build_input


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
        ScopeDecision(scope=Scope.PERSONAL, confidence=0.9),
        OwnershipDecision(owner_id=MEMBER_ID, responsible_person_id=MEMBER_ID, confidence=0.9),
    )

    assert result.visibility == Visibility.OWNER_ONLY


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
        ScopeDecision(scope=Scope.FAMILY, confidence=0.8),
        OwnershipDecision(owner_id=None, responsible_person_id=None, confidence=0.8),
    )

    assert result.visibility == Visibility.FAMILY


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
        ScopeDecision(scope=Scope.PERSONAL, confidence=0.9),
        OwnershipDecision(owner_id=MEMBER_ID, responsible_person_id=MEMBER_ID, confidence=0.9),
    )

    assert result.visibility == Visibility.PRIVATE
