#!/usr/bin/env bash
# Mythara Engine — Pilot Local Test Automation
# Copyright © 2026 Mythara Labs LLC. All rights reserved.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
API_DIR="$ROOT_DIR/core/source_proprietary"
LOG_DIR="${TMPDIR:-/tmp}"
API_LOG="$LOG_DIR/mythara_api.log"
STRIPE_LOG="$LOG_DIR/stripe_listen.log"

api_pid=""
stripe_pid=""

cleanup() {
  echo "\n[clean] Stopping background processes..."
  if [[ -n "${stripe_pid}" ]] && ps -p "${stripe_pid}" > /dev/null 2>&1; then
    kill "${stripe_pid}" || true
  fi
  if [[ -n "${api_pid}" ]] && ps -p "${api_pid}" > /dev/null 2>&1; then
    kill "${api_pid}" || true
  fi
}
trap cleanup EXIT

echo "[1/8] Ensuring Python dependencies are installed..."
python3 -m pip install -r "$API_DIR/requirements-api.txt" >/dev/null

echo "[2/8] Preparing environment for pilot paywall (test mode)..."
# Allow override via env or first arg for the purchase link
PURCHASE_URL_DEFAULT="https://buy.stripe.com/test_placeholder"
PURCHASE_URL_INPUT="${1:-}"  # optional arg
export MYTHARA_PILOT_PAYWALL="true"
export MYTHARA_PILOT_PURCHASE_URL="${MYTHARA_PILOT_PURCHASE_URL:-${PURCHASE_URL_INPUT:-$PURCHASE_URL_DEFAULT}}"
export MYTHARA_PILOT_FORCE_UNLOCK="false"

echo "       MYTHARA_PILOT_PURCHASE_URL=${MYTHARA_PILOT_PURCHASE_URL}"

echo "[3/8] Configuring webhook secret (Stripe CLI if available, else secure fallback)..."
have_stripe_cli="false"
if command -v stripe >/dev/null 2>&1; then
  have_stripe_cli="true"
  # Print a signing secret (does not start the listener)
  if secret_out=$(stripe listen --print-secret 2>/dev/null); then
    export STRIPE_WEBHOOK_SECRET="$secret_out"
    echo "       Using Stripe CLI signing secret: ${STRIPE_WEBHOOK_SECRET}"
  fi
else
  echo "       Stripe CLI not found; will use fallback shared-secret mode."
fi

# If we still don't have a secret, generate one for fallback mode
if [[ -z "${STRIPE_WEBHOOK_SECRET:-}" ]]; then
  export STRIPE_WEBHOOK_SECRET="whsec_$(python3 - <<'PY'
import secrets
print(secrets.token_hex(16))
PY
)"
  echo "       Generated fallback secret: ${STRIPE_WEBHOOK_SECRET}"
fi

echo "[4/8] Starting API server (logs: $API_LOG)..."
PYTHONUNBUFFERED=1 python3 "$API_DIR/main.py" >"$API_LOG" 2>&1 &
api_pid=$!
sleep 0.5

echo "       Waiting for API to become ready..."
attempts=0
until curl -sf "http://127.0.0.1:8000/health" >/dev/null 2>&1 || [[ $attempts -gt 60 ]]; do
  sleep 0.5
  attempts=$((attempts+1))
done
if ! curl -sf "http://127.0.0.1:8000/health" >/dev/null 2>&1; then
  echo "[error] API didn't come up in time. Tail:"
  tail -n 60 "$API_LOG" || true
  exit 1
fi

echo "[5/8] (Optional) Starting Stripe CLI listener (logs: $STRIPE_LOG)..."
if [[ "$have_stripe_cli" == "true" ]]; then
  # Start listener to forward events to API (non-blocking)
  stripe listen --forward-to localhost:8000/api/webhooks/stripe --log-level error >"$STRIPE_LOG" 2>&1 &
  stripe_pid=$!
  sleep 0.8
else
  echo "       Skipping listener (fallback shared-secret path)."
fi

echo "[6/8] Triggering a safe pilot unlock via signed fallback webhook..."
grant_response=$(curl -sS -X POST "http://127.0.0.1:8000/api/webhooks/stripe" \
  -H "x-shared-secret: ${STRIPE_WEBHOOK_SECRET}" \
  -H "Content-Type: application/json" \
  -d "{\n    \"type\": \"checkout.session.completed\",\n    \"license_type\": \"pilot\",\n    \"payment_id\": \"evt_auto_$(date +%s)\",\n    \"amount\": 49.00,\n    \"email\": \"pilot@example.com\"\n  }")
echo "       Webhook response: $grant_response"

echo "[7/8] Verifying pilot status..."
status_json=$(curl -sS "http://127.0.0.1:8000/v1/pilot/status")
echo "$status_json" | sed 's/.*/       &/'

granted=$(python3 - <<'PY'
import json,sys
try:
  data=json.load(sys.stdin)
  print(str(data.get('granted')))
except Exception:
  print('False')
PY
<<<"$status_json")

if [[ "$granted" != "True" ]]; then
  echo "[warn] Pilot not granted automatically. Showing API log tail:"
  tail -n 80 "$API_LOG" || true
  echo "[hint] You can open the purchase URL and complete a test checkout, then re-run this script."
else
  echo "[ok] Pilot access granted."
fi

echo "[8/8] Opening helpful pages (if available)..."
if [[ -n "${BROWSER:-}" ]]; then
  "$BROWSER" "http://127.0.0.1:8000/api/docs" || true
  if [[ -n "${MYTHARA_PILOT_PURCHASE_URL:-}" ]]; then
    "$BROWSER" "${MYTHARA_PILOT_PURCHASE_URL}" || true
  fi
else
  echo "       Tip: Open http://127.0.0.1:8000/api/docs in your browser."
  if [[ -n "${MYTHARA_PILOT_PURCHASE_URL:-}" ]]; then
    echo "       Pilot purchase link: ${MYTHARA_PILOT_PURCHASE_URL}"
  fi
fi

echo "\nAll set. Processes will stop when you Ctrl+C this script or when it exits."
