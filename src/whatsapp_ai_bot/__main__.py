"""Part of WhatsApp AI Bot by Viprasol Tech Private Limited (https://viprasol.com).

Run the bot with ``python -m whatsapp_ai_bot``. This starts a uvicorn server
hosting the FastAPI webhook app.
"""

from __future__ import annotations


def main() -> None:
    """Start the uvicorn server (uvicorn is imported lazily)."""
    import uvicorn

    uvicorn.run(
        "whatsapp_ai_bot.app:app",
        host="0.0.0.0",  # noqa: S104 - container/server binds all interfaces
        port=8000,
    )


if __name__ == "__main__":
    main()
