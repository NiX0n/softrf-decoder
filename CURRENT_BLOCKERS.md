# Current Blockers

This document tracks the current reality of the project.

It is not speculative.

It contains only demonstrated status.

---

## CRITICAL UPDATE (2026-10-12)

**The capture is VALID. The signal is OOK/ASK at ~769 ksym/s. This is NOT the SoftRF legacy protocol.**

The prior "capture is invalid" conclusion was wrong. The signal was there all along; we were looking for the wrong thing.

See `CRITICAL_FINDINGS_2026-10-12.md` for details.

---

# Status Matrix (UPDATED 2026-10-12)

## RF Capture

Control Sample Available:
✅ YES

Capture Validated:
✅ YES (SUPPLEDES prior "INVALID" conclusion)

Evidence:

- Float32 IQ
- 20 MS/s
- ~5.6 second duration
- 12 real RF bursts, 5.14 ms each
- OOK/ASK modulation, coherent phase

---

## Protocol Research

SoftRF firmware citations collected:
✅ YES (for legacy protocol, NOT the captured signal)

Legacy protocol documentation:
✅ YES (for legacy protocol, NOT the captured signal)

Frequency research:
✅ YES (carrier offset ~-0.779 MHz)

Protocol Identification:
❌ NOT COMPLETE (the captured signal is NOT the SoftRF legacy protocol)

---

## Decoding Pipeline

Signal Detection:
✅ CONFIRMED (12 real bursts)

Burst Identification:
✅ CONFIRMED (5.14 ms each)

Carrier Identification:
✅ CONFIRMED (coherent, ~-0.779 MHz offset)

Modulation Classification:
✅ CONFIRMED (OOK/ASK, NOT 2-FSK)

Symbol Recovery:
⚠ PARTIAL (~769 ksym/s, but not yet validated)

Frame Recovery:
❌ NOT PROVEN (don't know the frame structure)

Sync Validation:
❌ NOT PROVEN (don't know the syncword)

CRC Validation:
❌ NOT PROVEN (don't know if there's a CRC)

Payload Recovery:
❌ NOT PROVEN (don't know the payload structure)

Telemetry Decode:
❌ NOT PROVEN (don't know the protocol)

---

# Primary Goal

**Identify the protocol.**

The captured signal is OOK/ASK at ~769 ksym/s. This is NOT the SoftRF legacy protocol. We need to identify what protocol this is before we can decode it.

# Current Working Hypotheses

1. **The signal is a different SoftRF protocol variant** (not "legacy")
   - Status: POSSIBLE
   - Evidence: SoftRF may have multiple protocol variants
   - Action: Search the firmware source for other protocol implementations

2. **The signal is a different radio protocol entirely** (not SoftRF)
   - Status: POSSIBLE
   - Evidence: OOK/ASK at ~769 ksym/s is a distinctive signature
   - Action: Search for OOK/ASK protocols at ~769 ksym/s in the 915 MHz band

3. **The carrier offset is a receiver tuning artifact**
   - Status: POSSIBLE
   - Evidence: The ~-0.779 MHz offset could be a receiver mis-tuning
   - Action: Verify the receiver setup (IF/center frequency, sample rate)

# Success Definition

Control IQ Sample
        ↓
Recovered Frame
        ↓
Passing CRC (if applicable)
        ↓
Decoded Telemetry

Only then is Phase 1 complete.

# Decoder Evidence Ladder (UPDATED)

The decoder progresses through the following stages:

IQ Capture ✅
    ↓
Burst Detection ✅
    ↓
Carrier Identification ✅
    ↓
Modulation Classification ✅ (OOK/ASK)
    ↓
Symbol Recovery ⚠ (PARTIAL — ~769 ksym/s)
    ↓
Frame Recovery ❌
    ↓
Sync Validation ❌
    ↓
CRC Validation ❌
    ↓
Payload Recovery ❌
    ↓
Telemetry Decode ❌

The earliest failing stage is **Frame Recovery**. We know the modulation and symbol rate, but we don't know the frame structure, syncword, or payload format.

# Next Steps

1. **Verify the receiver setup** — What IF/center frequency was used? Was the transmitter actually at 915 MHz?
2. **Check if SoftRF has other protocol variants** — Search the firmware source for OOK/ASK or ASK modulation
3. **Search for OOK/ASK protocols at ~769 ksym/s** in the 915 MHz band
4. **Build a new decoder** for OOK/ASK at ~769 ksym/s
5. **Identify the protocol** — Cross-reference the signal characteristics with known protocols

# Files to Update

- `STATUS.md` — Updated ✅
- `DECODE_STATUS.md` — Updated ✅
- `CURRENT_BLOCKERS.md` — Updated ✅ (this file)
- `REVERSE_ENGINEERING_NOTES.md` — Needs update (add OOK/ASK findings)
- `NOTES.md` — Needs update (add OOK/ASK findings)
- `ANALYSIS_INVALID_CAPTURE.md` — Mark as SUPERSEDED
