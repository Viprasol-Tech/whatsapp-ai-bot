"""Part of WhatsApp AI Bot by Viprasol Tech Private Limited (https://viprasol.com).

Application configuration, loaded from environment variables (and an optional
``.env`` file) via pydantic-settings. Sensible offline defaults mean the app
boots and the test-suite runs without any real credentials.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the WhatsApp AI bot.

    All values can be supplied through environment variables. The defaults are
    deliberately safe for offline use so the bot can run with the bundled fakes.
    """

    model_config = SettingsConfigDict(
        env_prefix="WAB_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Webhook handshake (Meta calls GET /webhook with these on subscription).
    verify_token: str = "dev-verify-token"  # noqa: S105 - default; override via env

    # WhatsApp Cloud API credentials. Empty by default -> use the fake client.
    whatsapp_access_token: str = ""
    whatsapp_phone_number_id: str = ""
    graph_api_version: str = "v21.0"

    # Selects the real Cloud API sender when both credentials are present.
    use_real_whatsapp: bool = False

    # Bot persona, prepended to LLM prompts.
    bot_name: str = "Viprasol Assistant"

    @property
    def whatsapp_configured(self) -> bool:
        """True when real Cloud API credentials are available."""
        return bool(self.whatsapp_access_token and self.whatsapp_phone_number_id)


@lru_cache
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance."""
    return Settings()
