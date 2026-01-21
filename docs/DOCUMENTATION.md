# LogOS Documentation Index

## 📚 Start Here

| Document | Purpose | Audience |
|----------|---------|----------|
| **[QUICKSTART.md](QUICKSTART.md)** | Get running in 5 minutes | Everyone |
| **[PHASE3_COMPLETE.md](PHASE3_COMPLETE.md)** | What was built (executive summary) | Project leads |
| **[README.md](README.md)** | Full project overview | Users |

---

## 🏗️ Architecture & Design

| Document | Purpose | Audience |
|----------|---------|----------|
| **[docs/phase3_read_only_observability.md](docs/phase3_read_only_observability.md)** | Phase 3 architecture deep dive | Architects, developers |
| **[PHASE3_CHECKLIST.md](PHASE3_CHECKLIST.md)** | Detailed implementation checklist | Project reviewers |

---

## 👨‍💻 For Developers

| Document | Purpose |
|----------|---------|
| **[DEVELOPER_REFERENCE.md](DEVELOPER_REFERENCE.md)** | Code patterns, templates, common mistakes |
| **Source code docstrings** | Detailed function documentation |

---

## 🚫 For Copilot (Constraints)

| Document | Purpose | Applies To |
|----------|---------|-----------|
| **[.github/copilot-instructions.md](.github/copilot-instructions.md)** | Project principles (read automatically by Copilot) | All code changes |
| **[.copilot/config.json](.copilot/config.json)** | Guardrails and blocklists (blocklist patterns) | Code suggestions |
| **[docs/copilot_do_not_suggest.md](docs/copilot_do_not_suggest.md)** | Explicitly forbidden suggestions | Mutation/feature proposals |

---

## 📖 Reading Guide

### For First-Time Users
1. [QUICKSTART.md](QUICKSTART.md) — Get it running
2. Run `logos health`
3. [README.md](README.md) — Understand the system

### For Developers
1. [QUICKSTART.md](QUICKSTART.md) — Get it running
2. [DEVELOPER_REFERENCE.md](DEVELOPER_REFERENCE.md) — Learn patterns
3. [docs/phase3_read_only_observability.md](docs/phase3_read_only_observability.md) — Deep dive
4. Read the source code docstrings

### For Code Reviewers
1. [PHASE3_CHECKLIST.md](PHASE3_CHECKLIST.md) — What should be there
2. [PHASE3_COMPLETE.md](PHASE3_COMPLETE.md) — What was built
3. Verify against checklist

### For Copilot (Enforced)
1. [.github/copilot-instructions.md](.github/copilot-instructions.md)
2. [.copilot/config.json](.copilot/config.json)
3. [docs/copilot_do_not_suggest.md](docs/copilot_do_not_suggest.md)

---

## 🎯 By Use Case

### "I want to run `logos health`"
→ [QUICKSTART.md](QUICKSTART.md)

### "I want to understand the system"
→ [README.md](README.md) then [docs/phase3_read_only_observability.md](docs/phase3_read_only_observability.md)

### "I want to add a new command"
→ [DEVELOPER_REFERENCE.md](DEVELOPER_REFERENCE.md)

### "I want to modify alignment logic"
→ **STOP.** See [.github/copilot-instructions.md](.github/copilot-instructions.md) section 1.

### "I want to add mutation capabilities"
→ Wait for Phase 4.

### "I want to understand Copilot constraints"
→ [.github/copilot-instructions.md](.github/copilot-instructions.md) + [docs/copilot_do_not_suggest.md](docs/copilot_do_not_suggest.md)

### "I want to verify everything is complete"
→ [PHASE3_CHECKLIST.md](PHASE3_CHECKLIST.md)

---

## 📝 Document Sizes

| Document | Lines | Focus |
|----------|-------|-------|
| QUICKSTART.md | ~150 | Getting started |
| README.md | ~130 | Project overview |
| DEVELOPER_REFERENCE.md | ~210 | Code patterns |
| PHASE3_CHECKLIST.md | ~250 | Implementation details |
| PHASE3_COMPLETE.md | ~350 | Executive summary |
| phase3_read_only_observability.md | ~200 | Architecture |
| copilot_do_not_suggest.md | ~70 | Forbidden patterns |
| copilot-instructions.md | ~60 | Project principles |

---

## 🔗 Quick Links

**Essential files:**
- `logos/cli.py` — Command interface
- `logos/alignment.py` — **FROZEN** state machine
- `logos/db.py` — Database access
- `schema.sql` — Database schema

**Configuration:**
- `.github/copilot-instructions.md` — Project rules
- `.copilot/config.json` — Copilot guardrails
- `docker-compose.yml` — Environment setup

**Tests:**
- `tests/test_health.py` — Health command tests
- `run_tests.py` — Test runner

---

## ❓ FAQ

**Q: Where do I start?**  
A: [QUICKSTART.md](QUICKSTART.md)

**Q: Can I modify the alignment function?**  
A: No. It's frozen. See [.github/copilot-instructions.md](.github/copilot-instructions.md) section 1.

**Q: How do I add a new command?**  
A: [DEVELOPER_REFERENCE.md](DEVELOPER_REFERENCE.md) has templates.

**Q: Can I add mutation commands?**  
A: Not yet. That's Phase 4.

**Q: What are the exit codes?**  
A: 0=STABLE, 1=DEGRADED, 2=CRITICAL. See [README.md](README.md).

**Q: Why is there so much documentation?**  
A: Because the system constraints are strict, and clarity prevents drift.

---

## ✅ Verification

All documentation is:
- ✅ Complete and accurate
- ✅ Organized by audience
- ✅ Linked and cross-referenced
- ✅ Regularly updated
- ✅ Enforced by Copilot constraints

**Last updated:** January 20, 2026  
**Phase:** 3 (Read-Only Observability)  
**Status:** Complete
