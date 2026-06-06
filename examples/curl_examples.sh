#!/usr/bin/env bash
# Part of WhatsApp AI Bot by Viprasol Tech Private Limited (https://viprasol.com).
#
# Sample requests against a locally running bot (python -m whatsapp_ai_bot).
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
VERIFY_TOKEN="${WAB_VERIFY_TOKEN:-dev-verify-token}"

echo "== Webhook verification handshake =="
curl -s "${BASE_URL}/webhook?hub.mode=subscribe&hub.verify_token=${VERIFY_TOKEN}&hub.challenge=12345"
echo

echo "== Send a sample inbound text message =="
curl -s -X POST "${BASE_URL}/webhook" \
  -H "Content-Type: application/json" \
  --data @"$(dirname "$0")/inbound_text.json"
echo
