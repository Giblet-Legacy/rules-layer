# P12 Rules — Laptop Audit Prompt

P12 rules-layer is frozen at v1.0.0 on the phone with 12/12 tests passing.

## Your Task

1. Pull `Giblet-Legacy/rules-layer`.
2. Audit against SPEC.md and CHANGELOG.md.
3. Run `pytest -q` — expect 12 passed.
4. If you find gaps, create `rules_v2.py` (do NOT edit v1).
5. Suggested V2 hardening: add rule prioritisation, add exception isolation mode (`safe=True`), add async action support, add a `dry_run` mode that evaluates predicates without firing actions.
6. Push when green so the phone can verify.
