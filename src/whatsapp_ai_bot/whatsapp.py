"""Part of WhatsApp AI Bot by Viprasol Tech Private Limited (https://viprasol.com).

WhatsApp client abstraction. ``BaseWhatsAppClient`` is the send interface;
``FakeWhatsAppClient`` records sent messages in-memory for tests and demos;
``CloudApiClient`` posts to the real WhatsApp Cloud API (httpx is imported
lazily so the package and its tests have no hard runtime dependency on it).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from whatsapp_ai_bot.models import OutboundMessage


class BaseWhatsAppClient(ABC):
    """Interface for delivering an :class:`OutboundMessage` to a user."""

    @abstractmethod
    def send_text(self, message: OutboundMessage) -> str:
        """Send ``message`` and return a provider message id."""
        raise NotImplementedError


class FakeWhatsAppClient(BaseWhatsAppClient):
    """An offline client that records sent messages instead of delivering them.

    Inspect :attr:`sent` in tests to assert on what the bot replied with.
    """

    def __init__(self) -> None:
        self.sent: list[OutboundMessage] = []

    def send_text(self, message: OutboundMessage) -> str:
        self.sent.append(message)
        return f"fake-wamid-{len(self.sent)}"

    @property
    def last(self) -> OutboundMessage | None:
        """The most recently recorded message, or ``None`` if nothing was sent."""
        return self.sent[-1] if self.sent else None


class CloudApiClient(BaseWhatsAppClient):
    """Sends messages through the real WhatsApp Cloud API (Meta Graph API).

    ``httpx`` is imported lazily inside :meth:`send_text` so importing this
    module — and running the offline test-suite — never requires the dependency.
    """

    def __init__(
        self,
        *,
        access_token: str,
        phone_number_id: str,
        graph_api_version: str = "v21.0",
        timeout: float = 10.0,
    ) -> None:
        if not access_token or not phone_number_id:
            msg = "CloudApiClient requires access_token and phone_number_id."
            raise ValueError(msg)
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.graph_api_version = graph_api_version
        self.timeout = timeout

    @property
    def endpoint(self) -> str:
        """Graph API messages endpoint for the configured phone number."""
        return (
            f"https://graph.facebook.com/{self.graph_api_version}"
            f"/{self.phone_number_id}/messages"
        )

    def send_text(self, message: OutboundMessage) -> str:
        import httpx  # lazy import: optional dependency

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": message.to_number,
            "type": "text",
            "text": {"preview_url": False, "body": message.text},
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        response = httpx.post(
            self.endpoint,
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        messages = data.get("messages", [])
        if messages and isinstance(messages[0], dict):
            return str(messages[0].get("id", ""))
        return ""
