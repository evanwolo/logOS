# LogOS: Phase 3 Complete

**Date:** January 20, 2026  
**Status:** ✅ Phase 3 (Read-Only Observability) Complete

---

## Executive Summary

Phase 3 implements the **minimal executable kernel** of LogOS: the `logos health` command. This is a read-only diagnostic tool that:

- Reads system truth from PostgreSQL
- Evaluates health using a frozen state machine
- Outputs in systemctl style
- Fails loudly on missing invariants
- Returns exit codes: 0 (STABLE), 1 (DEGRADED), 2 (CRITICAL)

**No mutation.** No caching. No optimization. Pure observability.

---

## What Was Built

### Core Executable

```bash
logos health
```

This command:
1. **Reads** from `system_health_today` database view
2. **Validates** that invariants are present (daily_state, liturgical context)
3. **Evaluates** using `calculate_system_state()` (frozen logic)
4. **Outputs** in systemctl style with warnings
5. **Returns** exit code reflecting state

### Example Output

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

### Data Flow

```
PostgreSQL
    ↓
system_health_today (read-only view)
    ↓
fetch_system_health_today() [logos/db.py]
    ↓
calculate_system_state() [logos/alignment.py] — FROZEN
    ↓
format_health_output() [logos/cli.py]
    ↓
stdout + exit code
```

---

## Architecture

### Components

| Component | File | Purpose |
|-----------|------|---------|
| **CLI** | `logos/cli.py` | Argument parsing, command dispatch, output formatting |
| **Database** | `logos/db.py` | PostgreSQL access (no ORM), connection mgmt, validation |
| **Alignment** | `logos/alignment.py` | State machine (FROZEN) |
| **Entry Point** | `logos/__main__.py` | Allows `python -m logos health` |
| **Package Init** | `logos/__init__.py` | Package definition |

### Database Schema

| Table | Purpose |
|-------|---------|
| `liturgical_calendar` | Upstream truth: fast types, feasts |
| `daily_state` | Today's ascetic data: prayer, reading, screen, fasting |
| `hamartia_log` | Append-only sin record (append-only, never edit) |
| `system_health_today` | Read-only view: combines all data for health check |

### Docker Infrastructure

| File | Purpose |
|------|---------|
| `Dockerfile` | Container definition for LogOS |
| `docker-compose.yml` | Orchestrates PostgreSQL + LogOS |
| `entrypoint.sh` | Waits for DB, runs command |
| `schema.sql` | Creates all tables and views |
| `schema-init.sql` | Populates initial state |

---

## How to Use

### Quick Start (Docker)

```bash
cd /home/evan/Code/logOS
docker-compose up
```

### Convenience Script

```bash
./run.sh
./run.sh health
```

### Local Setup

```bash
pip install -r requirements.txt
export LOGOS_DB_HOST=localhost LOGOS_DB_PORT=5432 \
       LOGOS_DB_NAME=logos LOGOS_DB_USER=logos
bash scripts/init_db.sh
python3 -m logos health
```

### Running Tests

```bash
# Docker
docker-compose run --rm logos python3 run_tests.py

# Local
python3 run_tests.py
```

---

## Alignment Logic (Frozen)

The `calculate_system_state()` function is authoritative and must not be altered:

### 1. Hamartia Buffer Check
- **If:** unconfessed_count ≥ 5
- **Then:** CRITICAL
- **Why:** Too much unresolved sin destabilizes the system

### 2. Ascetic Integrity Check
- **If:** fast_type = 'strict' AND fasted = FALSE
- **Then:** CRITICAL
- **Why:** Explicit vow violations are critical failures

- **If:** prayed = FALSE
  - **And:** unconfessed_count > 0 → CRITICAL
  - **Else:** DEGRADED
  - **Why:** Missed prayer compounds existing sin

### 3. Signal/Noise Check
- **If:** noise > 0 AND (signal / noise) < 0.1
- **Then:** DEGRADED
- **Why:** Noise overwhelms ascetic practice

- **Special:** zero noise → STABLE (undefined ratio treated as perfect)

### 4. Default
- **Then:** STABLE
- **Why:** All critical checks passed

---

## Invariant Failures

The system **fails loudly** if upstream truth is missing:

```
error: no daily state found for today (missing invariant)
error: no liturgical context for today (missing invariant)
error: database connection failed: ...
```

This is **intentional**. The system is **self-aware of incompleteness**. There are no silent defaults.

---

## Exit Codes

| Code | State | Meaning |
|------|-------|---------|
| **0** | STABLE | All systems nominal |
| **1** | DEGRADED | One or more systems degraded |
| **2** | CRITICAL | System health compromised |

Use in scripts:
```bash
if logos health; then
  echo "System is healthy"
else
  echo "System needs attention (exit code: $?)"
fi
```

---

## What Is NOT in Phase 3

✅ **Read-only observability only.**

❌ No write commands (`logos log add`, `logos confess`, etc.)  
❌ No mutation of hamartia_log  
❌ No confession state transitions  
❌ No liturgical calendar sync  
❌ No time decay or forgiveness  
❌ No gamification or scoring  
❌ No ORM or implicit state  

**Everything that mutates comes in Phase 4.**

---

## Documentation

### User-Facing

- **[QUICKSTART.md](QUICKSTART.md)** — Getting started guide
- **[README.md](README.md)** — Full project overview
- **[DEVELOPER_REFERENCE.md](DEVELOPER_REFERENCE.md)** — Code patterns and templates

### Design & Architecture

- **[docs/phase3_read_only_observability.md](docs/phase3_read_only_observability.md)** — Phase 3 deep dive
- **[PHASE3_CHECKLIST.md](PHASE3_CHECKLIST.md)** — Detailed implementation checklist

### Constraints (Copilot)

- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** — Project principles
- **[.copilot/config.json](.copilot/config.json)** — Guardrails and blocklists
- **[docs/copilot_do_not_suggest.md](docs/copilot_do_not_suggest.md)** — Forbidden patterns

---

## Test Coverage

All alignment logic tested:

| Scenario | Expected | Status |
|----------|----------|--------|
| Perfect state (stable) | STABLE | ✅ |
| 5+ unconfessed sins | CRITICAL | ✅ |
| Strict fast violated | CRITICAL | ✅ |
| Prayer missed + sin | CRITICAL | ✅ |
| Prayer missed alone | DEGRADED | ✅ |
| High noise ratio | DEGRADED | ✅ |
| Zero noise | STABLE | ✅ |
| Output formatting | Correct | ✅ |
| Exit codes | 0/1/2 | ✅ |
| Missing invariants | Hard fail | ✅ |

Run tests: `python3 run_tests.py`

---

## File Structure

```
logOS/
├── QUICKSTART.md                        # Getting started
├── README.md                            # Full documentation
├── DEVELOPER_REFERENCE.md               # Code patterns
├── PHASE3_CHECKLIST.md                  # Implementation checklist
│
├── logos/                               # Main package
│   ├── __init__.py
│   ├── __main__.py                      # Entry point (python -m logos)
│   ├── cli.py                           # Command interface
│   ├── db.py                            # Database access
│   └── alignment.py                     # FROZEN state machine
│
├── tests/                               # Test suite
│   ├── __init__.py
│   └── test_health.py                   # health command tests
│
├── docker-compose.yml                   # Orchestration
├── Dockerfile                           # Container definition
├── entrypoint.sh                        # Container entry point
├── run.sh                               # Convenience script
├── run_tests.py                         # Test runner
│
├── schema.sql                           # Database schema
├── schema-init.sql                      # Initial data
├── requirements.txt                     # Python dependencies
│
├── .copilot/
│   └── config.json                      # Copilot guardrails
│
├── .github/
│   └── copilot-instructions.md          # Project principles
│
├── docs/
│   ├── copilot_do_not_suggest.md        # Forbidden patterns
│   └── phase3_read_only_observability.md # Phase 3 details
│
└── scripts/
    └── init_db.sh                       # DB initialization
```

---

## Verification Checklist

### Functional
- ✅ `logos health` reads from database
- ✅ Produces deterministic output
- ✅ Fails loudly on missing invariants
- ✅ Alignment logic frozen and documented
- ✅ Exit codes correct (0/1/2)
- ✅ Zero mutation capability
- ✅ All tests passing

### Non-Functional
- ✅ No ORM (explicit SQL only)
- ✅ No hidden state or implicit magic
- ✅ Standard library first (psycopg2 only)
- ✅ Comprehensive error messages
- ✅ Docker working
- ✅ Python files syntax-valid

### Documentation
- ✅ User guides
- ✅ Developer constraints
- ✅ Architecture documentation
- ✅ Code patterns and templates
- ✅ Example outputs
- ✅ Exit code meanings

---

## Key Design Decisions

### 1. Frozen Alignment Logic
`calculate_system_state()` is locked by design. The state machine is:
- Authoritative
- Unarguable
- Immune to "helpful" drift
- Metaphysically significant (order of checks matters)

### 2. Explicit SQL (No ORM)
- Every database interaction visible
- No implicit migrations
- No hidden state
- Easy to audit

### 3. Loud Failure
- Missing invariants → SystemExit
- No silent defaults
- No "helpfulness"
- System knows when it's incomplete

### 4. Systemctl Style Output
- Familiar to Unix operators
- Diagnostic, not therapeutic
- Clear status symbols (● ◐ ✕)
- Warnings only for non-stable states

### 5. Docker-First Deployment
- Eliminates environment variance
- PostgreSQL included
- Schema and initial state automated
- Single command: `docker-compose up`

---

## Next Phase (Phase 4)

Once Phase 3 is approved, Phase 4 will add **write-path ordering**:

- Which commands can mutate what tables
- Temporal constraints (when mutations allowed)
- Confession state transitions (`confessed=false → true`)
- Append-only enforcement for `hamartia_log`
- Daily state initialization and updates

**But:** The nervous system is complete. The observability layer is locked. Everything else is muscle.

---

## Support

**Getting Started?** → [QUICKSTART.md](QUICKSTART.md)  
**Want to contribute?** → [DEVELOPER_REFERENCE.md](DEVELOPER_REFERENCE.md)  
**Need details?** → [PHASE3_CHECKLIST.md](PHASE3_CHECKLIST.md)  
**Design philosophy?** → [.github/copilot-instructions.md](.github/copilot-instructions.md)  

---

## Summary

Phase 3 delivers a **read-only, diagnostic nervous system** for LogOS:

- `logos health` is the minimal executable
- Pure observability, zero mutation
- Frozen alignment logic
- Loud failure on invariants
- Complete test coverage
- Full Docker support
- Comprehensive documentation

The system can **see truth**. It just can't act on it yet.

**Status: ✅ Ready for Phase 4**
