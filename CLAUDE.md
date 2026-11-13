# Forge Stack Context — P12 Rules

CLAUDE.md — Context briefing for AI assistants working in this repository.

## The Immutable Rule
Never rewrite a primitive. Add a layer.

## Dual-Device Workflow
We build on an S24 (Termux) and a laptop (VS Code). State is confirmed, never assumed. Always use LF line endings. Commit messages must be clear. We use the Good/Bad/Ugly CHANGELOG format (latest at top).

## Header Discipline
Every file MUST have a top header paragraph explaining its function.
Every function MUST have a numbered header.

## P12 Architecture Specifics
- Depends on `envelope_v2` (P1) and `sign` (P2).
- Current layer: `rules_v3.py` (SPEC_V3.md, built, not frozen): declarative JSON rules compiled onto the `rules_v2` engine. New code imports `rules_v3`.
- The rule engine. Fires actions based on signed capsules.
- A rule is a predicate: `lambda capsule -> bool`.
- Rules are pure: given the same capsule, they produce the same result.
- P12 does NOT enforce the Keystone Gate directly — that is P13's job.
  P12 is the execution engine; P13 defines the rules.
