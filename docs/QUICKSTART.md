# Quick Start

## Option 1: Docker Compose (Easiest)

```bash
cd /home/evan/Code/logOS

# Start everything
docker-compose up

# Expected output:
# ● System: STABLE
# [with current date's stats]
```

The Docker Compose setup:
1. Starts PostgreSQL with initialized schema
2. Builds LogOS container
3. Runs `logos health` command

Everything is self-contained. No local database setup needed.

## Option 2: Convenience Script

```bash
cd /home/evan/Code/logOS

# Make it executable
chmod +x run.sh

# Run health check
./run.sh

# Run with cleanup
./run.sh health && docker-compose down
```

## Option 3: Manual Local Setup

**Prerequisites:** Python 3.9+, PostgreSQL 12+, psycopg2

```bash
cd /home/evan/Code/logOS

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export LOGOS_DB_HOST=localhost
export LOGOS_DB_PORT=5432
export LOGOS_DB_NAME=logos
export LOGOS_DB_USER=logos
export LOGOS_DB_PASSWORD=yourpassword

# Initialize database
bash scripts/init_db.sh

# Run health check
python3 -m logos health
```

## Running Tests

```bash
# With Docker (no local dependencies)
docker-compose run --rm logos python3 run_tests.py

# Locally (requires dependencies installed)
python3 run_tests.py
```

## Project Structure

```
logOS/
├── logos/                  # Main package
│   ├── alignment.py       # FROZEN state machine logic
│   ├── mutations.py       # Write-path operations (Phase 4)
│   ├── cli.py             # Command-line interface
│   ├── db.py              # Database access (no ORM)
│   └── __main__.py        # Entry point
├── tests/                 # Test suite
│   └── test_health.py     # health command tests
├── schema.sql             # Database schema
├── schema-init.sql        # Initial data
├── docker-compose.yml     # Docker orchestration
├── Dockerfile             # LogOS container definition
├── requirements.txt       # Python dependencies
└── README.md              # Full documentation
```

## Key Files Explained

| File | Purpose |
|------|---------|
| `logos/alignment.py` | **FROZEN** state calculation. Do not modify. |
| `logos/mutations.py` | Write-path operations with strict constraints (Phase 4). |
| `logos/db.py` | Reads from PostgreSQL without ORM or implicit state. |
| `logos/cli.py` | Command dispatcher and output formatting. |
| `schema.sql` | Append-only tables, read-only views. |
| `docker-compose.yml` | PostgreSQL + LogOS orchestration. |

## What to Know

1. **Append-only hamartia.** Once logged, sins cannot be deleted. Only `confessed` state transition.
2. **Today-only mutations.** You cannot edit yesterday's daily_state.
3. **Fails loudly.** Missing invariants cause hard failures, not silent defaults.
4. **No scores.** State is STABLE/DEGRADED/CRITICAL only.
5. **Aligned with truth.** System health is computed, never stored.

## Troubleshooting

### "database connection failed"
- **With Docker:** Make sure postgres service started. Check `docker-compose logs postgres`.
- **Locally:** PostgreSQL not running. Start it: `sudo systemctl start postgresql`.

### "no daily state found for today"
- Database initialized but no row for today. This is expected on first run.
- Docker setup handles this automatically via `schema-init.sql`.
- Local setup: Add manually or have Phase 4 commands do it.

### "no liturgical context for today"
- Liturgical calendar table is empty. Upstream truth missing.
- Docker setup initializes with `fast_type='regular'` for today.

## Next Steps

- Read [PHASE4_COMPLETE.md](PHASE4_COMPLETE.md) for mutation constraints
- Read [PHASE3_COMPLETE.md](PHASE3_COMPLETE.md) for observability system
- Review [Copilot Constraints](.github/copilot-instructions.md)
- Check [Forbidden Suggestions](docs/copilot_do_not_suggest.md)

## Exit Codes

- **0 (STABLE):** System health is good
- **1 (DEGRADED):** One or more systems degraded
- **2 (CRITICAL):** System health compromised

Use in scripts: `logos health && echo "healthy" || echo "system issues"`
