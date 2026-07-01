"""Unit tests for WhatsApp webhook handlers."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.integrations.whatsapp.webhook import router


@pytest.fixture
def whatsapp_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(whatsapp_app: FastAPI) -> TestClient:
    return TestClient(whatsapp_app, follow_redirects=False)


def test_get_verification_succeeds_with_only_verify_token(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.integrations.whatsapp.webhook.settings.WHATSAPP_VERIFY_TOKEN",
        "test-verify-token",
    )
    monkeypatch.setattr(
        "app.integrations.whatsapp.webhook.settings.WHATSAPP_ACCESS_TOKEN",
        "",
    )
    monkeypatch.setattr(
        "app.integrations.whatsapp.webhook.settings.WHATSAPP_PHONE_NUMBER_ID",
        "",
    )
    monkeypatch.setattr(
        "app.integrations.whatsapp.webhook.settings.WHATSAPP_DEFAULT_FAMILY_ID",
        "",
    )

    challenge = "1158201444"
    response = client.get(
        "/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "test-verify-token",
            "hub.challenge": challenge,
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert response.text == challenge


def test_get_verification_rejects_invalid_token(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.integrations.whatsapp.webhook.settings.WHATSAPP_VERIFY_TOKEN",
        "test-verify-token",
    )

    response = client.get(
        "/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong-token",
            "hub.challenge": "1158201444",
        },
    )

    assert response.status_code == 403


def test_get_verification_requires_verify_token_configured(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.integrations.whatsapp.webhook.settings.WHATSAPP_VERIFY_TOKEN",
        "",
    )

    response = client.get(
        "/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "any-token",
            "hub.challenge": "1158201444",
        },
    )

    assert response.status_code == 503
