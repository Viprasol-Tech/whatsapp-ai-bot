"""Part of WhatsApp AI Bot by Viprasol Tech Private Limited (https://viprasol.com).

The FastAPI application. It exposes the WhatsApp Cloud API webhook:

* ``GET  /webhook`` — Meta's verification handshake (echoes ``hub.challenge``).
* ``POST /webhook`` — receives inbound messages, routes them to the LLM, and
  replies through the configured WhatsApp client.

By default everything runs offline with :class:`FakeLLM` and
:class:`FakeWhatsAppClient`; set real Cloud API credentials in the environment
to switch to the live sender.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import PlainTextResponse

from whatsapp_ai_bot.config import Settings, get_settings
from whatsapp_ai_bot.llm import BaseLLM, FakeLLM
from whatsapp_ai_bot.models import parse_webhook_payload
from whatsapp_ai_bot.router import MessageRouter
from whatsapp_ai_bot.whatsapp import (
    BaseWhatsAppClient,
    CloudApiClient,
    FakeWhatsAppClient,
)


def build_llm(settings: Settings) -> BaseLLM:
    """Construct the LLM provider for the given settings (offline fake default)."""
    return FakeLLM(assistant_name=settings.bot_name)


def build_whatsapp_client(settings: Settings) -> BaseWhatsAppClient:
    """Construct the WhatsApp client: real Cloud API if configured, else fake."""
    if settings.use_real_whatsapp and settings.whatsapp_configured:
        return CloudApiClient(
            access_token=settings.whatsapp_access_token,
            phone_number_id=settings.whatsapp_phone_number_id,
            graph_api_version=settings.graph_api_version,
        )
    return FakeWhatsAppClient()


def create_app(
    *,
    settings: Settings | None = None,
    llm: BaseLLM | None = None,
    whatsapp: BaseWhatsAppClient | None = None,
) -> FastAPI:
    """Application factory.

    Pass ``settings``, ``llm`` and/or ``whatsapp`` to inject custom components
    (the test-suite uses this to supply fakes and assert on recorded sends).
    """
    settings = settings or get_settings()
    llm = llm or build_llm(settings)
    whatsapp = whatsapp or build_whatsapp_client(settings)
    router = MessageRouter(llm=llm, whatsapp=whatsapp, bot_name=settings.bot_name)

    app = FastAPI(
        title="WhatsApp AI Bot",
        version="0.1.0",
        summary="FastAPI webhook for the WhatsApp Cloud API, backed by an LLM.",
    )
    # Expose components for tests and other consumers.
    app.state.settings = settings
    app.state.llm = llm
    app.state.whatsapp = whatsapp
    app.state.router = router

    @app.get("/", include_in_schema=False)
    def index() -> dict[str, str]:
        return {
            "name": "WhatsApp AI Bot",
            "vendor": "Viprasol Tech Private Limited",
            "docs": "/docs",
        }

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/webhook")
    def verify_webhook(request: Request) -> Response:
        """Meta webhook verification handshake."""
        params = request.query_params
        mode = params.get("hub.mode")
        token = params.get("hub.verify_token")
        challenge = params.get("hub.challenge", "")
        if mode == "subscribe" and token == settings.verify_token:
            return PlainTextResponse(challenge, status_code=status.HTTP_200_OK)
        return PlainTextResponse(
            "verification failed",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    @app.post("/webhook")
    async def receive_webhook(request: Request) -> dict[str, Any]:
        """Receive inbound WhatsApp messages and reply via the router."""
        payload = await request.json()
        messages = parse_webhook_payload(payload)
        replies = [router.handle(message) for message in messages]
        return {"status": "received", "handled": len(replies)}

    return app


app = create_app()
