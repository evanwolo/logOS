
# LogOS Docker Guide

This guide describes how to run LogOS in a containerized environment.

## Prerequisites

- Docker
- Docker Compose

## Quick Start

Use the provided helper script:

```bash
# Check system health (default)
./run.sh

# Add a sin log
./run.sh log add --passion Gluttony --description "Overate at dinner"

# Record confession
./run.sh log confess

# Update daily state (ascetic)
./run.sh ascetic pray --minutes 15
```

## Manual Usage

If you prefer `docker-compose` directly:

1. **Start the database:**
   ```bash
   docker-compose up -d postgres
   ```

2. **Run a command:**
   ```bash
   docker-compose run --rm logos health
   ```

## Database Initialization

- The database is persisted in the `logos_db` Docker volume.
- First run will initialize the schema from `schema.sql`.
- **Note:** If you have an existing volume from pre-Phase 4, you may need to wipe it to apply the new schema:
  
  ```bash
  docker-compose down -v
  docker-compose up -d postgres
  ```

  *Warning: This deletes all data.*

## Troubleshooting

- **"PostgreSQL is ready" hangs:** Check `docker-compose logs postgres`.
- **Schema mismatch:** If you see errors about missing columns (`prayer_interruptions` etc.), your volume is outdated. Run migration or wipe volume.
