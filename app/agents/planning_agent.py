"""
Planning Agent for Naam.

Converts structured understanding output from the Understanding Agent
into an ExecutionPlan for the Execution Engine.

The Planning Agent performs pure transformation only. It does not access
the database, call repositories or services, or execute actions.
"""

from __future__ import annotations

from typing import Any

from app.execution.models import ActionType, ExecutionAction, ExecutionPlan


class PlanningAgent:
    """
    Maps AI understanding into deterministic execution plans.

    Each supported intent or understanding type is converted into one or
    more ExecutionAction objects. Unsupported or incomplete input yields
    an empty plan rather than raising an error.
    """

    _CREATE_TASK_INTENTS = frozenset({"create_task"})
    _CREATE_TASK_TYPES = frozenset({"TASK"})

    _TASK_PAYLOAD_FIELDS = (
        "family_id",
        "title",
        "description",
        "due_date",
        "priority",
        "status",
        "assigned_member_id",
        "inbox_item_id",
    )

    async def plan(self, understanding: dict[str, Any]) -> ExecutionPlan:
        """
        Convert structured understanding into an ExecutionPlan.

        Args:
            understanding: Structured output from the Understanding Agent
                or an upstream enrichment step. Supported shapes include
                explicit intents (``intent: create_task``) and classified
                types (``type: TASK``).

        Returns:
            ExecutionPlan containing zero or more executable actions.
        """
        actions: list[ExecutionAction] = []

        create_task_action = self._build_create_task_action(understanding)
        if create_task_action is not None:
            actions.append(create_task_action)

        return ExecutionPlan(actions=actions)

    def _build_create_task_action(
        self,
        understanding: dict[str, Any],
    ) -> ExecutionAction | None:
        """
        Build a CREATE_TASK action when understanding maps to task creation.

        Returns:
            ExecutionAction when intent/type and required payload fields
            are present, otherwise None.
        """
        if not self._is_create_task(understanding):
            return None

        payload = self._extract_task_payload(understanding)
        if not self._has_required_task_fields(payload):
            return None

        return ExecutionAction(
            type=ActionType.CREATE_TASK,
            payload=payload,
        )

    def _is_create_task(self, understanding: dict[str, Any]) -> bool:
        """
        Determine whether understanding should produce a CREATE_TASK action.
        """
        intent = understanding.get("intent")
        if isinstance(intent, str):
            normalized_intent = intent.strip().lower().replace(" ", "_")
            if normalized_intent in self._CREATE_TASK_INTENTS:
                return True

        understanding_type = understanding.get("type")
        if isinstance(understanding_type, str):
            if understanding_type.strip().upper() in self._CREATE_TASK_TYPES:
                return True

        return False

    def _extract_task_payload(self, understanding: dict[str, Any]) -> dict[str, Any]:
        """
        Copy task-relevant fields from understanding into an action payload.

        Only known TaskCreate-compatible fields are included. AI metadata
        such as confidence scores is intentionally excluded.
        """
        payload: dict[str, Any] = {}

        for field in self._TASK_PAYLOAD_FIELDS:
            value = understanding.get(field)
            if value is not None:
                payload[field] = value

        return payload

    def _has_required_task_fields(self, payload: dict[str, Any]) -> bool:
        """
        Validate that the minimum fields required to create a task are present.
        """
        family_id = payload.get("family_id")
        title = payload.get("title")

        if not isinstance(family_id, str) or not family_id.strip():
            return False

        if not isinstance(title, str) or not title.strip():
            return False

        return True
