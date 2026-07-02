"""Unit tests for ScopePolicy."""

from __future__ import annotations

from app.context.models import UnderstandingContext
from app.context.policies.scope_policy import ScopePolicy
from app.schemas.context import Scope
from tests.context.conftest import (
    CHILD_MEMBER_ID,
    build_input,
)


def test_explicit_scope_hint_wins(speaker) -> None:
    policy = ScopePolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="TASK",
            title="Pay electricity bill",
            scope_hint=Scope.FAMILY,
        ),
    )

    result = policy.evaluate(decision_input)

    assert result.scope == Scope.FAMILY
    assert result.confidence == 1.0


def test_personal_reminder_detected(speaker) -> None:
    policy = ScopePolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="NOTE",
            title="Remind me to call the gym after lunch",
        ),
    )

    result = policy.evaluate(decision_input)

    assert result.scope == Scope.PERSONAL


def test_family_task_is_default_for_household_work(speaker) -> None:
    policy = ScopePolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="TASK",
            title="Pay electricity bill",
            entities=["Home", "Electricity"],
        ),
    )

    result = policy.evaluate(decision_input)

    assert result.scope == Scope.FAMILY


def test_dependent_task_detected_from_entity(speaker) -> None:
    policy = ScopePolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="TASK",
            title="Pick up from dance class",
            entities=["Daughter", "Dance School"],
        ),
    )

    result = policy.evaluate(decision_input)

    assert result.scope == Scope.DEPENDENT


def test_dependent_task_detected_from_about_member(speaker) -> None:
    policy = ScopePolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="TASK",
            title="Book vaccination",
            about_member_id=CHILD_MEMBER_ID,
        ),
    )

    result = policy.evaluate(decision_input)

    assert result.scope == Scope.DEPENDENT


def test_external_entity_detected(speaker) -> None:
    policy = ScopePolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="TASK",
            title="Pay bill",
            entities=["Electricity Board"],
        ),
    )

    result = policy.evaluate(decision_input)

    assert result.scope == Scope.EXTERNAL
