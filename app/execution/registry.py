"""
Action Registry for the Execution Engine.

The registry maps execution action types to their corresponding
action handler classes.

This keeps the Execution Engine generic and makes it easy
to add new actions without modifying the engine itself.
"""

from __future__ import annotations

from typing import Type

from app.execution.models import ActionType
from app.execution.actions.base import BaseAction


class ActionRegistry:
    """
    Stores the mapping between ActionType and Action Handler.
    """

    def __init__(self) -> None:
        self._actions: dict[ActionType, Type[BaseAction]] = {}

    def register(
        self,
        action_type: ActionType,
        action_class: Type[BaseAction],
    ) -> None:
        """
        Register an action handler for a given ActionType.
        """
        self._actions[action_type] = action_class

    def get(self, action_type: ActionType) -> Type[BaseAction]:
        """
        Return the registered handler for an ActionType.
        """
        try:
            return self._actions[action_type]
        except KeyError as exc:
            raise ValueError(
                f"No action registered for '{action_type.value}'"
            ) from exc

    def supports(self, action_type: ActionType) -> bool:
        """
        Check whether an ActionType has been registered.
        """
        return action_type in self._actions

    def registered_actions(self) -> list[ActionType]:
        """
        Return all registered action types.
        """
        return list(self._actions.keys())