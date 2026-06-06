"""Part of WhatsApp AI Bot by Viprasol Tech Private Limited (https://viprasol.com).

WhatsApp AI Bot — a FastAPI webhook for the WhatsApp Cloud API that routes
inbound messages to an LLM and replies. Ships with deterministic offline fakes
so it runs and tests without any network access or API keys.
"""

from __future__ import annotations

from whatsapp_ai_bot.config import Settings, get_settings
from whatsapp_ai_bot.llm import BaseLLM, FakeLLM
from whatsapp_ai_bot.models import InboundMessage, OutboundMessage
from whatsapp_ai_bot.router import MessageRouter
from whatsapp_ai_bot.whatsapp import (
    BaseWhatsAppClient,
    CloudApiClient,
    FakeWhatsAppClient,
)

__version__ = "0.1.0"

__all__ = [
    "BaseLLM",
    "BaseWhatsAppClient",
    "CloudApiClient",
    "FakeLLM",
    "FakeWhatsAppClient",
    "InboundMessage",
    "MessageRouter",
    "OutboundMessage",
    "Settings",
    "__version__",
    "get_settings",
]
