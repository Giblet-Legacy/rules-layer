"""
conftest.py — pytest path setup for P12 Rules

Function:
    Puts this directory and the sibling P2 and P1 directories
    (../sign-layer, ../envelope-layer) on sys.path, located from this
    file rather than the working directory. pytest loads it before
    collecting tests, so test_rules.py (frozen v1, cwd-relative
    import) and test_rules_v2.py both run from any working directory
    (NOTES D1). Contains no functions.

Layer:    P12 — Rules
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_P1 = os.path.join(_ROOT, "envelope-layer")
_P2 = os.path.join(_ROOT, "sign-layer")

for _p in (_P1, _P2, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
