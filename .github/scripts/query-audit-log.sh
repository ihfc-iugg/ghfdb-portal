#!/bin/bash
# Query GitHub Deployments API for audit log
# Usage: ./query-audit-log.sh [environment] [since-date] [deployer]
# Example: ./query-audit-log.sh production 2026-01-01 username

set -e

ENVIRONMENT="${1:-production}"
SINCE_DATE="${2:-}"
DEPLOYER="${3:-}"

# Requires GITHUB_TOKEN environment variable
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable not set"
    echo "Usage: GITHUB_TOKEN=ghp_xxx $0 [environment] [since-date] [deployer]"
    exit 1
fi

REPO="${GITHUB_REPOSITORY:-ihfc-iugg/global-heat-flow-database}"
API_URL="https://api.github.com"

echo "🔍 Querying deployment audit log..."
echo "Environment: $ENVIRONMENT"
[ -n "$SINCE_DATE" ] && echo "Since: $SINCE_DATE"
[ -n "$DEPLOYER" ] && echo "Deployer: $DEPLOYER"
echo "================================================"

# Query deployments
DEPLOYMENTS=$(curl -s \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "$API_URL/repos/$REPO/deployments?environment=$ENVIRONMENT&per_page=100")

# Parse and filter results
echo "$DEPLOYMENTS" | python3 -c "
import json
import sys
from datetime import datetime

try:
    deployments = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f'Error parsing JSON: {e}')
    sys.exit(1)

if not isinstance(deployments, list):
    print('Error: Expected list of deployments')
    if isinstance(deployments, dict) and 'message' in deployments:
        print(f'API Error: {deployments[\"message\"]}')
    sys.exit(1)

# Filter by date if provided
since_date = '$SINCE_DATE'
if since_date:
    since_dt = datetime.fromisoformat(since_date.replace('Z', '+00:00'))
    deployments = [d for d in deployments if datetime.fromisoformat(d['created_at'].replace('Z', '+00:00')) >= since_dt]

# Filter by deployer if provided
deployer = '$DEPLOYER'
if deployer:
    deployments = [d for d in deployments if d.get('creator', {}).get('login') == deployer]

# Print results
print(f'Found {len(deployments)} deployments')
print()

for dep in deployments[:20]:  # Limit to 20 most recent
    created = dep['created_at']
    sha = dep['sha'][:7]
    creator = dep.get('creator', {}).get('login', 'unknown')
    description = dep.get('description', 'N/A')
    print(f'{created} | {sha} | {creator} | {description}')
"

echo "================================================"
echo "Query complete"
