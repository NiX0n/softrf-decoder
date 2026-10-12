# Current Blockers

This document tracks the current reality of the project.

It is not speculative.

It contains only demonstrated status.

---

# Status Matrix

## RF Capture

Control Sample Available:
✅ YES

Capture Validated:
✅ YES

Evidence:

- Float32 IQ
- 20 MS/s
- ~5.6 second duration
- RF bursts observed

---

## Protocol Research

SoftRF firmware citations collected:
✅ YES

Legacy protocol documentation:
✅ YES

Frequency research:
✅ PARTIAL

---

## Decoding Pipeline

Signal Detection:
✅ CONFIRMED

Burst Identification:
✅ CONFIRMED

Carrier Identification:
⚠ PARTIAL

Modulation Classification:
⚠ PARTIAL

Symbol Recovery:
❌ NOT PROVEN

Manchester Decoding:
❌ NOT PROVEN

Frame Recovery:
❌ NOT PROVEN

CRC Validation:
❌ NOT PROVEN

Payload Recovery:
❌ NOT PROVEN

Telemetry Decode:
❌ NOT PROVEN

---

# Primary Goal

Advance the earliest failing stage.

Do not skip ahead.

---

# Current Working Hypotheses

These are NOT facts.

1. Manchester decoding is required.
2. Legacy uses a fixed channel.
3. Incorrect symbol recovery is preventing frame extraction.

These hypotheses require validation.

---

# Success Definition

Control IQ Sample
        ↓
Recovered Frame
        ↓
Passing CRC
        ↓
Decoded Telemetry

Only then is Phase 1 complete.

# Decoder Evidence Ladder

The decoder progresses through the following stages:

IQ Capture
    ↓
Burst Detection
    ↓
Carrier Identification
    ↓
Modulation Classification
    ↓
Symbol Recovery
    ↓
Frame Recovery
    ↓
Sync Validation
    ↓
CRC Validation
    ↓
Payload Recovery
    ↓
Telemetry Decode

The earliest failing stage must always be identified.

Development shall focus exclusively on the earliest failing stage.
