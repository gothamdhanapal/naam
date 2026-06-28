"""
Execution Engine bootstrap.

Centralizes wiring for the execution layer so the rest of the
application obtains a fully configured ExecutionEngine from a single
entry point instead of assembling registries and services manually.
"""

from __future__ import annotations

from typing import Type

from app.execution.actions.base import BaseAction
from app.execution.actions.create_task import CreateTaskAction
from app.execution.engine import ExecutionEngine
from app.execution.models import ActionType
from app.execution.registry import ActionRegistry
from app.services.task_service import TaskService


def _register_actions(registry: ActionRegistry) -> None:
    """
    Register all supported execution action handlers.

    Add new ActionType → handler mappings here as actions are implemented.
    """
    _ACTION_HANDLERS: list[tuple[ActionType, Type[BaseAction]]] = [
        (ActionType.CREATE_TASK, CreateTaskAction),
    ]

    for action_type, handler_class in _ACTION_HANDLERS:
        registry.register(action_type, handler_class)


def _create_services() -> dict[str, object]:
    """
    Instantiate services required by execution action handlers.

    Add new service instances here as additional actions are implemented.
    Keys must match the dependency names expected by action handlers.
    """
    return {
        "task_service": TaskService(),
    }


def create_execution_engine() -> ExecutionEngine:
    """
    Build and return a fully configured ExecutionEngine.

    Wires together the action registry, application services, and engine
    instance. Callers should use this factory rather than constructing
    these objects directly.

    Returns:
        ExecutionEngine with all currently supported actions registered
        and required services injected.
    """
    registry = ActionRegistry()
    _register_actions(registry)

    services = _create_services()

    return ExecutionEngine(
        registry=registry,
        **services,
    )
