"""Unit tests for OwnershipPolicy."""

from __future__ import annotations

from app.context.models import UnderstandingContext
from app.context.policies.ownership_policy import OwnershipPolicy
from app.schemas.context import Scope
from tests.context.conftest import (
    CHILD_MEMBER_ID,
    MEMBER_ID,
    OTHER_MEMBER_ID,
    build_input,
    scope_decision,
)


def test_explicit_ownership_uses_provided_ids(speaker) -> None:
    policy = OwnershipPolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="TASK",
            title="Pay school fees",
            owner_id=OTHER_MEMBER_ID,
            responsible_id=MEMBER_ID,
        ),
    )

    result = policy.evaluate(
        decision_input,
        scope_decision(Scope.FAMILY, confidence=1.0),
    )

    assert result.owner_id == OTHER_MEMBER_ID
    assert result.responsible_person_id == MEMBER_ID
    assert result.confidence == 1.0
    assert result.reason_code == OwnershipPolicy.REASON_EXPLICIT


def test_explicit_owner_does_not_infer_responsible_from_speaker(speaker) -> None:
    policy = OwnershipPolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="TASK",
            title="Pay school fees",
            owner_id=OTHER_MEMBER_ID,
        ),
    )

    result = policy.evaluate(
        decision_input,
        scope_decision(Scope.FAMILY, confidence=1.0),
    )

    assert result.owner_id == OTHER_MEMBER_ID
    assert result.responsible_person_id is None


def test_personal_scope_owner_and_responsible_are_the_speaker(speaker) -> None:
    """Owner = Person, Responsible = Person (explicit personal evidence)."""
    policy = OwnershipPolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="NOTE",
            title="Remind me to read",
        ),
    )

    result = policy.evaluate(
        decision_input,
        scope_decision(Scope.PERSONAL, confidence=0.9),
    )

    assert result.owner_id == MEMBER_ID
    assert result.responsible_person_id == MEMBER_ID
    assert result.reason_code == OwnershipPolicy.REASON_PERSONAL_SPEAKER


def test_family_owned_commitment_has_no_owner_or_responsible_person(speaker) -> None:
    """Owner = Family (None id), Responsible = None."""
    policy = OwnershipPolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="TASK",
            title="Pay electricity bill",
        ),
    )

    result = policy.evaluate(
        decision_input,
        scope_decision(Scope.FAMILY, confidence=0.8),
    )

    assert result.owner_id is None
    assert result.responsible_person_id is None
    assert result.confidence == 0.8
    assert result.reason_code == OwnershipPolicy.REASON_FAMILY_UNASSIGNED


def test_dependent_child_owner_has_no_responsible_person_without_evidence(
    speaker,
) -> None:
    """Owner = Child, Responsible = None unless explicitly provided."""
    policy = OwnershipPolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="TASK",
            title="Book vaccination",
            about_member_id=CHILD_MEMBER_ID,
        ),
    )

    result = policy.evaluate(
        decision_input,
        scope_decision(Scope.DEPENDENT, confidence=0.9),
    )

    assert result.owner_id == CHILD_MEMBER_ID
    assert result.responsible_person_id is None
    assert result.reason_code == OwnershipPolicy.REASON_DEPENDENT_MEMBER


def test_dependent_child_owner_with_explicit_parent_responsible(speaker) -> None:
    """Owner = Child, Responsible = Parent only when explicitly known."""
    policy = OwnershipPolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="TASK",
            title="Book vaccination",
            owner_id=CHILD_MEMBER_ID,
            responsible_id=MEMBER_ID,
        ),
    )

    result = policy.evaluate(
        decision_input,
        scope_decision(Scope.DEPENDENT, confidence=1.0),
    )

    assert result.owner_id == CHILD_MEMBER_ID
    assert result.responsible_person_id == MEMBER_ID


def test_external_scope_leaves_owner_and_responsible_unassigned(speaker) -> None:
    policy = OwnershipPolicy()
    decision_input = build_input(
        speaker,
        UnderstandingContext(
            type="TASK",
            title="Follow up with utility",
            entities=["Electricity Board"],
        ),
    )

    result = policy.evaluate(
        decision_input,
        scope_decision(Scope.EXTERNAL, confidence=0.9),
    )

    assert result.owner_id is None
    assert result.responsible_person_id is None
    assert result.reason_code == OwnershipPolicy.REASON_EXTERNAL_UNASSIGNED
