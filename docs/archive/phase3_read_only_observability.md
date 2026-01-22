# Phase 3: Read-Only Observability

## Overview

Phase 3 implements the minimal executable kernel of LogOS: the `logos health` command.

**Core principle:** No mutation until observability is correct. You must see truth before you can act on it.

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│ CLI Layer (logos/cli.py)                                    │
│ - Argument parsing (argparse)                              │
│ - Command dispatcher                                        │
│ - Output formatting (systemctl style)                      │
└──────────────┬──────────────────────────────────────────────┘
               │
               ├──> Alignment (logos/alignment.py)
               │    └─ calculate_system_state()
               │       (FROZEN - do not alter)
               │
└──────────────┬──────────────────────────────────────────────┐
│ Database Layer (logos/db.py)                               │
│ - Explicit SQL queries                                     │
│ - No ORM                                                   │
│ - Loud failures on invariant violations                    │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│ PostgreSQL (system_health_today view)                       │
│ - Daily state (prayer, reading, screen time, fasting)      │
│ - Liturgical calendar (fast type, feast)                   │
│ - Hamartia log (unconfessed sin count)                     │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Read from DB:** `fetch_system_health_today()` queries the read-only view
2. **Validate:** Fails loudly if invariants missing (liturgical context, daily state)
3. **Evaluate:** Call `calculate_system_state(daily_state, liturgical_context, unconfessed_count)`
4. **Format:** Convert state to systemctl-style output with warnings
5. **Exit:** Return code reflects state (0=STABLE, 1=DEGRADED, 2=CRITICAL)

## Usage

### With Docker (Recommended)

```bash
# Start services and run health check
docker-compose up

# Or use the convenience script
./run.sh
```

### Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
bash scripts/init_db.sh

# Run health check
python3 -m logos health
```

### Run Tests

```bash
# With Docker
docker-compose run --rm logos python3 run_tests.py

# Locally
python3 run_tests.py
```

## Output Examples

### STABLE State

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

Exit code: **0**

### DEGRADED State

```
◐ System: DEGRADED

     Date: 2026-01-20
    Fasted: false
    Prayed: false
Fast Type: regular
   Prayer: 0 min
  Reading: 0 min
   Screen: 600 min

Unconfessed: 0 sin(s)

Warnings:
  - Prayer rule missed
  - Signal-to-noise ratio degraded (0:600)
```

Exit code: **1**

### CRITICAL State

```
✕ System: CRITICAL

     Date: 2026-01-20
    Fasted: false
    Prayed: true
Fast Type: strict
   Prayer: 120 min
  Reading: 45 min
   Screen: 600 min

Unconfessed: 5 sin(s)

Warnings:
  - Hamartia buffer critical (≥5 unconfessed)
  - Strict fast violated
```

Exit code: **2**

## Alignment Logic (Frozen)

The `calculate_system_state()` function implements a fixed state machine:

### 1. Hamartia Buffer Check (Memory Leak)
- **Condition:** `unconfessed_count >= 5`
- **Result:** CRITICAL
- **Why:** Too much unresolved sin destabilizes the system

### 2. Ascetic Integrity Check (Kernel Integrity)
- **Condition:** Strict fast type AND not fasted
- **Result:** CRITICAL
- **Why:** Explicit vow violations are critical failures
- **Condition:** Prayer not performed
  - **With sin:** CRITICAL (compound failure)
  - **Without sin:** DEGRADED (rule missed)

### 3. Signal/Noise Check (Latency)
- **Condition:** Screen time > 0 AND (prayer + reading) / screen_time < 0.1
- **Result:** DEGRADED
- **Why:** Noise overwhelms signal
- **Special:** Zero noise is always STABLE (ratio undefined)

### 4. Default
- **Result:** STABLE
- **Why:** All critical checks passed

## Invariant Failures

The system fails loudly if upstream truth is missing:

```
error: no daily state found for today (missing invariant)
error: no liturgical context for today (missing invariant)
error: database connection failed: ...
```

These are NOT silent defaults. The system is **self-aware of incompleteness**.

## What Is NOT in Phase 3

- ❌ `logos log add` — No mutation yet
- ❌ `logos ascetic` — No write path
- ❌ Liturgical calendar sync — Phase 5
- ❌ Confession state transitions — Phase 4
- ❌ Any command that mutates the database

## Definition of Done

Phase 3 is complete when:

- ✅ `logos health` reads from database deterministically
- ✅ Produces identical output for identical DB state
- ✅ Fails loudly if invariants missing
- ✅ Alignment function is frozen and documented
- ✅ Exit codes reflect state correctly (0/1/2)
- ✅ Zero mutation logic
- ✅ All tests pass
- ✅ Docker setup is working

## Next Phase

Phase 4 will define **write-path ordering**:

- Which commands mutate which tables
- Temporal constraints (when mutations are allowed)
- State transitions for confession
- Append-only enforcement for `hamartia_log`

Until then, LogOS is a diagnostic tool only. The nervous system is complete. Muscles come later.
