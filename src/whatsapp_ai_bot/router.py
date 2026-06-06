"""Part of WhatsApp AI Bot by Viprasol Tech Private Limited (https://viprasol.com).

The :class:`MessageRouter` wires the pieces together: it takes an inbound
message, asks the LLM for a reply, formats an :class:`OutboundMessage`, and
hands it to the WhatsApp client for delivery.
"""

from __future__ import annotations

from whatsapp_ai_bot.llm import BaseLLM
from whatsapp_ai_bot.models import InboundMessage, OutboundMessage
from whatsapp_ai_bot.whatsapp import BaseWhatsAppClient


class MessageRouter:
    """Routes inbound messages through the LLM and out via the WhatsApp client."""

    def __init__(
        self,
        *,
        llm: BaseLLM,
        whatsapp: BaseWhatsAppClient,
        bot_name: str = "Viprasol Assistant",
    ) -> None:
        self.llm = llm
        self.whatsapp = whatsapp
        self.bot_name = bot_name

    def build_reply(self, message: InboundMessage) -> OutboundMessage:
        """Generate an outbound reply for ``message`` without sending it."""
        system = (
            f"You are {self.bot_name}, a helpful WhatsApp assistant. "
            f"Keep replies concise and friendly."
        )
        answer = self.llm.complete(message.text, system=system).strip()
        greeting = f"Hi {message.contact_name}, " if message.contact_name else ""
        body = f"{greeting}{answer}" if greeting else answer
        return OutboundMessage(to_number=message.from_number, text=body)

    def handle(self, message: InboundMessage) -> OutboundMessage:
        """Generate a reply for ``message`` and send it via the WhatsApp client."""
        reply = self.build_reply(message)
        self.whatsapp.send_text(reply)
        return reply
