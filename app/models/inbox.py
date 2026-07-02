"""
Domain models for Inbox items.
"""

from __future__ import annotations

from enum import Enum


class InboxStatus(str, Enum):
    """Lifecycle status of an inbox item."""

    RECEIVED = "RECEIVED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
