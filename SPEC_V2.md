# SPEC V2 — rules-layer (P12 Rules, hardened layer)

SPEC_V2.md — specification for rules_v2.py, the layer above P12 v1.0.0.

Function:
    Specifies rules_v2.py, a layer over the frozen P12 v1.0.0
    primitive (rules.py). It closes divergences D1–D4 recorded in
    NOTES.md and adds the v2 options chosen in NOTES.md (priority,
    exception isolation, dry run) without editing rules.py
    (Immutable Rule).

    SPEC.md v1.0.0 remains authoritative for everything this document
    does not change. Where this document is silent, SPEC.md v1.0.0
    applies unchanged.

Layer:     P12 — Rules, v2 (hardened)
Depends:   rules.py (P12 v1.0.0), sign_v2.py (P2 v2.0.0)
Consumed:  P13 DataCube, P15 HAL, The Cockpit — new code imports
           rules_v2, not rules
Version:   SPEC V2 2.0.0
Licence:   MSL-1.0
Author:    James Gilbert (Giblets Forge)

---

## 1. Compatibility guarantee

- With default arguments, `evaluate` returns the same list as v1 for
  the same well-formed inputs whenever no action mutates the capsule.
- Rule registration, duplicate detection and callable checks are
  done by v1's `Engine.register`, so the error messages match v1.
- v2 narrows v1 by rejecting non-str rule names (§2.3) and non
  Ed25519 public keys (§2.2). That narrowing is why the major
  version is 2.

## 2. Changes from SPEC.md v1.0.0

### 2.1 Imports located from this file (closes D1)
rules_v2.py finds `../sign-layer` and `../envelope-layer` from its own
location, not the working directory. A `conftest.py` does the same for
the test suites, so `pytest` works from any directory.

### 2.2 Verification through P2 v2
Signatures are checked with `sign_v2.verify_capsule`. Any malformed
capsule (non-dict, missing or malformed signature, tampered) returns
`[]` and fires nothing. A `public_key` that is not an
`Ed25519PublicKey` raises `TypeError` (a caller bug, not a policy
answer).

### 2.3 Rule names (closes D3)
`register` raises `ValueError` if `name` is not a non-empty `str`.

### 2.4 Capsule isolation (closes D2)
After verification the engine takes a deep copy of the capsule. Each
predicate and each action receives its own deep copy of that
snapshot. No callable can change what another callable sees, and the
caller's capsule is never modified by the engine.

### 2.5 Priority
`register(name, predicate, action, priority=0)`.
- `priority` must be an `int` (not `bool`), else `ValueError`.
- Rules are evaluated in descending priority; ties break by name
  ascending. With all priorities equal this is v1's sorted order.
- `list_rules()` still returns names sorted alphabetically (v1).
- `get_priority(name) -> int` returns a rule's priority; `KeyError`
  if the name is not registered.

### 2.6 Exception isolation: `safe=True`
`evaluate(capsule, public_key, safe=False, dry_run=False)`.
- `safe=False` (default): exceptions propagate, as in v1.
- `safe=True`: an exception raised by a predicate or an action
  (any `Exception` subclass) is caught. That rule appends
  `{"name": name, "error": "<ExcType>: <message>"}` and evaluation
  continues with the next rule. A rule whose predicate raised does
  not fire its action. `BaseException`s that are not `Exception`
  (e.g. `KeyboardInterrupt`) always propagate.

### 2.7 Dry run: `dry_run=True`
- Predicates are evaluated; no action is called.
- Returns `{"name": name, "result": None}` for each rule that would
  fire, in evaluation order.
- Combines with `safe`: predicate errors are recorded as in §2.6.

### 2.8 Header discipline (closes D4)
Every function and method in rules_v2.py carries a numbered header.

## 3. Not in v2 (decided, see NOTES.md)

- Async actions — deferred until a consumer needs them.
- Rule serialisation to disk — P13's job.
