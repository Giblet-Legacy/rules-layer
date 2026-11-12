# SPEC — rules-layer (P12 Rules)

SPEC.md — the complete layer specification for P12 Rules.

Function:
    This document is the authoritative specification for primitive
    layer P12 of the Forge Stack. It defines the rule engine that
    evaluates signed capsules and fires actions on match.

Layer:     P12 — Rules
Depends:   P1 Envelope v2, P2 Sign
Consumed:  P13 DataCube, P15 HAL, The Cockpit
Version:   SPEC 1.0.0
Licence:   MSL-1.0
Author:    James Gilbert (Giblets Forge)

## 1. The Rule Engine Rule

A rule is a named predicate over a capsule:
    rule_name: str
    predicate: Callable[[dict], bool]
    action:    Callable[[dict], Any]

The engine registers rules and evaluates capsules. On a match, the
action fires. Rules are pure: given the same capsule, they produce
the same match result. Actions may be impure (I/O, notifications).

P12 does not decide which rules should exist. That is P13
(DataCube) — P12 is the engine, P13 is the policy.

## 2. Function Contracts

### 2.1 create_engine() -> Engine
- Returns an empty rule engine instance.

### 2.2 Engine.register(name: str, predicate: Callable, action: Callable) -> None
- Registers a rule.
- Raises ValueError if `name` is already registered.
- Raises ValueError if `predicate` or `action` is not callable.

### 2.3 Engine.evaluate(capsule: dict, public_key) -> list[dict]
- Verifies the capsule's signature via P2's verify_capsule.
- If invalid, returns [] and does not fire any rules.
- For each registered rule, calls predicate(capsule).
- If True, calls action(capsule) and records the fired rule.
- Returns a list of {name, result} for each fired rule.

### 2.4 Engine.list_rules() -> list[str]
- Returns the list of registered rule names, sorted.

## 3. Known Limitations (P12 v1.0.0)

- Synchronous execution only. Async actions are a v2 concern.
- No priority or ordering between rules. All matches fire.
- No exception isolation: if an action raises, the exception
  propagates to the caller. This is deliberate — silent rule
  failures hide bugs.
- Rules are registered at runtime. Serialising rules to disk is
  a v2 concern.
