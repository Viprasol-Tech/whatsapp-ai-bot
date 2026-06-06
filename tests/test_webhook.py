"""Part of WhatsApp AI Bot by Viprasol Tech Private Limited (https://viprasol.com).

End-to-end webhook tests driven through the FastAPI ``TestClient``, fully
offline: verify handshake, inbound parsing, and the inbound -> LLM -> client
delivery path asserted against the fake client's recorded sends.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import VERIFY_TOKEN, text_message_payload
from whatsapp_ai_bot.whatsapp import FakeWhatsAppClient


def test_health_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_index_mentions_vendor(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Viprasol" in response.json()["vendor"]


def test_webhook_verify_handshake_success(client: TestClient) -> None:
    response = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": VERIFY_TOKEN,
            "hub.challenge": "challenge-42",
        },
    )
    assert response.status_code == 200
    assert response.text == "challenge-42"


def test_webhook_verify_handshake_wrong_token(client: TestClient) -> None:
    response = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "nope",
            "hub.challenge": "challenge-42",
        },
    )
    assert response.status_code == 403


def test_webhook_verify_handshake_wrong_mode(client: TestClient) -> None:
    response = client.get(
        "/webhook",
        params={
            "hub.mode": "unsubscribe",
            "hub.verify_token": VERIFY_TOKEN,
            "hub.challenge": "x",
        },
    )
    assert response.status_code == 403


def test_inbound_message_triggers_fake_reply(
    client: TestClient, fake_whatsapp: FakeWhatsAppClient
) -> None:
    payload = text_message_payload(text="hello", from_number="15550009999")
    response = client.post("/webhook", json=payload)

    assert response.status_code == 200
    assert response.json() == {"status": "received", "handled": 1}

    assert len(fake_whatsapp.sent) == 1
    sent = fake_whatsapp.last
    assert sent is not None
    assert sent.to_number == "15550009999"
    assert "Viprasol Assistant" in sent.text


def test_inbound_reply_addresses_contact_by_name(
    client: TestClient, fake_whatsapp: FakeWhatsAppClient
) -> None:
    payload = text_message_payload(text="random words", name="Bob")
    client.post("/webhook", json=payload)
    sent = fake_whatsapp.last
    assert sent is not None
    assert sent.text.startswith("Hi Bob,")


def test_non_text_message_is_ignored(
    client: TestClient, fake_whatsapp: FakeWhatsAppClient
) -> None:
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": "15550001111",
                                    "id": "wamid.IMG",
                                    "type": "image",
                                    "image": {"id": "media-1"},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    response = client.post("/webhook", json=payload)
    assert response.status_code == 200
    assert response.json()["handled"] == 0
    assert fake_whatsapp.sent == []


def test_empty_payload_handled_gracefully(
    client: TestClient, fake_whatsapp: FakeWhatsAppClient
) -> None:
    response = client.post("/webhook", json={})
    assert response.status_code == 200
    assert response.json()["handled"] == 0
    assert fake_whatsapp.sent == []


def test_multiple_messages_all_handled(
    client: TestClient, fake_whatsapp: FakeWhatsAppClient
) -> None:
    payload = text_message_payload(text="hi")
    extra = {
        "from": "15550002222",
        "id": "wamid.SECOND",
        "timestamp": "1700000001",
        "type": "text",
        "text": {"body": "help me please"},
    }
    payload["entry"][0]["changes"][0]["value"]["messages"].append(extra)  # type: ignore[index]

    response = client.post("/webhook", json=payload)
    assert response.json()["handled"] == 2
    assert len(fake_whatsapp.sent) == 2
