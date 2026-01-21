# LogOS — Metaphysical Truth Engine

A CLI-first system for tracking ascetic practice and sin with fixed metaphysics.

## Current Status

✅ **Phase 3 Complete:** Read-only observability (`logos health`)  
✅ **Phase 4 Complete:** Write-path mutations (`logos log add`, `logos ascetic`)

See [PHASE3_COMPLETE.md](PHASE3_COMPLETE.md) and [PHASE4_COMPLETE.md](PHASE4_COMPLETE.md) for details.

## Core Commands

### Read System State

```bash
logos health          # Show current system state + exit code
```

### Log Hamartia (Append-Only)

```bash
logos log add                                  # Interactive
logos log add --passion Lust --description "..." # CLI
logos log confess                              # Mark as confessed
```

### Record Daily Practice (Today Only)

```bash
logos ascetic fast --kept         # Set fasting status
logos ascetic pray --minutes 20   # Log prayer time
logos ascetic read --minutes 30   # Log reading time
logos ascetic screen --minutes 90 # Log screen time
logos ascetic status              # Show today's state
```

---

## Setup with Docker (Recommended)

### Prerequisites

- Docker
- Docker Compose

### Quick Start

```bash
docker-compose up
```

This will:

1. Start PostgreSQL 15
2. Initialize schema from `schema.sql`
3. Populate initial state from `schema-init.sql`
4. Build and run LogOS CLI
5. Execute `logos health`

### Manual Setup (Without Docker)

#### Prerequisites

- Python 3.9+
- PostgreSQL 12+

#### Installation

```bash
pip install -r requirements.txt
```

#### Database Initialization

Set environment variables:

```bash
export LOGOS_DB_HOST=localhost
export LOGOS_DB_PORT=5432
export LOGOS_DB_NAME=logos
export LOGOS_DB_USER=logos
export LOGOS_DB_PASSWORD=your_password
```

Then initialize the database:

```bash
bash scripts/init_db.sh
```

This creates:

- `liturgical_calendar` — Upstream truth (fast types, feasts)
- `hamartia_log` — Append-only sin record
- `daily_state` — Today's ascetic state
- `system_health_today` — Computed read-only view

## Usage

### Using Docker Compose (Recommended)

```bash
# Start services and run health check
docker-compose up

# Or use the convenience script
./run.sh

# Run with explicit command
./run.sh health
./run.sh log add --passion Anger --description "Road rage"
./run.sh ascetic fast --kept
```

Example output:

```
● System: STABLE

     Date: 2026-01-20
    Fasted: false
    Prayed: true
Fast Type: regular
   Prayer: 120 min
  Reading: 45 min
   Screen: 0 min

Unconfessed: 0 sin(s)
```

Exit codes:

- `0` — STABLE
- `1` — DEGRADED
- `2` — CRITICAL

### Running Tests

With Docker Compose:

```bash
docker-compose run --rm logos python3 run_tests.py
```

Or from command line (with local Python):

```bash
python3 run_tests.py
```

### Using the CLI Directly

In Docker container:

```bash
docker-compose exec logos python3 -m logos health
```

Locally (after setup):

```bash
python3 -m logos health
```

## Architecture

### Frozen Components

- **`calculate_system_state()`** — Alignment logic. Fixed metaphysics. Do not alter.
- **Schema** — Append-only hamartia_log. No deletion. No editing.

### Design Principles

1. **CLI is canonical** — All truth flows through the command line
2. **Health is derived** — No stored scores, percentages, or smoothing
3. **Fail loudly** — Missing invariants cause hard failure
4. **No mutation yet** — `health` is read-only. Mutation comes in Phase 4.

## Constraints (Copilot)

See [`.github/copilot-instructions.md`](.github/copilot-instructions.md) and [`docs/copilot_do_not_suggest.md`](docs/copilot_do_not_suggest.md).

Do not:

- Add gamification, scores, or rewards
- Introduce percentages or normalized metrics
- Add motivational language
- Cache or smooth system state
- Use ORMs or implicit state machines

If a change makes LogOS more pleasant but less truthful, reject it.

## Next Phase

Once `logos health` is correct and stable, Phase 4 will define write-path ordering:

- Which commands mutate which tables
- Temporal constraints on mutations
- Append-only enforcement for hamartia_log
- Confession state transitions

Until then, **no mutation commands exist**.
