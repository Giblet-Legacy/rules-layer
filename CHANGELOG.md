# CHANGELOG — rules-layer (P12 Rules)

CHANGELOG.md — build history for P12 Rules, latest entry at top.

## [Unreleased]

### Good

- (none)

### Bad

- (none)

### Ugly

- (none)

## [v3.0.0] — 2026-11-13 — FROZEN

### Good

- `SPEC_V3.md`, `test_rules_v3.py` (5 tests, run red first) and `rules_v3.py`: a declarative rule format that can live in a JSON file (the Echo's three matchers, adopted), validated fail-closed, compiled onto the v2 engine. `preview` runs through the real v2 engine with `dry_run=True`. 48/48 pass.
- Closes the gap where no two consumers could share a rule set and the Echo previewed "P12" without using P12.
- Built on James's delegation ("fix all 11 issues"). Frozen at 3.0.0 on James's sign-off ("freeze all", 2026-11-13).

### Bad

- Frozen on the laptop run alone (2026-11-13); the S24 run is still to be confirmed.

### Ugly

- Only three matchers exist (subject, face, object substring). Richer predicates need a later SPEC version; the loader refuses anything else rather than guess.

## [v2.0.0] — 2026-11-12

### Good
- Laptop audit against SPEC.md: v1 tests 12/12, four divergences
  found (NOTES D1–D4). `rules.py` left untouched (Immutable Rule).
- `rules_v2.py`: hardened layer specified in `SPEC_V2.md` before code,
  tests in `test_rules_v2.py` (31) written before the implementation.
- Imports located from the file, plus `conftest.py`: `pytest` now
  passes from any working directory (was `ModuleNotFoundError`).
- Each predicate and action gets its own capsule copy; actions can no
  longer change what later rules see or mutate the caller's capsule.
- Added rule priority, `safe=True` exception isolation and
  `dry_run=True`. Async actions deferred (see NOTES).
- Verification now goes through P2 `sign_v2`.
- Docs fixed: README status, NOTES spec reference, CHANGELOG headings.
- 43/43 tests pass (v1 12, v2 31).

### Bad
- v1 `rules.py` keeps D1–D4 by design; new code must import
  `rules_v2`.

### Ugly
- v2 reads v1 Engine's private `_rules` dict to fetch callables in
  priority order. Safe while v1 is frozen; revisit if v1 ever moves.

## [v1.0.0] — 2026-11-12

### Good
- `rules.py` implemented to SPEC v1.0.0.
- 12/12 pytest tests pass.
- Rule engine fires actions on matching capsules.
- Signature verification happens BEFORE any rule fires.
- Tampered or invalid capsules fire nothing.

### Bad
- (none)

### Ugly
- (none)

## [v0.0.0-dev] — scaffold

### Good
- Repository scaffolded: `Giblet-Legacy/rules-layer` created for P12.
- Depends on P1 Envelope v2.0.0 and P2 Sign v1.0.0.

### Bad
- (none)

### Ugly
- (none)
