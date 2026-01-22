#!/bin/bash
# Run LogOS with Docker Compose
# Usage: ./run.sh [command]
#   ./run.sh health          -- Check system health (default)
#   ./run.sh log add ...     -- Run specific command
#   ./run.sh bash            -- Open shell

set -e

cd "$(dirname "$0")"

# Default command is "health" if no args provided
if [ $# -eq 0 ]; then
    CMD=( "health" )
else
    CMD=( "$@" )
fi

# Ensure Postgres is running
echo "Checking background services..."
docker-compose up -d postgres

# Wait for Postgres health (timeout 30s)
echo -n "Waiting for database..."
for i in {1..30}; do
    if docker-compose ps postgres | grep -q "healthy"; then
        echo " ready."
        break
    fi
    echo -n "."
    sleep 1
done

echo ""
echo "Running: logos ${CMD[*]}"
echo "---"

# Run ephemeral container
# We use "${CMD[@]}" to preserve quoted arguments
docker-compose run --rm logos python3 -m logos "${CMD[@]}"

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
