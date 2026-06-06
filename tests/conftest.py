"""Part of WhatsApp AI Bot by Viprasol Tech Private Limited (https://viprasol.com).

Shared pytest fixtures: an offline app wired with the deterministic fakes plus
a FastAPI ``TestClient``, so every test runs without network access or keys.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from whatsapp_ai_bot.app import create_app
from whatsapp_ai_bot.config import Settings
from whatsapp_ai_bot.llm import FakeLLM
from whatsapp_ai_bot.whatsapp import FakeWhatsAppClient

VERIFY_TOKEN = "test-verify-token"


@pytest.fixture
def settings() -> Settings:
    return Settings(verify_token=VERIFY_TOKEN, bot_name="Viprasol Assistant")


@pytest.fixture
def fake_whatsapp() -> FakeWhatsAppClient:
    return FakeWhatsAppClient()


@pytest.fixture
def app(settings: Settings, fake_whatsapp: FakeWhatsAppClient) -> FastAPI:
    return create_app(
        settings=settings,
        llm=FakeLLM(assistant_name=settings.bot_name),
        whatsapp=fake_whatsapp,
    )


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def text_message_payload(
    *,
    text: str = "Hello there",
    from_number: str = "15550001111",
    message_id: str = "wamid.TEST123",
    name: str = "Alice",
) -> dict[str, object]:
    """Build a minimal WhatsApp Cloud API text-message webhook payload."""
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WABA_ID",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15551234567",
                                "phone_number_id": "PHONE_NUMBER_ID",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": name},
                                    "wa_id": from_number,
                                }
                            ],
                            "messages": [
                                {
                                    "from": from_number,
                                    "id": message_id,
                                    "timestamp": "1700000000",
                                    "type": "text",
                                    "text": {"body": text},
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }
