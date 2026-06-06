"""Part of WhatsApp AI Bot by Viprasol Tech Private Limited (https://viprasol.com).

Unit tests for the building blocks: payload parsing, the deterministic FakeLLM,
the fake WhatsApp client, the router, and CloudApiClient construction/endpoint.
"""

from __future__ import annotations

import pytest

from tests.conftest import text_message_payload
from whatsapp_ai_bot.llm import FakeLLM
from whatsapp_ai_bot.models import (
    InboundMessage,
    OutboundMessage,
    parse_webhook_payload,
)
from whatsapp_ai_bot.router import MessageRouter
from whatsapp_ai_bot.whatsapp import CloudApiClient, FakeWhatsAppClient


def test_parse_webhook_payload_extracts_text() -> None:
    payload = text_message_payload(text="hi there", from_number="15551112222")
    messages = parse_webhook_payload(payload)
    assert len(messages) == 1
    msg = messages[0]
    assert msg.text == "hi there"
    assert msg.from_number == "15551112222"
    assert msg.contact_name == "Alice"
    assert msg.message_id == "wamid.TEST123"


def test_parse_webhook_payload_empty() -> None:
    assert parse_webhook_payload({}) == []


def test_fake_llm_is_deterministic() -> None:
    llm = FakeLLM()
    assert llm.complete("hello") == llm.complete("hello")


def test_fake_llm_greeting() -> None:
    llm = FakeLLM(assistant_name="Viprasol Assistant")
    reply = llm.complete("hi")
    assert "Viprasol Assistant" in reply


def test_fake_llm_help_branch() -> None:
    assert "help" in FakeLLM().complete("I need help").lower()


def test_fake_llm_empty_input() -> None:
    assert FakeLLM().complete("   ") == "I didn't catch that — could you say it again?"


def test_fake_whatsapp_records_sends() -> None:
    client = FakeWhatsAppClient()
    assert client.last is None
    wamid = client.send_text(OutboundMessage(to_number="1", text="hi"))
    assert wamid == "fake-wamid-1"
    assert client.last is not None
    assert client.last.text == "hi"


def test_router_handle_sends_via_client() -> None:
    fake = FakeWhatsAppClient()
    router = MessageRouter(llm=FakeLLM(), whatsapp=fake, bot_name="Bot")
    inbound = InboundMessage(
        message_id="wamid.X",
        from_number="15550000000",
        text="hello",
        contact_name="Sam",
    )
    reply = router.handle(inbound)
    assert reply.to_number == "15550000000"
    assert reply.text.startswith("Hi Sam,")
    assert fake.sent == [reply]


def test_cloud_api_client_requires_credentials() -> None:
    with pytest.raises(ValueError, match="requires"):
        CloudApiClient(access_token="", phone_number_id="")


def test_cloud_api_client_endpoint() -> None:
    client = CloudApiClient(
        access_token="tok",
        phone_number_id="123",
        graph_api_version="v21.0",
    )
    assert client.endpoint == "https://graph.facebook.com/v21.0/123/messages"
