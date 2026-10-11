# Development Rules

# Core Philosophy

90% planning.

10% implementation.

Prove assumptions before building abstractions.

Prefer boring solutions.

---

# Sources of Truth

Priority order:

1. SoftRF firmware source (https://github.com/lyusupov/SoftRF)
2. Validated RF captures
3. SYSTEM_FACTS.md
4. PROJECT_SPEC.md
5. ARCHITECTURE.md

If disagreement occurs:

Firmware wins.

Observed RF evidence wins over assumptions.

Every claim in documentation must be traceable to the firmware source.
Do not state a fact without a `file:line` citation.
If the firmware source does not confirm a claim, mark it as a hypothesis
in REVERSE_ENGINEERING_NOTES.md, not as a fact in SYSTEM_FACTS.md.

The firmware source is authoritative over:
- Protocol structure (sync word, frame layout, CRC, encryption)
- Modulation parameters (data rate, deviation, filtering)
- Frequency plan (channels, spacing, offsets)
- Any constant or behavior that appears in the source code

The firmware source does NOT define:
- The specific device's configuration (channel, device ID, encryption key)
- The specific application's message semantics
- The observed signal characteristics (which must come from captures)

When a fact comes from a capture rather than the firmware source, label it
as "observed" and cite the capture file and analysis method.

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

Every technical claim must cite its source with:
- File path (relative to the source repo)
- Line number(s)
- GitHub URL for remote verification (append path to the repo base URL)

Documentation must be consumable by both humans and other AI agents.
A fresh agent session with only the repo URL and a WAV sample must be able to
pick up from where the previous agent left off using the committed documentation.

The firmware source repository (https://github.com/lyusupov/SoftRF) is for
reference only. It is not a dependency, not committed, not required at build time.
All citations must be verifiable via GitHub without a local clone.

Before ending a session, all working memory (findings, hypotheses, partial
results) must be persisted to the appropriate documentation files. Nothing
documented only in conversation context may be considered durable.

Session winding down: prioritize documentation and committing work over
further investigation. An agent may leave investigation half-finished if the
documentation is complete.

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
