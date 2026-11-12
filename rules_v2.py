"""
rules_v2.py — P12 Rules v2, hardened layer over the frozen v1 primitive

Function:
    The layer new code imports instead of rules.py. It finds P2 and P1
    from its own location rather than the working directory, verifies
    capsules through sign_v2, rejects non-str rule names, gives every
    predicate and action its own copy of the capsule, and adds rule
    priority, exception isolation (safe=True) and a dry-run mode
    (SPEC_V2.md §2). Registration validation is delegated to v1's
    Engine.register, so v1's error contract is kept.

    rules.py is not edited (Immutable Rule). This file is the
    "add a layer" half of that rule.

Public API (v1 names and numbering kept, new entries appended):
    1. Engine.register     — v1 checks, plus str name and int priority
    2. Engine.evaluate     — verify via sign_v2, then fire by priority;
                             safe and dry_run options
    3. Engine.list_rules   — registered names, sorted (v1)
    4. create_engine       — returns an empty v2 Engine
    5. Engine.__init__     — empty v1 engine plus priority table
    6. Engine.get_priority — a registered rule's priority

Internal helpers (not exported):
    7. _call — run a callable, isolating exceptions when safe=True

Layer:    P12 — Rules, v2 (hardened)
Depends:  rules.py (P12 v1.0.0), sign_v2.py (P2 v2.0.0)
Consumed: P13 DataCube, P15 HAL, The Cockpit
Spec:     SPEC_V2.md 2.0.0 (over SPEC.md v1.0.0)
Version:  2.0.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import copy
import os
import sys

# Locate P1 and P2 from this file, not the working directory
# (SPEC_V2 §2.1). Must run before importing rules.py, whose own path
# inserts are cwd-relative and only correct inside rules-layer.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (os.path.join(_ROOT, "envelope-layer"), os.path.join(_ROOT, "sign-layer")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import rules as _v1
import sign_v2


# ---------------------------------------------------------------------------
# 7. _call
#    Calls fn(arg). With safe=True an Exception becomes (False, text);
#    otherwise it propagates. Returns (ok, value_or_error_text).
# ---------------------------------------------------------------------------
def _call(fn, arg, safe):
    if not safe:
        return True, fn(arg)
    try:
        return True, fn(arg)
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


class Engine:
    """Rule engine. Storage and validation by a v1 Engine; priority here."""

    # -----------------------------------------------------------------------
    # 5. __init__
    #    An empty v1 engine holds (predicate, action); priorities kept here.
    # -----------------------------------------------------------------------
    def __init__(self):
        self._v1 = _v1.Engine()
        self._priority = {}

    # -----------------------------------------------------------------------
    # 1. register
    #    str name and int priority checked first (SPEC_V2 §2.3, §2.5),
    #    then v1 register for duplicate and callable checks.
    # -----------------------------------------------------------------------
    def register(self, name, predicate, action, priority=0):
        if not isinstance(name, str) or not name:
            raise ValueError("rule name must be a non-empty str")
        if isinstance(priority, bool) or not isinstance(priority, int):
            raise ValueError("priority must be an int")
        self._v1.register(name, predicate, action)
        self._priority[name] = priority

    # -----------------------------------------------------------------------
    # 6. get_priority
    #    Returns the rule's priority. KeyError if not registered.
    # -----------------------------------------------------------------------
    def get_priority(self, name):
        return self._priority[name]

    # -----------------------------------------------------------------------
    # 2. evaluate
    #    Verify via sign_v2 (SPEC_V2 §2.2); invalid -> []. Snapshot the
    #    capsule and give each callable its own copy (§2.4). Evaluate by
    #    descending priority, then name (§2.5). safe (§2.6) and dry_run
    #    (§2.7) as specified.
    # -----------------------------------------------------------------------
    def evaluate(self, capsule, public_key, safe=False, dry_run=False):
        if not sign_v2.verify_capsule(capsule, public_key):
            return []

        snapshot = copy.deepcopy(capsule)
        order = sorted(self._priority, key=lambda n: (-self._priority[n], n))

        fired = []
        for name in order:
            predicate, action = self._v1._rules[name]
            ok, matched = _call(predicate, copy.deepcopy(snapshot), safe)
            if not ok:
                fired.append({"name": name, "error": matched})
                continue
            if not matched:
                continue
            if dry_run:
                fired.append({"name": name, "result": None})
                continue
            ok, result = _call(action, copy.deepcopy(snapshot), safe)
            if ok:
                fired.append({"name": name, "result": result})
            else:
                fired.append({"name": name, "error": result})
        return fired

    # -----------------------------------------------------------------------
    # 3. list_rules
    #    Registered rule names, sorted alphabetically (v1 behaviour).
    # -----------------------------------------------------------------------
    def list_rules(self):
        return self._v1.list_rules()


# ---------------------------------------------------------------------------
# 4. create_engine
#    Factory function. Returns a fresh v2 rule engine.
# ---------------------------------------------------------------------------
def create_engine():
    return Engine()
