# Developer Reference

## Key Principles (Non-negotiable)

1. **Alignment is frozen.** Do not alter `calculate_system_state()` without explicit instruction.
2. **Fail loudly.** Missing invariants cause hard failures, not silent defaults.
3. **No mutation yet.** Phase 3 is read-only. Phase 4 will define write rules.
4. **Explicit over clever.** Prefer readability and traceability over DRY abstractions.
5. **CLI is truth.** All observability flows through the command-line interface.

## Command Structure

```
logos [COMMAND] [OPTIONS]

Commands:
  health              Display system health (implemented)
  [Phase 4]           Mutation commands (not yet)
```

## Adding a New Read-Only Command

### 1. Add handler in `logos/cli.py`

```python
def cmd_new_command(args):
    """
    new-command — Brief description.
    
    Reads from database, computes result, outputs.
    No mutation. No caching.
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

## Database Query Template

```python
def fetch_something(date):
    """
    Read something from the database.
    
    Raises:
        SystemExit: If query fails or data missing
        
    Returns:
        dict: Result data
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT ...
            FROM ...
            WHERE date = %s;
        """, (date,))
        
        row = cur.fetchone()
        if not row:
            print("error: expected data not found", flush=True)
            raise SystemExit(1)
        
        return {"field": row[0], ...}
        
    except psycopg2.Error as e:
        print(f"error: query failed: {e}", flush=True)
        raise SystemExit(1)
    finally:
        cur.close()
        conn.close()
```

## Output Formatting Template

```python
def format_output(data):
    """Format output in systemctl style."""
    lines = []
    lines.append(f"Status: {data['status']}")
    lines.append("")
    lines.append(f"  Field: {data['value']}")
    
    if data['status'] != "GOOD":
        lines.append("")
        lines.append("Warnings:")
        for warning in data['warnings']:
            lines.append(f"  - {warning}")
    
    return "\n".join(lines)
```

## Testing Template

```python
def test_something():
    """Test [what it tests]."""
    with patch("logos.db.fetch_x") as mock:
        mock.return_value = {"field": "value"}
        exit_code = cmd_something(None)
        assert exit_code == 0
        # or whatever the expected outcome is
```

## Running Tests

```bash
# All tests
python3 run_tests.py

# In Docker
docker-compose run --rm logos python3 run_tests.py

# Individual test file
python3 -m pytest tests/test_health.py -v
```

## Database Inspection

```bash
# With Docker Compose running:
docker-compose exec postgres psql -U logos -d logos

# Queries:
SELECT * FROM daily_state;
SELECT * FROM liturgical_calendar;
SELECT COUNT(*) FROM hamartia_log WHERE confessed = FALSE;
SELECT * FROM system_health_today;
```

## Environment Variables

```bash
LOGOS_DB_HOST       # PostgreSQL host (default: localhost)
LOGOS_DB_PORT       # PostgreSQL port (default: 5432)
LOGOS_DB_NAME       # Database name (default: logos)
LOGOS_DB_USER       # Database user (default: logos)
LOGOS_DB_PASSWORD   # Database password (default: empty)
```

## Exit Codes

```python
0  # STABLE (success)
1  # DEGRADED (warning)
2  # CRITICAL (error)
```

Use `sys.exit(code)` to set the return code.

## Common Mistakes (Don't Do This)

❌ **Adding features to `calculate_system_state()`**
- It's frozen. Make a new alignment function if needed.

❌ **Silent defaults for missing data**
```python
# BAD:
fast_type = data.get("fast_type", "regular")

# GOOD:
if data["fast_type"] is None:
    print("error: missing fast type", flush=True)
    raise SystemExit(1)
```

❌ **Using decorators or metaclasses**
```python
# BAD:
@cache
@validate
def my_function():
    ...

# GOOD:
def my_function():
    # Explicit code
```

❌ **Adding computed fields or scores**
```python
# BAD:
health_score = (prayer * 0.4) + (reading * 0.3) + (fasting * 0.3)

# GOOD:
state = calculate_system_state(daily_state, liturgical, unconfessed_count)
```

❌ **Storing derived data**
```python
# BAD:
UPDATE system_state SET computed_health = 'STABLE';

# GOOD:
SELECT CASE WHEN ... THEN 'STABLE' ...  -- Always computed from source
```

## File Editing Checklist

Before modifying any file:

- [ ] Does it change the frozen alignment logic? (If yes, stop.)
- [ ] Does it add mutation capability? (If yes, this is Phase 4+.)
- [ ] Does it fail loudly on missing data? (If no, fix it.)
- [ ] Does it use ORM, decorators, or implicit state? (If yes, simplify.)
- [ ] Are errors clear and diagnostic? (If not, improve them.)
- [ ] Is every line auditable and traceable? (If not, refactor.)

## Reading the Code

### Start here:
1. [QUICKSTART.md](QUICKSTART.md) — How to run it
2. [logos/cli.py](logos/cli.py) — Entry point and command structure
3. [logos/alignment.py](logos/alignment.py) — The state machine (frozen)
4. [logos/db.py](logos/db.py) — Database access
5. [schema.sql](schema.sql) — Data model

### Then read:
- [docs/phase3_read_only_observability.md](docs/phase3_read_only_observability.md) — Architecture
- [.github/copilot-instructions.md](.github/copilot-instructions.md) — Design principles
- [docs/copilot_do_not_suggest.md](docs/copilot_do_not_suggest.md) — Forbidden patterns

## Asking Questions

**"Can I add a score to system health?"**
No. State machine only: STABLE/DEGRADED/CRITICAL.

**"Can I smooth out fluctuations?"**
No. State is computed fresh every time.

**"Can I add a feature to speed things up?"**
Only if it doesn't change observable behavior. Test it.

**"Can I refactor this for readability?"**
Yes, if every line remains auditable.

**"Can I add mutation commands?"**
Not yet. That's Phase 4. For now, read-only.

**"Can I use SQLAlchemy?"**
No. Explicit SQL only. No ORM.

**"Can I add gamification?"**
No. See [docs/copilot_do_not_suggest.md](docs/copilot_do_not_suggest.md).

## Contact Points

If you're lost:
- Check [QUICKSTART.md](QUICKSTART.md)
- Check [PHASE3_CHECKLIST.md](PHASE3_CHECKLIST.md)
- Read the docstrings in the code
- Run the tests and read the output

If something is unclear, the code should clarify it. If it doesn't, that's a bug.
