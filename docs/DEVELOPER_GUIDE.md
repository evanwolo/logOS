# Developer Guide

## Project Structure

```
logOS/
│
├─ DOCUMENTATION.md               ← Documentation index
├─ README.md                      ← Project overview & Quickstart
├─ docs/                          ← Detailed documentation
│  ├─ ARCHITECTURE.md             ← System architecture & design
│  ├─ DEVELOPER_GUIDE.md          ← This file
│  └─ archive/                    ← Historical phase documents
│
├─ Core Application
│  ├─ logos/
│  │  ├─ __init__.py              ← Package definition
│  │  ├─ __main__.py              ← Entry point (python -m logos)
│  │  ├─ cli.py                   ← Command interface (argparse)
│  │  ├─ db.py                    ← Database access (no ORM)
│  │  ├─ mutations.py             ← Write-path operations (Phase 4)
│  │  └─ alignment.py             ← FROZEN state machine
│  │
│  └─ tests/
│     ├─ __init__.py
│     └─ test_health.py           ← Health command tests
│
├─ Database
│  ├─ schema.sql                  ← Schema definition
│  ├─ schema-init.sql             ← Initial data population
│  └─ scripts/
│     └─ init_db.sh               ← Database initialization script
│
├─ Docker Infrastructure
│  ├─ Dockerfile                  ← LogOS container definition
│  ├─ docker-compose.yml          ← PostgreSQL + LogOS orchestration
│  ├─ entrypoint.sh               ← Container entry point
│  └─ run.sh                      ← Convenience script
```

## Key Principles (Non-negotiable)

1. **Alignment is frozen.** Do not alter `calculate_system_state()` without explicit instruction.
2. **Fail loudly.** Missing invariants cause hard failures, not silent defaults.
3. **Explicit over clever.** Prefer readability and traceability over DRY abstractions.
4. **CLI is truth.** All observability flows through the command-line interface.

## Development Workflow

### Running Tests

```bash
# All tests
python3 run_tests.py

# In Docker (clean environment)
docker-compose run --rm logos python3 run_tests.py

# Individual test file
python3 -m pytest tests/test_health.py -v
```

### Database Inspection

```bash
# With Docker Compose running:
docker-compose exec postgres psql -U logos -d logos

# Queries:
SELECT * FROM daily_state;
SELECT * FROM liturgical_calendar;
SELECT COUNT(*) FROM hamartia_log WHERE confessed = FALSE;
SELECT * FROM system_health_today;
```

## Adding a New Command

### 1. Add handler in `logos/cli.py`

```python
def cmd_new_command(args):
    """
    new-command — Brief description.
    
    Reads from database, computes result, outputs.
    No mutation (unless clearly Phase 4+). 
    """
    data = fetch_something_from_db()
    result = process_data(data)
    print(format_output(result))
    return exit_code
```

### 2. Register in `main()` argument parser

```python
parser_new = subparsers.add_parser(
    "new-command",
    help="Brief help text"
)
parser_new.set_defaults(func=cmd_new_command)
```

### 3. Write tests

```python
def test_new_command():
    with patch("logos.cli.fetch_something_from_db") as mock:
        mock.return_value = {...}
        result = cmd_new_command(None)
        assert result == expected
```

## Code Patterns

### Database Query Template

```python
def fetch_something(date):
    """
    Read something from the database.
    
    Raises:
        SystemExit: If query fails or data missing
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT ... FROM ... WHERE date = %s;", (date,))
        row = cur.fetchone()
        if not row:
            print("error: expected data not found", flush=True)
            raise SystemExit(1)
        return {"field": row[0]}
    except psycopg2.Error as e:
        print(f"error: query failed: {e}", flush=True)
        raise SystemExit(1)
    finally:
        cur.close()
        conn.close()
```

### Common Mistakes (Don't Do This)

❌ **Adding features to `calculate_system_state()`**
- It's frozen. Make a new alignment function if needed.

❌ **Silent defaults for missing data**
- BAD: `fast_type = data.get("fast_type", "regular")`
- GOOD: Raise SystemExit if data is missing.

❌ **Using decorators or metaclasses**
- Keep it simple and explicit.

❌ **Using ORMs**
- Explicit SQL only.

## Environment Variables

```bash
LOGOS_DB_HOST       # PostgreSQL host (default: localhost)
LOGOS_DB_PORT       # PostgreSQL port (default: 5432)
LOGOS_DB_NAME       # Database name (default: logos)
LOGOS_DB_USER       # Database user (default: logos)
LOGOS_DB_PASSWORD   # Database password (default: empty)
```

## Exit Codes

- `0`: STABLE (success)
- `1`: DEGRADED (warning)
- `2`: CRITICAL (error)
