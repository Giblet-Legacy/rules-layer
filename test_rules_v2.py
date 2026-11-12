"""
test_rules_v2.py — P12 Rules v2 test suite

Function:
    Executable expression of SPEC_V2.md. Written before rules_v2.py
    per build discipline. Covers v1 compatibility, the closed
    divergences D1–D3, priority, safe mode and dry run.

Layer:    P12 — Rules, v2
Spec:     SPEC_V2.md 2.0.0
Licence:  MSL-1.0
"""

import os
import subprocess
import sys

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import sign
import rules
import rules_v2


@pytest.fixture
def key():
    return Ed25519PrivateKey.generate()


@pytest.fixture
def engine():
    return rules_v2.create_engine()


@pytest.fixture
def capsule(key):
    return sign.sign_capsule({"kind": "note", "text": "hello", "tags": ["a"]}, key)


# 1. Compatibility with v1 (SPEC_V2 §1) -------------------------------------

def test_same_result_as_v1(engine, capsule, key):
    v1 = rules.create_engine()
    for e in (v1, engine):
        e.register("b", lambda c: True, lambda c: "B")
        e.register("a", lambda c: c["kind"] == "note", lambda c: c["text"])
        e.register("c", lambda c: False, lambda c: "C")
    assert engine.evaluate(capsule, key.public_key()) == v1.evaluate(capsule, key.public_key())


def test_v1_register_errors_preserved(engine):
    engine.register("r1", lambda c: True, lambda c: None)
    with pytest.raises(ValueError):
        engine.register("r1", lambda c: True, lambda c: None)
    with pytest.raises(ValueError):
        engine.register("r2", "x", lambda c: None)
    with pytest.raises(ValueError):
        engine.register("r3", lambda c: True, "x")
    assert engine.list_rules() == ["r1"]


# 2. Imports independent of cwd (SPEC_V2 §2.1, D1) --------------------------

def test_import_from_other_cwd(tmp_path):
    here = os.path.dirname(os.path.abspath(__file__))
    code = f"import sys; sys.path.insert(0, {here!r}); import rules_v2; print('ok')"
    out = subprocess.run([sys.executable, "-c", code], cwd=tmp_path,
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "ok"


# 3. Verification (SPEC_V2 §2.2) --------------------------------------------

def test_invalid_signature_fires_nothing(engine, capsule):
    log = []
    engine.register("r", lambda c: True, lambda c: log.append(1))
    other = Ed25519PrivateKey.generate().public_key()
    assert engine.evaluate(capsule, other) == []
    assert log == []


def test_tampered_fires_nothing(engine, capsule, key):
    log = []
    engine.register("r", lambda c: True, lambda c: log.append(1))
    capsule["kind"] = "tampered"
    assert engine.evaluate(capsule, key.public_key()) == []
    assert log == []


@pytest.mark.parametrize("bad", ["x", None, {}, {"kind": "note"},
                                 {"kind": "note", "signature": "nope"}])
def test_malformed_capsule_returns_empty(engine, key, bad):
    engine.register("r", lambda c: True, lambda c: 1)
    assert engine.evaluate(bad, key.public_key()) == []


def test_wrong_key_type_raises(engine, capsule):
    with pytest.raises(TypeError):
        engine.evaluate(capsule, "not-a-key")


# 4. Rule names (SPEC_V2 §2.3, D3) ------------------------------------------

@pytest.mark.parametrize("name", [1, None, "", b"r", ("r",)])
def test_bad_name_raises(engine, name):
    with pytest.raises(ValueError):
        engine.register(name, lambda c: True, lambda c: None)
    assert engine.list_rules() == []


# 5. Capsule isolation (SPEC_V2 §2.4, D2) -----------------------------------

def test_action_mutation_does_not_leak(engine, capsule, key):
    engine.register("a", lambda c: True, lambda c: c.update(kind="x"))
    engine.register("b", lambda c: c["kind"] == "note", lambda c: "b")
    fired = engine.evaluate(capsule, key.public_key())
    assert [r["name"] for r in fired] == ["a", "b"]
    assert capsule["kind"] == "note"


def test_predicate_mutation_does_not_leak(engine, capsule, key):
    def bad_pred(c):
        c["tags"].append("z")
        return True
    seen = []
    engine.register("a", bad_pred, lambda c: None)
    engine.register("b", lambda c: True, lambda c: seen.append(list(c["tags"])))
    engine.evaluate(capsule, key.public_key())
    assert seen == [["a"]]
    assert capsule["tags"] == ["a"]


# 6. Priority (SPEC_V2 §2.5) ------------------------------------------------

def test_priority_order(engine, capsule, key):
    order = []
    engine.register("low", lambda c: True, lambda c: order.append("low"), priority=-1)
    engine.register("high", lambda c: True, lambda c: order.append("high"), priority=10)
    engine.register("b_mid", lambda c: True, lambda c: order.append("b_mid"))
    engine.register("a_mid", lambda c: True, lambda c: order.append("a_mid"))
    fired = engine.evaluate(capsule, key.public_key())
    assert order == ["high", "a_mid", "b_mid", "low"]
    assert [r["name"] for r in fired] == order
    assert engine.list_rules() == ["a_mid", "b_mid", "high", "low"]


@pytest.mark.parametrize("p", [1.5, "1", True, None])
def test_bad_priority_raises(engine, p):
    with pytest.raises(ValueError):
        engine.register("r", lambda c: True, lambda c: None, priority=p)
    assert engine.list_rules() == []


def test_get_priority(engine):
    engine.register("r", lambda c: True, lambda c: None, priority=3)
    assert engine.get_priority("r") == 3
    with pytest.raises(KeyError):
        engine.get_priority("missing")


# 7. Safe mode (SPEC_V2 §2.6) -----------------------------------------------

def _boom(c):
    raise RuntimeError("boom")


def test_unsafe_propagates(engine, capsule, key):
    engine.register("r", lambda c: True, _boom)
    with pytest.raises(RuntimeError):
        engine.evaluate(capsule, key.public_key())


def test_safe_action_error_recorded(engine, capsule, key):
    engine.register("a", lambda c: True, _boom)
    engine.register("b", lambda c: True, lambda c: "ok")
    fired = engine.evaluate(capsule, key.public_key(), safe=True)
    assert fired == [{"name": "a", "error": "RuntimeError: boom"},
                     {"name": "b", "result": "ok"}]


def test_safe_predicate_error_skips_action(engine, capsule, key):
    log = []
    engine.register("a", _boom, lambda c: log.append("a"))
    engine.register("b", lambda c: True, lambda c: log.append("b"))
    fired = engine.evaluate(capsule, key.public_key(), safe=True)
    assert fired[0] == {"name": "a", "error": "RuntimeError: boom"}
    assert log == ["b"]


def test_safe_does_not_swallow_base_exceptions(engine, capsule, key):
    def interrupt(c):
        raise KeyboardInterrupt
    engine.register("r", lambda c: True, interrupt)
    with pytest.raises(KeyboardInterrupt):
        engine.evaluate(capsule, key.public_key(), safe=True)


# 8. Dry run (SPEC_V2 §2.7) -------------------------------------------------

def test_dry_run_fires_no_actions(engine, capsule, key):
    log = []
    engine.register("a", lambda c: True, lambda c: log.append("a"), priority=1)
    engine.register("b", lambda c: False, lambda c: log.append("b"))
    engine.register("c", lambda c: True, lambda c: log.append("c"))
    fired = engine.evaluate(capsule, key.public_key(), dry_run=True)
    assert fired == [{"name": "a", "result": None}, {"name": "c", "result": None}]
    assert log == []


def test_dry_run_with_safe(engine, capsule, key):
    engine.register("a", _boom, lambda c: 1)
    engine.register("b", lambda c: True, _boom)
    fired = engine.evaluate(capsule, key.public_key(), safe=True, dry_run=True)
    assert fired == [{"name": "a", "error": "RuntimeError: boom"},
                     {"name": "b", "result": None}]


def test_dry_run_invalid_signature(engine, capsule):
    engine.register("a", lambda c: True, lambda c: 1)
    other = Ed25519PrivateKey.generate().public_key()
    assert engine.evaluate(capsule, other, dry_run=True) == []
