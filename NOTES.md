# NOTES — rules-layer (P12 Rules)

NOTES.md — open questions, divergences and decisions for P12 Rules.

## Open questions
- **Q1 — Freeze rules_v3 at 3.0.0?** **Resolved 2026-11-13 — James: "freeze all".** Frozen on the laptop run; the S24 run is still to be confirmed. Built and green on the laptop
  (48/48). Not yet run on the S24. Raised 2026-11-13. Owner: James.

## Divergences from SPEC.md v1.0.0 (found in laptop audit, 2026-11-12)
All closed in rules_v2.py (SPEC_V2.md). rules.py is frozen and unedited.

- D1 — rules.py and test_rules.py add `../sign-layer` and
  `../envelope-layer` to sys.path relative to the working directory.
  `pytest` run from anywhere but inside rules-layer fails with
  `ModuleNotFoundError: sign`. Closed by conftest.py and the
  file-relative imports in rules_v2.py (SPEC_V2 §2.1).
- D2 — every predicate and action receives the same live capsule. An
  action that mutates it changes what later predicates see, breaking
  "rules are pure" (SPEC §1), and mutates the caller's capsule.
  Closed by per-callable deep copies (SPEC_V2 §2.4).
- D3 — rule names are not type-checked. Registering a non-str name
  alongside a str name makes `list_rules()` and `evaluate()` raise
  `TypeError` on every later call. Closed by SPEC_V2 §2.3.
- D4 — `Engine.__init__` has no numbered header (Header Discipline).
  Closed in rules_v2.py (SPEC_V2 §2.8).

## Decisions
- 2026-11-13 — v3 (SPEC_V3.md) adopts the Echo's JSON matchers as
  the stack's declarative rule format, fail-closed on unknown keys.
  Decided by the VS Code AI on James's delegation ("fix all 11
  issues"). The "serialise rules" item below now has a home.
- Engine.evaluate verifies the capsule signature BEFORE firing any
  rules. This prevents firing rules on tampered capsules.
- Empty result on invalid signature (rather than raise) matches the
  Forge Stack posture: verification is a policy question, not an
  exception.
- No exception isolation in v1: action exceptions propagate. v2 adds
  `safe=True`; the default stays propagating.
- Rules are callables, not serialised data. This keeps P12 minimal
  and testable. Serialising rules to disk is P13's or a higher
  layer's job.

## v2 option decisions (PROMPT_P12.md step 5)
- Priority — ADOPTED. `register(..., priority=0)`; higher first, ties
  by name, so equal priorities reproduce v1's order exactly.
- Exception isolation `safe=True` — ADOPTED. Errors become
  `{name, error}` entries; only `Exception` is caught, so
  `KeyboardInterrupt`/`SystemExit` still stop the engine.
- Dry run — ADOPTED as `evaluate(..., dry_run=True)`. Predicates run,
  actions do not. Lets P13 and The Cockpit preview policy safely.
- Async actions — DEFERRED. No consumer needs it yet (P13 is not
  built), and an awaiting engine would force every caller onto an
  event loop. An action can still hand work to a loop it owns. Revisit
  when a consumer asks.
- Wrong public key type raises `TypeError` in v2 (inherited from
  sign_v2): passing a non-key is a caller bug, not a policy answer.
