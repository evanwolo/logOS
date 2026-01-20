# GitHub Copilot – Project Instructions

This repository implements **LogOS**, a CLI-first system with a fixed metaphysical model. Copilot must follow these constraints strictly.

## 1. Architectural Authority

* The CLI is the canonical interface. Web UI, if any, is secondary and read-only.
* System health is *derived*, never stored.
* The alignment logic (`calculate_system_state`) is frozen and must not be altered without explicit instruction.
* Prefer explicit, boring code over abstractions, ORMs, or frameworks.

## 2. Data Integrity Rules

* PostgreSQL is the source of truth.
* `hamartia_log` is append-only. Never delete rows. Never edit descriptions or passions.
* Confession is the only allowed state transition (`confessed=false → true` with timestamp).
* `unconfessed_count` is a raw count. No decay. No weighting. No optimization.
* `daily_state` uses lazy initialization via upsert on `date`.

## 3. Coding Style

* Python: standard library first. No "clever" patterns.
* No implicit magic (decorators, metaprogramming, hidden state).
* Functions should be small, deterministic, and auditable.
* Prefer clarity over DRY if it improves traceability.

## 4. CLI Semantics

* Commands must fail loudly if invariants are missing (e.g., empty `liturgical_context`).
* No gamification, scores, streaks, badges, or dopamine mechanics.
* Outputs should resemble system tools (`systemctl`, `git status`), not apps.
* Language must be diagnostic, not motivational or therapeutic.

## 5. External Interfaces

* The only external network dependency is the liturgical calendar sync.
* Calendar data is upstream truth and must not be user-editable.
* Unknown or ambiguous fasting rules must default to stricter interpretations.

## 6. What NOT to Do

* Do not introduce percentages, normalized scores, or ML-style weighting.
* Do not auto-resolve sins, smooth metrics, or "help" the user look better.
* Do not refactor the schema for convenience.
* Do not add UI polish at the expense of constraint.

## 7. Design Principle

When uncertain, choose the option that:

* Preserves invariants
* Increases friction
* Reduces optimization
* Forces explicit intent

If a change would make the system more pleasant but less truthful, reject it.
