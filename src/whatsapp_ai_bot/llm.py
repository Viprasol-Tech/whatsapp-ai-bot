"""Part of WhatsApp AI Bot by Viprasol Tech Private Limited (https://viprasol.com).

The LLM abstraction. ``BaseLLM`` is the provider interface the router depends
on; ``FakeLLM`` is a deterministic, network-free implementation used for local
runs and tests. Plug in a real provider (OpenAI, Anthropic, etc.) by
subclassing ``BaseLLM`` and implementing :meth:`complete`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """Provider-agnostic large-language-model interface."""

    @abstractmethod
    def complete(self, prompt: str, *, system: str = "") -> str:
        """Return a completion for ``prompt`` given an optional ``system`` prompt."""
        raise NotImplementedError


class FakeLLM(BaseLLM):
    """A deterministic offline LLM.

    It never touches the network. Replies are derived purely from the input so
    tests are stable and the bot is usable for demos without any API key.
    """

    def __init__(self, *, assistant_name: str = "Viprasol Assistant") -> None:
        self.assistant_name = assistant_name

    def complete(self, prompt: str, *, system: str = "") -> str:
        text = prompt.strip()
        lowered = text.lower()

        if not text:
            return "I didn't catch that — could you say it again?"

        if any(word in lowered for word in ("hi", "hello", "hey")):
            return f"Hello! I'm {self.assistant_name}. How can I help you today?"

        if "help" in lowered:
            return (
                "Sure, I can help. Tell me what you need and I'll do my best — "
                "you can ask me a question or describe your problem."
            )

        if "?" in text:
            return (
                f"Good question. Here's what I can tell you about "
                f'"{_truncate(text)}": I\'m a demo assistant, so connect a real '
                f"LLM provider for full answers."
            )

        return f"You said: {_truncate(text)}. Thanks for your message!"


def _truncate(text: str, limit: int = 160) -> str:
    """Collapse whitespace and clip ``text`` to ``limit`` characters."""
    collapsed = " ".join(text.split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 1].rstrip() + "…"
