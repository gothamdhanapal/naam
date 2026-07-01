"""
WhatsApp webhook handlers.

Receives and validates Meta webhook callbacks and forwards messages
to the WhatsApp service.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import PlainTextResponse

from app.core.config import settings
from app.integrations.whatsapp.client import WhatsAppClient
from app.integrations.whatsapp.models import (
    WebhookVerificationParams,
    WhatsAppWebhookPayload,
)
from app.integrations.whatsapp.service import WhatsAppService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/whatsapp", tags=["WhatsApp"])


def _require_verify_token() -> None:
    """Ensure the Meta webhook verify token is configured."""
    if not settings.WHATSAPP_VERIFY_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="WhatsApp verify token is not configured.",
        )


def _require_whatsapp_config() -> None:
    """Ensure required WhatsApp settings are configured."""
    missing = []
    if not settings.WHATSAPP_VERIFY_TOKEN:
        missing.append("WHATSAPP_VERIFY_TOKEN")
    if not settings.WHATSAPP_ACCESS_TOKEN:
        missing.append("WHATSAPP_ACCESS_TOKEN")
    if not settings.WHATSAPP_PHONE_NUMBER_ID:
        missing.append("WHATSAPP_PHONE_NUMBER_ID")
    if not settings.WHATSAPP_DEFAULT_FAMILY_ID:
        missing.append("WHATSAPP_DEFAULT_FAMILY_ID")

    if missing:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"WhatsApp integration is not configured: {', '.join(missing)}",
        )


def get_whatsapp_client() -> WhatsAppClient:
    """Provide a configured WhatsApp Cloud API client."""
    _require_whatsapp_config()
    return WhatsAppClient(
        access_token=settings.WHATSAPP_ACCESS_TOKEN,
        phone_number_id=settings.WHATSAPP_PHONE_NUMBER_ID,
        api_version=settings.WHATSAPP_API_VERSION,
    )


def get_whatsapp_service(
    client: WhatsAppClient = Depends(get_whatsapp_client),
) -> WhatsAppService:
    """Provide a configured WhatsApp service."""
    return WhatsAppService(
        client=client,
        default_family_id=settings.WHATSAPP_DEFAULT_FAMILY_ID,
    )


def _verify_signature(raw_body: bytes, signature_header: str | None) -> None:
    """
    Validate the X-Hub-Signature-256 header when an app secret is configured.
    """
    app_secret = settings.WHATSAPP_APP_SECRET
    if not app_secret:
        return

    if not signature_header or not signature_header.startswith("sha256="):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing or invalid webhook signature.",
        )

    expected = hmac.new(
        app_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    received = signature_header.removeprefix("sha256=")

    if not hmac.compare_digest(expected, received):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid webhook signature.",
        )


@router.get("")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
) -> PlainTextResponse:
    """
    Handle Meta webhook verification challenge.

    Meta sends a GET request during webhook setup. Respond with the
    hub.challenge value when the verify token matches.
    """
    _require_verify_token()
    params = WebhookVerificationParams(
        **{
            "hub.mode": hub_mode,
            "hub.verify_token": hub_verify_token,
            "hub.challenge": hub_challenge,
        }
    )

    if params.hub_mode != "subscribe":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid hub.mode.",
        )

    if params.hub_verify_token != settings.WHATSAPP_VERIFY_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid verify token.",
        )

    return PlainTextResponse(content=params.hub_challenge)


@router.post("")
async def receive_webhook(
    request: Request,
    service: WhatsAppService = Depends(get_whatsapp_service),
) -> dict[str, Any]:
    """
    Receive incoming WhatsApp webhook callbacks.

    Validates the request, extracts text messages, and forwards them
    to the WhatsApp service for inbox ingestion.
    """
    raw_body = await request.body()
    _verify_signature(raw_body, request.headers.get("X-Hub-Signature-256"))

    payload = WhatsAppWebhookPayload.model_validate_json(raw_body)

    if payload.object != "whatsapp_business_account":
        logger.info("Ignoring webhook for unsupported object: %s", payload.object)
        return {"status": "ignored", "processed": 0}

    results = await service.handle_webhook_payload(payload)

    return {
        "status": "ok",
        "processed": len(results),
        "results": [result.model_dump() for result in results],
    }
