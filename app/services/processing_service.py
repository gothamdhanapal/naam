"""
Inbox processing orchestration.

Coordinates the Understanding Agent, Planning Agent, and Execution Engine
without bypassing any layer or accessing Supabase directly.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from app.agents.planning_agent import PlanningAgent
from app.agents.understanding_agent import understand_message
from app.execution.bootstrap import create_execution_engine
from app.execution.models import ActionResult
from app.repositories.inbox_repository import update_ai_result


def _enrich_for_planning(
    understanding: dict[str, Any],
    family_id: str,
    inbox_id: str,
) -> dict[str, Any]:
    """
    Add inbox context required by the Planning Agent.

    Non-ISO due dates from the Understanding Agent are omitted so task
    creation can proceed with the remaining valid fields.
    """
    planning_input = {
        **understanding,
        "family_id": family_id,
        "inbox_item_id": inbox_id,
    }

    due_date = planning_input.get("due_date")
    if due_date is not None and not _is_iso_date(due_date):
        planning_input.pop("due_date")

    return planning_input


def _is_iso_date(value: Any) -> bool:
    """Return True when value is a YYYY-MM-DD date string."""
    if not isinstance(value, str):
        return False

    try:
        date.fromisoformat(value)
    except ValueError:
        return False

    return True


async def process_inbox_item(
    inbox_id: str,
    family_id: str,
    content: str,
) -> dict[str, Any]:
    """
    Run the full inbox processing pipeline for a persisted inbox item.

    Workflow:
        1. Invoke the Understanding Agent.
        2. Enrich understanding with inbox context.
        3. Generate an ExecutionPlan via the Planning Agent.
        4. Execute the plan via the bootstrap ExecutionEngine.
        5. Persist understanding output on the inbox item.

    Args:
        inbox_id: Primary key of the persisted inbox item.
        family_id: Family that owns the inbox item.
        content: Raw inbox message content.

    Returns:
        Dictionary containing understanding output, execution plan, and
        execution results.
    """
    understanding_result = understand_message(content)
    understanding = understanding_result.model_dump()

    planning_input = _enrich_for_planning(
        understanding=understanding,
        family_id=family_id,
        inbox_id=inbox_id,
    )

    planning_agent = PlanningAgent()
    execution_plan = await planning_agent.plan(planning_input)

    engine = create_execution_engine()
    execution_results = await engine.execute(execution_plan)

    update_ai_result(inbox_id, understanding)

    return {
        "understanding": understanding,
        "execution_plan": execution_plan.model_dump(mode="json"),
        "execution_results": [
            _serialize_action_result(result)
            for result in execution_results
        ],
    }


def _serialize_action_result(result: ActionResult) -> dict[str, Any]:
    """Convert an ActionResult into a JSON-serializable dictionary."""
    return result.model_dump(mode="json")
