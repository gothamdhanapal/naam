"""Unit tests for the Planning Agent."""

from __future__ import annotations

import pytest

from app.agents.planning_agent import PlanningAgent
from app.execution.models import ActionType
from tests.conftest import FAMILY_ID, INBOX_ID


@pytest.fixture
def planning_agent() -> PlanningAgent:
    return PlanningAgent()


@pytest.mark.asyncio
async def test_maps_task_understanding_into_create_task(
    planning_agent: PlanningAgent,
) -> None:
    plan = await planning_agent.plan(
        {
            "type": "TASK",
            "title": "Pay electricity bill",
            "family_id": str(FAMILY_ID),
            "due_date": "2026-06-29",
            "confidence": 0.95,
        }
    )

    assert len(plan.actions) == 1
    action = plan.actions[0]
    assert action.type == ActionType.CREATE_TASK
    assert action.payload["family_id"] == str(FAMILY_ID)
    assert action.payload["title"] == "Pay electricity bill"
    assert action.payload["due_date"] == "2026-06-29"
    assert "confidence" not in action.payload


@pytest.mark.asyncio
async def test_returns_empty_plan_for_incomplete_understanding(
    planning_agent: PlanningAgent,
) -> None:
    plan = await planning_agent.plan(
        {
            "type": "TASK",
            "title": "Pay electricity bill",
            "confidence": 0.95,
        }
    )

    assert plan.actions == []


@pytest.mark.asyncio
async def test_ignores_unsupported_understanding_types(
    planning_agent: PlanningAgent,
) -> None:
    plan = await planning_agent.plan(
        {
            "type": "EVENT",
            "title": "Parent teacher meeting",
            "family_id": str(FAMILY_ID),
            "confidence": 0.9,
        }
    )

    assert plan.actions == []


@pytest.mark.asyncio
async def test_maps_create_task_intent(
    planning_agent: PlanningAgent,
) -> None:
    plan = await planning_agent.plan(
        {
            "intent": "create_task",
            "title": "Water plants",
            "family_id": str(FAMILY_ID),
            "inbox_item_id": str(INBOX_ID),
        }
    )

    assert len(plan.actions) == 1
    assert plan.actions[0].type == ActionType.CREATE_TASK
    assert plan.actions[0].payload["inbox_item_id"] == str(INBOX_ID)
