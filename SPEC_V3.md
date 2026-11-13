# SPEC V3 — rules-layer (P12 Rules, declarative rule layer)

SPEC_V3.md — specification for rules_v3.py, the layer above P12 v2.0.0.

Function:
    Gives P12 a rule format that can live in a file. P12 rules are
    Python callables (SPEC.md §1), so no two consumers could share a
    rule set, and The Echo invented its own JSON matchers to "preview
    P12" without using P12 at all. V3 adopts the Echo's format as the
    stack's declarative rule format and compiles it onto the v2
    engine. SPEC_V2.md remains authoritative for the engine itself.

Layer:     P12 — Rules, v3
Depends:   rules_v2.py (P12 v2.0.0)
Consumed:  The Echo, The Cockpit, P13 DataCube
Version:   SPEC V3 3.0.0
Licence:   MSL-1.0
Author:    James Gilbert (Giblets Forge)

---

## 1. Declarative rule format (JSON)

A rule file is a JSON array of rule objects:

    {
      "name": "<non-empty str>",
      "predicate_spec": { <matchers> },
      "action_spec": { <any JSON object> },
      "priority": <int, optional, default 0>
    }

Matchers (all optional; every present matcher must hold — AND):

| Matcher | Type | Holds when |
| --- | --- | --- |
| `subject_matches` | str | `"*"`, or equal to the capsule's `subject` |
| `face_matches` | list of str | the capsule's `face` is in the list |
| `object_contains` | str | it is a substring of the capsule's `object` (missing → `""`) |

These are exactly the Echo v1.0.0 semantics. An empty
`predicate_spec` matches every capsule.

**Fail closed.** An unknown matcher key, a wrong matcher type, an
unknown rule key, a missing `name` / `predicate_spec`, a non-object
`action_spec`, a bool or non-int `priority`, or a duplicate name is a
ValueError when loading. A typo must never turn into "matches
everything".

`action_spec` is data. P12 never executes it: what an action *does*
is the consumer's decision (§2.3).

## 2. Function Contracts

### 2.1 load_rules(source) -> list[dict]
`source` is a JSON string, or an already-parsed list. Returns the
validated rules, each with `priority` filled in. Raises ValueError as
§1.

### 2.2 compile_predicate(predicate_spec) -> Callable[[dict], bool]
The pure predicate for one spec. Validates as §1.

### 2.3 register_rules(engine, rules, action_factory=None) -> None
Registers each rule on a rules_v2 Engine with its compiled predicate
and priority. The action is `action_factory(rule)` if given, else a
function returning a copy of the rule's `action_spec`. Engine errors
(duplicate name already registered) propagate.

### 2.4 preview(rules, capsule, public_key) -> list[str]
Builds a fresh v2 engine, registers the rules, and calls
`evaluate(capsule, public_key, dry_run=True)`. Returns the fired rule
names in engine order. A capsule whose signature does not verify
fires nothing, as in v2. No action runs.

## 3. Public API

1. load_rules
2. compile_predicate
3. register_rules
4. preview
(re-exported from v2: Engine, create_engine)

## 4. Tests (test_rules_v3.py)

- Each matcher holds and fails as §1; matchers combine with AND;
  empty spec matches all.
- Fail closed on every §1 error case.
- load_rules accepts a JSON string and a list; fills priority.
- register_rules: compiled rules fire through a real v2 engine; the
  default action returns the action_spec; a custom factory is used.
- preview: names in priority order, nothing for a bad signature, no
  action called.

---

## Document control

- **SPEC V3 3.0.0** — 2026-11-13, by the VS Code AI on James's
  delegation ("fix all 11 issues").
