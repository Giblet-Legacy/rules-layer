# NOTES — rules-layer (P12 Rules)

NOTES.md — open questions, divergences and decisions for P12 Rules.

## Open questions
- (none)

## Divergences from v1.2.1 specification
- (none)

## Decisions
- Engine.evaluate verifies the capsule signature BEFORE firing any
  rules. This prevents firing rules on tampered capsules.
- Empty result on invalid signature (rather than raise) matches the
  Forge Stack posture: verification is a policy question, not an
  exception.
- No exception isolation: action exceptions propagate. A v2 could
  add a `safe=True` mode if needed.
- Rules are callables, not serialised data. This keeps P12 v1
  minimal and testable. Serialising rules to disk is P13's or a
  higher layer's job.
