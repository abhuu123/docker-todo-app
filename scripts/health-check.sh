#!/usr/bin/env bash
set -euo pipefail
URL="${1:-http://localhost/health}"
for i in {1..20}; do curl --fail --silent --show-error "$URL" >/dev/null && { echo "Health check passed."; exit 0; }; echo "Waiting... $i/20"; sleep 5; done
echo "Health check failed."; exit 1
