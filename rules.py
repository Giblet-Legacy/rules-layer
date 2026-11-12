"""
rules.py — P12 Rules primitive layer

Function:
    The rule engine. Evaluates signed capsules against registered
    rules. Fires actions on match. Verifies capsule signatures via
    P2 before firing any rules.

Public API:
    1. create_engine  — Returns an empty rule engine.
    2. Engine.register — Registers a named rule.
    3. Engine.evaluate — Verifies a capsule and fires matching rules.
    4. Engine.list_rules — Returns registered rule names.

Layer:    P12 — Rules
Depends:  P1 Envelope v2, P2 Sign
Consumed: P13 DataCube, P15 HAL, The Cockpit
Version:  1.0.0 (on freeze; 0.0.0-dev until then)
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import os
import sys

sys.path.insert(0, os.path.abspath('../envelope-layer'))
sys.path.insert(0, os.path.abspath('../sign-layer'))
import sign

# ---------------------------------------------------------------------------
# Engine class
# Holds registered rules. Rules are (predicate, action) tuples.
# ---------------------------------------------------------------------------
class Engine:
    def __init__(self):
        self._rules = {}

    # -----------------------------------------------------------------------
    # 1. register
    # Adds a rule. Raises on duplicate name or non-callable args.
    # -----------------------------------------------------------------------
    def register(self, name, predicate, action):
        if name in self._rules:
            raise ValueError(f"rule already registered: {name}")
        if not callable(predicate):
            raise ValueError("predicate must be callable")
        if not callable(action):
            raise ValueError("action must be callable")
        self._rules[name] = (predicate, action)

    # -----------------------------------------------------------------------
    # 2. evaluate
    # Verifies the capsule signature first. Then fires matching rules.
    # Returns list of {name, result} for each fired rule.
    # -----------------------------------------------------------------------
    def evaluate(self, capsule, public_key):
        if not sign.verify_capsule(capsule, public_key):
            return []

        fired = []
        for name in sorted(self._rules.keys()):
            predicate, action = self._rules[name]
            if predicate(capsule):
                result = action(capsule)
                fired.append({"name": name, "result": result})
        return fired

    # -----------------------------------------------------------------------
    # 3. list_rules
    # Returns registered rule names, sorted.
    # -----------------------------------------------------------------------
    def list_rules(self):
        return sorted(self._rules.keys())

# ---------------------------------------------------------------------------
# 4. create_engine
# Factory function. Returns a fresh rule engine.
# ---------------------------------------------------------------------------
def create_engine():
    return Engine()
