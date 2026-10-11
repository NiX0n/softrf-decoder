# Evidence Rules

All protocol claims shall be labeled as one of:

[FIRMWARE VERIFIED]
[RF VERIFIED]
[HYPOTHESIS]
[UNVERIFIED]

Examples:

[FIRMWARE VERIFIED]
Legacy bitrate is 100 kbps.

[RF VERIFIED]
Burst observed at frequency X.

[HYPOTHESIS]
Manchester decoding is required.

---

# Investigation Rules

Before implementing a fix:

1. Identify failing stage.
2. Collect evidence.
3. Document evidence.
4. Implement change.
5. Re-test.

Do not implement speculative fixes.

---

# Session Exit Criteria

Before ending a development session:

- Update CURRENT_BLOCKERS.md
- Update SYSTEM_FACTS.md
- Update REVERSE_ENGINEERING_NOTES.md
- Document discoveries
- Document failed experiments
- Record confidence level

A session is not complete until documentation has been updated.

---

# Confidence Reporting

Every major conclusion shall include:

- Conclusion
- Evidence
- Confidence

Example:

Manchester decoding required.

Confidence: Medium

Evidence:
- Firmware references suggest Manchester encoding.
- Decoder output inconsistent with expected framing.

Status:
HYPOTHESIS
