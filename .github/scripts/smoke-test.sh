#!/bin/bash
# Post-deployment smoke test script
# Usage: ./smoke-test.sh <URL>
# Example: ./smoke-test.sh https://staging.heatflow.world

set -e

URL="${1}"
TIMEOUT=30
RETRY_INTERVAL=5

if [ -z "$URL" ]; then
    echo "Error: URL argument required"
    echo "Usage: $0 <URL>"
    exit 1
fi

echo "🔍 Running smoke tests for: $URL"
echo "================================================"

# Test 1: Health check endpoint
echo "Test 1: Health check endpoint..."
HEALTH_URL="${URL}/health/"
if curl -sf --max-time "$TIMEOUT" "$HEALTH_URL" > /dev/null 2>&1; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed: $HEALTH_URL not responding"
    exit 1
fi

# Test 2: Homepage accessibility
echo "Test 2: Homepage accessibility..."
HOME_URL="${URL}/"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$HOME_URL")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ Homepage accessible (HTTP 200)"
elif [ "$RESPONSE" = "302" ] || [ "$RESPONSE" = "301" ]; then
    echo "✅ Homepage accessible (HTTP $RESPONSE redirect)"
else
    echo "❌ Homepage failed with HTTP $RESPONSE"
    exit 1
fi

# Test 3: Database connectivity (via admin login page)
echo "Test 3: Database connectivity..."
ADMIN_URL="${URL}/admin/login/"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$ADMIN_URL")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ Database connectivity confirmed (admin page loads)"
else
    echo "⚠️  Admin page returned HTTP $RESPONSE (may be expected if admin disabled)"
fi

# Test 4: Static files serving
echo "Test 4: Static files serving..."
STATIC_URL="${URL}/static/img/brand/logo.png"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$STATIC_URL" || echo "000")
if [ "$RESPONSE" = "200" ] || [ "$RESPONSE" = "304" ]; then
    echo "✅ Static files serving correctly"
else
    echo "⚠️  Static file test returned HTTP $RESPONSE (check static configuration)"
fi

echo "================================================"
echo "✅ Smoke tests completed successfully"
echo "Deployment to $URL is healthy"
exit 0
