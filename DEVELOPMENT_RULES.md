# Development Rules

# Core Philosophy

90% planning.

10% implementation.

Prove assumptions before building abstractions.

Prefer boring solutions.

---

# Sources of Truth

Priority order:

1. SoftRF firmware source
2. Validated RF captures
3. SYSTEM_FACTS.md
4. PROJECT_SPEC.md
5. ARCHITECTURE.md

If disagreement occurs:

Firmware wins.

Observed RF evidence wins over assumptions.

---

# Language Rules

Preferred language: TypeScript.

Do not introduce Python implementations of business logic.

Python is limited to:

- GNU Radio
- DSP tooling
- analysis tooling
- development utilities

Business logic belongs in TypeScript.

---

# Framework Rules

Do not begin with NestJS.

Build libraries first.

Build services second.

Wrap proven libraries in NestJS later.

Examples:

Correct:

Library
→ Tests
→ NestJS

Incorrect:

NestJS
→ Business Logic

---

# GNU Radio Rules

GNU Radio is a permanent dependency.

Do not replace GNU Radio.

Do not migrate DSP into TypeScript.

Do not build a custom DSP framework.

---

# Testing Rules

Testing is mandatory.

Every practical feature requires tests.

Every bug fix should include a regression test.

Coverage is a project objective.

Important paths should be fixture-driven.

---

# Fixture Rules

Control captures are sensitive.

Never commit sensitive captures.

Where practical:

Generate synthetic fixtures.

Public fixtures must not contain sensitive telemetry.

---

# Commit Hygiene

Commit early.

Commit often.

Keep commits focused.

Keep commits small.

Keep commits understandable.

Write meaningful commit messages.

---

# Documentation

Maintain README.

Maintain architecture documents.

Document protocol discoveries.

Document assumptions.

Promote verified discoveries into SYSTEM_FACTS.md.

---

# Anti-Drift Rules

Do not implement additional protocols before Legacy works.

Do not build a UI before decoding works.

Do not build adapters before tracks exist.

Do not build tracks before telemetry decodes.

Do not add databases before realtime decoding exists.

Do not add distributed architectures.

Do not add cloud dependencies.

Major architectural changes require written justification.

---

# Phase Gates

Do not advance to the next phase until current acceptance criteria are satisfied.

Prototype first.

Verify second.

Refactor third.

Scale last.

---

# Success Definition

The first true project milestone is:

Control IQ Capture
        ↓
Decoded Telemetry

Nothing else is considered complete until this milestone is achieved.
