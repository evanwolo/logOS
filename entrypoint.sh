#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! pg_isready -h "${LOGOS_DB_HOST}" -p "${LOGOS_DB_PORT}" -U "${LOGOS_DB_USER}" > /dev/null 2>&1; do
  sleep 1
done


# Initialize DB if needed (migrates schema)
python3 scripts/migrate_v4.py

# Populate liturgical calendar (Ortho-fix)
python3 scripts/populate_liturgical_calendar.py

echo "PostgreSQL is ready"

# Run the health command
exec python3 -m logos "$@"
