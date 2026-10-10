# Development Rules

## General

Prefer boring solutions.

Novel solutions require justification.

Avoid unnecessary abstraction.

---

## Git Hygiene

Commit early.

Commit often.

Keep commits small.

Keep commits focused.

Write meaningful commit messages.

---

## Documentation

README shall be maintained.

Architecture documentation shall be maintained.

Public interfaces shall be documented.

Protocol discoveries shall be documented.

---

## Testing

Unit tests are mandatory.

Regression tests are mandatory.

Tests should accompany new functionality.

Coverage is a project objective.

---

## Sensitive Data

Do not commit IQ captures.

Do not commit sensitive location data.

Replace private captures with synthetic fixtures whenever possible.

---

## Anti-Drift Rules

Do not replace GNU Radio.

Do not implement additional protocols before Legacy works.

Do not build a UI before decoding works.

Do not add a database before decoding works.

Do not introduce distributed architectures.

Every major architectural change requires written justification.

---

## Phase Gates

Do not proceed to the next phase until the current phase is proven.

Examples:

- No track management before decoding.
- No output adapters before tracks.
- No service framework before core functionality.

Proof over speculation.
