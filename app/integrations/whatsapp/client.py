"""
WhatsApp Cloud API client.

Thin wrapper around the Meta WhatsApp Cloud API for outbound messaging.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.integrations.whatsapp.models import OutgoingMediaMessage, OutgoingTextMessage

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """
    Client for the WhatsApp Cloud API.

    Accepts credentials via constructor injection for testability.
    """

    def __init__(
        self,
        access_token: str,
        phone_number_id: str,
        api_version: str = "v21.0",
        timeout: float = 30.0,
    ) -> None:
        """
        Initialize the WhatsApp client.

        Args:
            access_token: Meta Graph API access token.
            phone_number_id: WhatsApp business phone number ID.
            api_version: Graph API version to use.
            timeout: HTTP request timeout in seconds.
        """
        self._access_token = access_token
        self._phone_number_id = phone_number_id
        self._api_version = api_version
        self._timeout = timeout

    @property
    def _messages_url(self) -> str:
        return (
            f"https://graph.facebook.com/{self._api_version}/"
            f"{self._phone_number_id}/messages"
        )

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

    async def send_text(self, message: OutgoingTextMessage) -> dict[str, Any]:
        """
        Send a text message to a WhatsApp user.

        Args:
            message: Outgoing text message payload.

        Returns:
            Raw API response data.
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": message.to,
            "type": "text",
            "text": {
                "preview_url": message.preview_url,
                "body": message.body,
            },
        }
        return await self._post(payload)

    async def mark_as_read(self, message_id: str) -> dict[str, Any]:
        """
        Mark an incoming message as read.

        Args:
            message_id: WhatsApp message ID (wamid).

        Returns:
            Raw API response data.
        """
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        return await self._post(payload)

    async def send_image(self, message: OutgoingMediaMessage) -> dict[str, Any]:
        """
        Send an image message.

        Stub for future media support.
        """
        raise NotImplementedError("WhatsApp image messages are not yet implemented.")

    async def send_document(self, message: OutgoingMediaMessage) -> dict[str, Any]:
        """
        Send a document message.

        Stub for future media support.
        """
        raise NotImplementedError("WhatsApp document messages are not yet implemented.")

    async def send_audio(self, message: OutgoingMediaMessage) -> dict[str, Any]:
        """
        Send an audio message.

        Stub for future media support.
        """
        raise NotImplementedError("WhatsApp audio messages are not yet implemented.")

    async def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute a POST request against the WhatsApp messages endpoint."""
        url = self._messages_url
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                url,
                headers=self._headers(),
                json=payload,
            )
            if response.is_error:
                logger.error(
                    "WhatsApp Graph API request failed: url=%s status=%s body=%s",
                    url,
                    response.status_code,
                    response.text,
                )
            response.raise_for_status()
            return response.json()
