"""
Shared pytest fixtures and helpers for the Naam backend test suite.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import UUID

import pytest

from app.models.task import Task, TaskPriority, TaskStatus

FAMILY_ID = UUID("550e8400-e29b-41d4-a716-446655440000")
TASK_ID = UUID("660e8400-e29b-41d4-a716-446655440001")
INBOX_ID = UUID("770e8400-e29b-41d4-a716-446655440002")
NOW = datetime(2026, 6, 28, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_task_row() -> dict:
    """Raw task row as returned by Supabase."""
    return {
        "id": str(TASK_ID),
        "family_id": str(FAMILY_ID),
        "title": "Pay electricity bill",
        "description": None,
        "due_date": "2026-06-29",
        "priority": TaskPriority.MEDIUM.value,
        "status": TaskStatus.NEW.value,
        "assigned_member_id": None,
        "inbox_item_id": str(INBOX_ID),
        "created_at": NOW.isoformat(),
        "updated_at": NOW.isoformat(),
        "deleted_at": None,
    }


@pytest.fixture
def sample_task(sample_task_row: dict) -> Task:
    """Validated Task domain model."""
    return Task.from_row(sample_task_row)


def build_supabase_response(data: list | None) -> MagicMock:
    """Build a Supabase execute() response mock."""
    response = MagicMock()
    response.data = data
    return response


def build_query_chain(final_response: MagicMock) -> MagicMock:
    """
    Build a chainable Supabase query mock.

    Supports table().select().eq().is_().order().insert().update().execute().
    """
    chain = MagicMock()
    chain.execute.return_value = final_response
    chain.eq.return_value = chain
    chain.is_.return_value = chain
    chain.select.return_value = chain
    chain.insert.return_value = chain
    chain.update.return_value = chain
    chain.order.return_value = chain
    return chain


def build_supabase_client(final_response: MagicMock) -> MagicMock:
    """Build a Supabase client mock that returns a query chain."""
    client = MagicMock()
    client.table.return_value = build_query_chain(final_response)
    return client
