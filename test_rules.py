"""
test_rules.py — P12 Rules test suite

Function:
    Executable expression of SPEC.md. Written before rules.py per
    build discipline.

Layer:    P12 — Rules
Spec:     SPEC.md v1.0.0
Licence:  MSL-1.0
"""

import os
import sys
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, os.path.abspath('../envelope-layer'))
sys.path.insert(0, os.path.abspath('../sign-layer'))

import sign
import rules

@pytest.fixture
def key():
    return Ed25519PrivateKey.generate()

@pytest.fixture
def engine():
    return rules.create_engine()

@pytest.fixture
def signed_capsule(key):
    return sign.sign_capsule({"kind": "note", "text": "hello"}, key)

def test_create_engine_empty(engine):
    assert engine.list_rules() == []

def test_register_rule(engine):
    engine.register(
        "always_true",
        predicate=lambda c: True,
        action=lambda c: None,
    )
    assert engine.list_rules() == ["always_true"]

def test_register_duplicate_raises(engine):
    engine.register("r1", lambda c: True, lambda c: None)
    with pytest.raises(ValueError):
        engine.register("r1", lambda c: True, lambda c: None)

def test_register_non_callable_predicate_raises(engine):
    with pytest.raises(ValueError):
        engine.register("r1", "not_a_function", lambda c: None)

def test_register_non_callable_action_raises(engine):
    with pytest.raises(ValueError):
        engine.register("r1", lambda c: True, "not_a_function")

def test_evaluate_no_rules(engine, signed_capsule, key):
    fired = engine.evaluate(signed_capsule, key.public_key())
    assert fired == []

def test_evaluate_matching_rule_fires(engine, signed_capsule, key):
    log = []
    engine.register(
        "kind_is_note",
        predicate=lambda c: c.get("kind") == "note",
        action=lambda c: log.append(c["text"]),
    )
    fired = engine.evaluate(signed_capsule, key.public_key())
    assert len(fired) == 1
    assert fired[0]["name"] == "kind_is_note"
    assert log == ["hello"]

def test_evaluate_non_matching_rule_does_not_fire(engine, signed_capsule, key):
    log = []
    engine.register(
        "kind_is_alert",
        predicate=lambda c: c.get("kind") == "alert",
        action=lambda c: log.append(c),
    )
    fired = engine.evaluate(signed_capsule, key.public_key())
    assert fired == []
    assert log == []

def test_evaluate_multiple_rules_only_matching_fire(engine, signed_capsule, key):
    log = []
    engine.register("a", lambda c: True, lambda c: log.append("a"))
    engine.register("b", lambda c: False, lambda c: log.append("b"))
    engine.register("c", lambda c: True, lambda c: log.append("c"))
    fired = engine.evaluate(signed_capsule, key.public_key())
    names = sorted(r["name"] for r in fired)
    assert names == ["a", "c"]
    assert log == ["a", "c"]

def test_evaluate_invalid_signature_returns_empty(engine, signed_capsule, key):
    log = []
    engine.register("always", lambda c: True, lambda c: log.append(1))
    other_key = Ed25519PrivateKey.generate()
    fired = engine.evaluate(signed_capsule, other_key.public_key())
    assert fired == []
    assert log == []

def test_evaluate_tampered_capsule_returns_empty(engine, signed_capsule, key):
    log = []
    engine.register("always", lambda c: True, lambda c: log.append(1))
    signed_capsule["kind"] = "tampered"
    fired = engine.evaluate(signed_capsule, key.public_key())
    assert fired == []
    assert log == []

def test_evaluate_action_receives_capsule(engine, signed_capsule, key):
    captured = []
    engine.register("capture", lambda c: True, lambda c: captured.append(c))
    engine.evaluate(signed_capsule, key.public_key())
    assert len(captured) == 1
    assert captured[0]["kind"] == "note"
