"""
test_rules_v3.py — P12 Rules v3 (declarative rule layer) test suite

Function:
    Executable expression of SPEC_V3.md. Written before rules_v3.py
    and run red first.

Functions in this file (pytest-collected):
    1. test_matchers
    2. test_fail_closed
    3. test_load_rules_forms
    4. test_register_rules_fire_through_v2
    5. test_preview

Helpers:
    6. _signed — a P2-signed capsule and its public key

Layer:    P12 — Rules, v3
Spec:     SPEC_V3.md 3.0.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import json

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import rules_v2
import rules_v3
import sign_v2

RULES = [
    {"name": "any_unknown", "predicate_spec": {"face_matches": ["UNKNOWN"]},
     "action_spec": {"notify": "dreams"}},
    {"name": "sky", "predicate_spec": {"subject_matches": "sky", "object_contains": "blu"},
     "action_spec": {"tag": "colour"}, "priority": 10},
    {"name": "everything", "predicate_spec": {}, "action_spec": {}},
]


# 6. _signed
def _signed(claim):
    key = Ed25519PrivateKey.generate()
    return sign_v2.sign_capsule(dict(claim, signature=None), key), key.public_key()


# 1. test_matchers
def test_matchers():
    p = rules_v3.compile_predicate
    assert p({"subject_matches": "*"})({"subject": "x"})
    assert p({"subject_matches": "sky"})({"subject": "sky"})
    assert not p({"subject_matches": "sky"})({"subject": "sea"})
    assert p({"face_matches": ["FACT", "UNKNOWN"]})({"face": "UNKNOWN"})
    assert not p({"face_matches": ["FACT"]})({"face": "UNKNOWN"})
    assert p({"object_contains": "lu"})({"object": "blue"})
    assert not p({"object_contains": "lu"})({})
    both = p({"subject_matches": "sky", "face_matches": ["FACT"]})
    assert both({"subject": "sky", "face": "FACT"})
    assert not both({"subject": "sky", "face": "OPINION"})
    assert p({})({"anything": 1})


# 2. test_fail_closed
def test_fail_closed():
    bad_specs = [{"subject_match": "sky"}, {"subject_matches": 1},
                 {"face_matches": "FACT"}, {"face_matches": [1]},
                 {"object_contains": None}, "not a dict"]
    for spec in bad_specs:
        with pytest.raises(ValueError):
            rules_v3.compile_predicate(spec)
    good = {"name": "r", "predicate_spec": {}, "action_spec": {}}
    bad_rules = [
        [dict(good, extra=1)], [{"predicate_spec": {}}], [{"name": "r"}],
        [dict(good, name="")], [dict(good, action_spec=[])],
        [dict(good, priority=True)], [dict(good, priority=1.5)],
        [good, dict(good)], {"not": "a list"}, "not json [",
    ]
    for rules in bad_rules:
        with pytest.raises(ValueError):
            rules_v3.load_rules(rules)


# 3. test_load_rules_forms
def test_load_rules_forms():
    from_text = rules_v3.load_rules(json.dumps(RULES))
    from_list = rules_v3.load_rules(RULES)
    assert from_text == from_list
    assert [r["priority"] for r in from_list] == [0, 10, 0]


# 4. test_register_rules_fire_through_v2
def test_register_rules_fire_through_v2():
    capsule, pub = _signed({"subject": "sky", "object": "blue", "face": "FACT"})
    engine = rules_v2.create_engine()
    rules_v3.register_rules(engine, rules_v3.load_rules(RULES))
    fired = engine.evaluate(capsule, pub)
    assert [f["name"] for f in fired] == ["sky", "everything"]
    assert fired[0]["result"] == {"tag": "colour"}
    seen = []
    engine2 = rules_v2.create_engine()
    rules_v3.register_rules(engine2, rules_v3.load_rules(RULES),
                            action_factory=lambda rule: (lambda c: seen.append(rule["name"]) or "done"))
    engine2.evaluate(capsule, pub)
    assert seen == ["sky", "everything"]


# 5. test_preview
def test_preview():
    capsule, pub = _signed({"subject": "sky", "object": "pale blue", "face": "UNKNOWN"})
    calls = []
    rules = rules_v3.load_rules(RULES)
    assert rules_v3.preview(rules, capsule, pub) == ["sky", "any_unknown", "everything"]
    other = Ed25519PrivateKey.generate().public_key()
    assert rules_v3.preview(rules, capsule, other) == []
    assert calls == []
