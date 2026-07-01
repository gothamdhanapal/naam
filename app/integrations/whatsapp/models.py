"""
Pydantic models for WhatsApp Cloud API webhooks and outbound messages.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WebhookVerificationParams(BaseModel):
    """Query parameters for Meta webhook verification."""

    hub_mode: str = Field(alias="hub.mode")
    hub_verify_token: str = Field(alias="hub.verify_token")
    hub_challenge: str = Field(alias="hub.challenge")

    model_config = ConfigDict(populate_by_name=True)


class WhatsAppTextBody(BaseModel):
    """Text body of an incoming WhatsApp message."""

    body: str


class WhatsAppIncomingMessage(BaseModel):
    """A single incoming WhatsApp message from a webhook payload."""

    sender: str = Field(alias="from")
    id: str
    timestamp: str
    type: str
    text: WhatsAppTextBody | None = None

    model_config = ConfigDict(populate_by_name=True)

    def extract_text(self) -> str | None:
        """Return message text when the payload is a text message."""
        if self.type != "text" or self.text is None:
            return None
        return self.text.body.strip() or None


class WhatsAppWebhookMetadata(BaseModel):
    """Phone number metadata included in webhook value objects."""

    display_phone_number: str | None = None
    phone_number_id: str | None = None


class WhatsAppWebhookValue(BaseModel):
    """Value object within a WhatsApp webhook change."""

    messaging_product: str | None = None
    metadata: WhatsAppWebhookMetadata | None = None
    messages: list[WhatsAppIncomingMessage] = Field(default_factory=list)
    statuses: list[dict[str, Any]] = Field(default_factory=list)


class WhatsAppWebhookChange(BaseModel):
    """A single change entry in a WhatsApp webhook payload."""

    field: str | None = None
    value: WhatsAppWebhookValue | None = None


class WhatsAppWebhookEntry(BaseModel):
    """Top-level entry in a WhatsApp webhook payload."""

    id: str | None = None
    changes: list[WhatsAppWebhookChange] = Field(default_factory=list)


class WhatsAppWebhookPayload(BaseModel):
    """Incoming webhook payload from the WhatsApp Cloud API."""

    object: str | None = None
    entry: list[WhatsAppWebhookEntry] = Field(default_factory=list)

    def extract_text_messages(self) -> list[WhatsAppIncomingMessage]:
        """
        Extract incoming text messages from the webhook payload.

        Status updates and unsupported message types are ignored.
        """
        messages: list[WhatsAppIncomingMessage] = []

        for entry in self.entry:
            for change in entry.changes:
                if change.value is None:
                    continue
                for message in change.value.messages:
                    if message.extract_text() is not None:
                        messages.append(message)

        return messages


class OutgoingTextMessage(BaseModel):
    """Payload for sending a text message via the WhatsApp Cloud API."""

    to: str
    body: str
    preview_url: bool = False


class OutgoingMediaMessage(BaseModel):
    """Base payload for future media message support."""

    to: str
    media_url: str
    caption: str | None = None


class WhatsAppIngestionResult(BaseModel):
    """Result of ingesting a WhatsApp message into the inbox."""

    message_id: str
    inbox_item: dict[str, Any]
