# rules-layer — P12 Rules

README.md — repository purpose and layer contract for P12 Rules.

Function:
    This repository implements primitive layer P12 of the Forge Stack:
    the rule engine. It evaluates signed capsules against registered
    rules and fires actions when they match.

Layer:    P12 — Rules
Depends:  P1 Envelope v2, P2 Sign
Consumed: P13 DataCube, P15 HAL, The Cockpit
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
Status:   2.0.0 (v1 frozen; v2 hardened layer frozen). v3 declarative
          layer (rules_v3.py, SPEC_V3.md) built, not frozen.

Use:
    New code imports `rules_v2` (SPEC_V2.md). `rules.py` is the frozen
    v1.0.0 primitive (SPEC.md) and is never edited.

Test:
    pytest -q        # 43 passed, from any working directory
