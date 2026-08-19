#!/bin/bash
# CoreTrust Hermes — Pipeline Test Script
# Run from project root: bash scripts/test_pipeline.sh

BASE_URL="http://127.0.0.1:3000"
API_KEY=$(grep HERMES_API_KEY .env | cut -d= -f2)
SESSION_ID="test-session-$(date +%s)"

echo "=== CoreTrust Hermes Pipeline Test ==="
echo "Session: $SESSION_ID"
echo ""

# Health check
echo "[1] Health check..."
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""

# Planner stage
echo "[2] Planner stage..."
curl -s -X POST "$BASE_URL/run-agent" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"stage\": \"planner\",
    \"input\": { \"raw\": \"Inbound credit dispute inquiry from GTA small business owner\" },
    \"session_id\": \"$SESSION_ID\"
  }" | python3 -m json.tool
echo ""

echo "=== Test complete ==="
