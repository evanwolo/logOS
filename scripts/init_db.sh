#!/bin/bash
# Initialize LogOS database and schema
# Usage: ./scripts/init_db.sh

set -e

DB_HOST="${LOGOS_DB_HOST:-localhost}"
DB_PORT="${LOGOS_DB_PORT:-5432}"
DB_NAME="${LOGOS_DB_NAME:-logos}"
DB_USER="${LOGOS_DB_USER:-logos}"
DB_PASSWORD="${LOGOS_DB_PASSWORD:-}"

echo "Initializing LogOS database..."
echo "Host: $DB_HOST"
echo "Port: $DB_PORT"
echo "Database: $DB_NAME"
echo "User: $DB_USER"

# Create database if not exists
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" postgres <<EOF
CREATE DATABASE IF NOT EXISTS "$DB_NAME";
EOF

# Apply schema
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" < schema.sql

echo "Database initialized successfully."
