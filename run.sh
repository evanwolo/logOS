#!/bin/bash
# Run LogOS with Docker Compose
# Usage: ./run.sh [command]
#   ./run.sh health     -- Check system health (default)
#   ./run.sh bash       -- Open shell in container

set -e

cd "$(dirname "$0")"

COMMAND="${1:-health}"

echo "Building LogOS containers..."
docker-compose build

echo "Starting services..."
docker-compose up -d

echo "Waiting for services to be ready..."
sleep 3

echo ""
echo "Running: logos $COMMAND"
echo "---"

docker-compose exec -T logos python3 -m logos "$COMMAND"

exit_code=$?

echo "---"
if [ "$exit_code" -eq 0 ]; then
  echo "✓ STABLE"
elif [ "$exit_code" -eq 1 ]; then
  echo "◐ DEGRADED"
elif [ "$exit_code" -eq 2 ]; then
  echo "✕ CRITICAL"
fi

exit $exit_code
