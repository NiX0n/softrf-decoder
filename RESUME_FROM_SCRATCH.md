# RESUME FROM SCRATCH — Complete Starting Guide

**Last updated:** 2026-10-20
**Purpose:** Given this repository alone, be able to pick up where we left off.

> **⚠️ THIS FILE IS OUTDATED.** The "TL;DR" section below contains the WRONG
> OOK/ASK conclusion. The authoritative current state is:
>
> **[`SESSION_STATE_2026-10-20.md`](SESSION_STATE_2026-10-20.md)**
>
> Read that file first. Everything below it is historical context.

---

## TL;DR (30-second version) — **OUTDATED 2026-10-20**

> **⚠️ SUPERSEDED:** The OOK/ASK conclusion below was based on a wrong frequency
> offset estimate. The signal IS the SoftRF Legacy protocol (2-FSK, 100 kbps).
> See `SESSION_STATE_2026-10-20.md` for the corrected state.

We're decoding a signal captured at 915 MHz (channel 915000000 Hz, 203524_03-10-2026).
The SoftRF legacy protocol in the firmware is **2-FSK, 100 kbps, ±50 kHz deviation**,
but the captured signal is **NOT that**. It's **OOK/ASK at ~769 ksym/s** with a
**coherent carrier offset of ~-0.779 MHz**. This means:

1. The legacy decoder (FSK_Demodulator_V6.py) **does not work** on this signal.
2. We need to either find the right SoftRF variant that uses OOK/ASK, or
   this is a completely different protocol.

**The signal IS valid.** The "invalid capture" conclusion was based on wrong assumptions.

---

## What we KNOW (verified)

### Signal characteristics
| Property | Value | Confidence |
|----------|-------|------------|
| Center frequency | 915 MHz (channel 915000000) | ✅ From filename |
| Sample rate | 20 MS/s | ✅ From filename/analysis |
| Modulation | FSK (2-FSK, 100 kbps) | ✅ Corrected 2026-10-20 |
| Carrier offset | -8.733 MHz | ✅ Corrected 2026-10-20 |
| Burst SNR | ~29.1 dB | ✅ Corrected 2026-10-20 |
| Protocol | SoftRF Legacy | ✅ Firmware-verified |

---

## File Map (read in this order)

1. **`SESSION_STATE_2026-10-20.md`** — Authoritative current state
2. **`SESSION_REPORT_2026-10-20.md`** — Corrected analysis with evidence
3. **`QUICK_REFERENCE.md`** — All key facts
4. **`REVERSE_ENGINEERING_NOTES.md`** — Protocol spec
5. **`NOTES.md`** — Firmware citations
6. **`SYSTEM_FACTS.md`** — Verified constants
7. **`DEVELOPMENT_RULES.md`** — Rules and methodology
