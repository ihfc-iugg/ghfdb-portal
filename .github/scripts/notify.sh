#!/bin/bash
# Notification helper script for Slack/Discord webhooks
# Usage: ./notify.sh <webhook_url> <status> <message> [details...]
# Example: ./notify.sh "$SLACK_WEBHOOK" "success" "Deployment to staging" "commit: abc123, by: user"

set -e

WEBHOOK_URL="${1}"
STATUS="${2}"
MESSAGE="${3}"
DETAILS="${4:-}"

if [ -z "$WEBHOOK_URL" ] || [ -z "$STATUS" ] || [ -z "$MESSAGE" ]; then
    echo "Error: Missing required arguments"
    echo "Usage: $0 <webhook_url> <status> <message> [details]"
    exit 1
fi

# Determine color and emoji based on status
case "$STATUS" in
    success)
        COLOR="#36a64f"
        EMOJI="✅"
        ;;
    failure)
        COLOR="#ff0000"
        EMOJI="❌"
        ;;
    warning)
        COLOR="#ffcc00"
        EMOJI="⚠️"
        ;;
    info)
        COLOR="#0099cc"
        EMOJI="ℹ️"
        ;;
    *)
        COLOR="#808080"
        EMOJI="📌"
        ;;
esac

# Build JSON payload for Slack
PAYLOAD=$(cat <<EOF
{
    "attachments": [
        {
            "color": "$COLOR",
            "title": "$EMOJI $MESSAGE",
            "text": "$DETAILS",
            "footer": "GitHub Actions CI/CD",
            "ts": $(date +%s)
        }
    ]
}
EOF
)

# Send notification
echo "Sending notification to webhook..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "$PAYLOAD" "$WEBHOOK_URL")

if [ "$RESPONSE" = "200" ]; then
    echo "✅ Notification sent successfully"
    exit 0
else
    echo "⚠️  Notification failed with HTTP $RESPONSE (continuing anyway)"
    exit 0  # Don't fail the build if notification fails
fi
