# Changelog

All notable changes to this project are documented here. Format based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[SemVer](https://semver.org/).

## [0.1.0] - 2025

### Added
- Initial release of WhatsApp AI Bot.
- FastAPI webhook for the WhatsApp Cloud API: `GET /webhook` verify handshake and `POST /webhook` inbound message handling.
- `MessageRouter` that routes inbound messages to a pluggable LLM and formats replies.
- `BaseLLM` interface with a deterministic offline `FakeLLM`.
- `BaseWhatsAppClient` interface with `FakeWhatsAppClient` (records sends) and a real `CloudApiClient` (lazy `httpx` import).
- Environment-based configuration via `pydantic-settings`.
- Sample payloads, `Dockerfile`, `docker-compose.yml`, and an offline test-suite (FastAPI `TestClient`).
