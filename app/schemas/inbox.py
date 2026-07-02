"""
Input and output schemas for the Inbox API.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class InboxCreate(BaseModel):
    """Request payload for creating a new inbox item."""

    family_id: str
    raw_content: str
    source_type: str = "text"


class InboxProcessResponse(BaseModel):
    """Response returned after inbox submission and processing."""

    inbox_item: dict[str, Any]
    understanding: dict[str, Any] = Field(default_factory=dict)
    execution_plan: dict[str, Any] = Field(default_factory=dict)
    execution_results: list[dict[str, Any]] = Field(default_factory=list)
    processing_error: str | None = None
