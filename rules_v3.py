"""
rules_v3.py — P12 Rules v3, the declarative rule layer over the v2 engine

Function:
    The layer new code imports instead of rules_v2.py when rules come
    from a file. It defines the stack's declarative rule format (the
    Echo's matchers, adopted), validates it fail-closed, compiles it to
    pure predicates and registers it on a rules_v2 Engine. Previews run
    through the real v2 engine with dry_run=True (SPEC_V3.md).

    rules.py and rules_v2.py are not edited (Immutable Rule).

Public API:
    1. load_rules        — JSON text or list → validated rules
    2. compile_predicate — one predicate_spec → pure predicate
    3. register_rules    — rules onto a v2 Engine
    4. preview           — names that would fire, via v2 dry_run
    (re-exported from v2: Engine, create_engine)

Internal helpers (not exported):
    5. _check_spec — validate one predicate_spec
    6. _check_rule — validate one rule object, fill priority

Layer:    P12 — Rules, v3
Depends:  rules_v2.py (P12 v2.0.0)
Consumed: The Echo, The Cockpit, P13 DataCube
Spec:     SPEC_V3.md 3.0.0
Version:  3.0.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import copy
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import rules_v2 as _v2  # noqa: E402

Engine = _v2.Engine
create_engine = _v2.create_engine

_RULE_KEYS = {"name", "predicate_spec", "action_spec", "priority"}
_MATCHERS = {"subject_matches", "face_matches", "object_contains"}


# ---------------------------------------------------------------------------
# 5. _check_spec
#    SPEC_V3 §1: known matchers only, right types. Fail closed.
# ---------------------------------------------------------------------------
def _check_spec(spec):
    if not isinstance(spec, dict):
        raise ValueError("predicate_spec must be an object")
    unknown = set(spec) - _MATCHERS
    if unknown:
        raise ValueError(f"unknown matcher(s): {sorted(unknown)}")
    if "subject_matches" in spec and not isinstance(spec["subject_matches"], str):
        raise ValueError("subject_matches must be a str")
    if "face_matches" in spec:
        faces = spec["face_matches"]
        if not isinstance(faces, list) or not all(isinstance(f, str) for f in faces):
            raise ValueError("face_matches must be a list of str")
    if "object_contains" in spec and not isinstance(spec["object_contains"], str):
        raise ValueError("object_contains must be a str")


# ---------------------------------------------------------------------------
# 2. compile_predicate
#    SPEC_V3 §2.2. Every present matcher must hold (AND).
# ---------------------------------------------------------------------------
def compile_predicate(predicate_spec):
    _check_spec(predicate_spec)
    spec = copy.deepcopy(predicate_spec)

    def predicate(capsule):
        if "subject_matches" in spec:
            if spec["subject_matches"] != "*" and capsule.get("subject") != spec["subject_matches"]:
                return False
        if "face_matches" in spec and capsule.get("face") not in spec["face_matches"]:
            return False
        if "object_contains" in spec:
            obj = capsule.get("object")
            if spec["object_contains"] not in (obj if isinstance(obj, str) else ""):
                return False
        return True

    return predicate


# ---------------------------------------------------------------------------
# 6. _check_rule
# ---------------------------------------------------------------------------
def _check_rule(rule):
    if not isinstance(rule, dict):
        raise ValueError("each rule must be an object")
    unknown = set(rule) - _RULE_KEYS
    if unknown:
        raise ValueError(f"unknown rule key(s): {sorted(unknown)}")
    name = rule.get("name")
    if not isinstance(name, str) or not name:
        raise ValueError("rule name must be a non-empty str")
    if "predicate_spec" not in rule:
        raise ValueError(f"rule {name!r} has no predicate_spec")
    _check_spec(rule["predicate_spec"])
    if not isinstance(rule.get("action_spec", {}), dict):
        raise ValueError(f"rule {name!r} action_spec must be an object")
    priority = rule.get("priority", 0)
    if isinstance(priority, bool) or not isinstance(priority, int):
        raise ValueError(f"rule {name!r} priority must be an int")
    out = copy.deepcopy(rule)
    out.setdefault("action_spec", {})
    out["priority"] = priority
    return out


# ---------------------------------------------------------------------------
# 1. load_rules
#    SPEC_V3 §2.1.
# ---------------------------------------------------------------------------
def load_rules(source):
    if isinstance(source, str):
        try:
            source = json.loads(source)
        except ValueError:
            raise ValueError("rule file is not valid JSON") from None
    if not isinstance(source, list):
        raise ValueError("rules must be a JSON array")
    rules = [_check_rule(r) for r in source]
    names = [r["name"] for r in rules]
    if len(names) != len(set(names)):
        raise ValueError("duplicate rule name")
    return rules


# ---------------------------------------------------------------------------
# 3. register_rules
#    SPEC_V3 §2.3. Default action returns a copy of the action_spec.
# ---------------------------------------------------------------------------
def register_rules(engine, rules, action_factory=None):
    for rule in rules:
        if action_factory is not None:
            action = action_factory(rule)
        else:
            spec = copy.deepcopy(rule["action_spec"])
            action = (lambda s: lambda capsule: copy.deepcopy(s))(spec)
        engine.register(rule["name"], compile_predicate(rule["predicate_spec"]),
                        action, priority=rule["priority"])


# ---------------------------------------------------------------------------
# 4. preview
#    SPEC_V3 §2.4. Real v2 engine, dry_run=True: predicates run, no action.
# ---------------------------------------------------------------------------
def preview(rules, capsule, public_key):
    engine = create_engine()
    register_rules(engine, rules)
    return [f["name"] for f in engine.evaluate(capsule, public_key, dry_run=True)]
