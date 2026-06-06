"""Part of WhatsApp AI Bot by Viprasol Tech Private Limited (https://viprasol.com).

Domain models shared across the bot: a normalised inbound message and the
outbound reply, plus a parser that turns a raw WhatsApp Cloud API webhook
payload into typed :class:`InboundMessage` objects.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class InboundMessage(BaseModel):
    """A single normalised inbound WhatsApp text message."""

    message_id: str = Field(..., description="WhatsApp message id (wamid.*).")
    from_number: str = Field(..., description="Sender's phone number in E.164.")
    text: str = Field(..., description="Plain text body of the message.")
    timestamp: str = Field("", description="Unix timestamp as sent by WhatsApp.")
    contact_name: str = Field("", description="Sender profile name, if provided.")


class OutboundMessage(BaseModel):
    """A reply the bot wants to send back to a user."""

    to_number: str = Field(..., description="Recipient phone number in E.164.")
    text: str = Field(..., description="Reply body to deliver.")


def parse_webhook_payload(payload: dict[str, Any]) -> list[InboundMessage]:
    """Extract inbound text messages from a WhatsApp Cloud API webhook payload.

    The Cloud API nests messages under ``entry[].changes[].value.messages[]``.
    Non-text messages and malformed entries are skipped rather than raising, so
    the webhook always returns ``200`` and never gets retried into a loop.
    """
    messages: list[InboundMessage] = []

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            contacts = value.get("contacts", []) or []
            name_by_wa_id = {
                contact.get("wa_id", ""): (contact.get("profile", {}).get("name", ""))
                for contact in contacts
                if isinstance(contact, dict)
            }

            for raw in value.get("messages", []) or []:
                if not isinstance(raw, dict) or raw.get("type") != "text":
                    continue
                body = raw.get("text", {}).get("body")
                from_number = raw.get("from")
                message_id = raw.get("id")
                if not (body and from_number and message_id):
                    continue
                messages.append(
                    InboundMessage(
                        message_id=message_id,
                        from_number=from_number,
                        text=body,
                        timestamp=str(raw.get("timestamp", "")),
                        contact_name=name_by_wa_id.get(from_number, ""),
                    )
                )

    return messages
