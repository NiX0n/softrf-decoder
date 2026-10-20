# Session Report — 2026-10-19/20 (CRITICAL CORRECTION)

## Executive Summary

**The OOK/ASK hypothesis is REJECTED.** The latest detailed burst analysis (Oct 19)
reveals that after removing the carrier, the signal shows **constant amplitude**
(std/mean = 0.144), which is **inconsistent with OOK/ASK** and **consistent with
FSK**. The FSK hypothesis must be **re-examined** — it was prematurely disproven.

The dominant frequency offset is **-8.733 MHz** (with a strong component at
-8.833 MHz), not the previously estimated +11.23 MHz. After carrier removal, a
residual frequency offset of **-47.3 kHz** remains.

**Overall Status**: REOPENED — FSK hypothesis is back in play.

---

## What Changed

### Previous Understanding (Oct 12-13)
- Signal is OOK/ASK (not FSK) — "proven" by envelope bimodality
- FSK disproven by lack of two-tone structure
- SNR too low for decoding
- 12 bursts of ~5.17 ms each
- Duty cycle ~1.1%

### New Findings (Oct 19)
1. **Frequency offset corrected**: Dominant offset is **-8.733 MHz** (not +11.23 MHz)
2. **Constant amplitude after carrier removal**: std/mean = 0.144 → NOT OOK
3. **79 burst regions** in the 30.4s capture (not 12)
4. **Burst SNR ~29.1 dB** (much better than the 13.3 dB previously reported)
5. **Residual frequency offset**: -47.3 kHz after carrier removal
6. **Typical burst duration**: ~5.3 ms (consistent with prior finding)

---

## Evidence for FSK (Re-examination)

### 1. Constant Amplitude (KILLER EVIDENCE)
After removing the -8.733 MHz carrier:
- Mean magnitude: 1.225
- Std magnitude: 0.176
- **Variation ratio: 0.144 (14.4%)**

OOK/ASK would show **large amplitude variation** (ON vs OFF states, typically
>50% variation). 14.4% is consistent with:
- FSK (constant envelope)
- Phase noise
- Minor AM sidebands

### 2. Two-Component Spectrum
- Dominant peak at -8.733 MHz
- Second strong component at -8.833 MHz
- This 100 kHz separation is consistent with FSK frequency deviation

### 3. Residual Frequency Offset
- After carrier removal: -47.3 kHz
- This is consistent with FSK modulation (symbols shifting frequency around the carrier)

### 4. Burst Duration
- ~5.3 ms bursts (79 in 30.4s)
- Consistent with short data frames

---

## Why the OOK/ASK Conclusion Was Wrong

The Oct 12-13 analysis claimed OOK/ASK based on:
1. "Bimodal envelope" — This was likely the **envelope of the FSK signal** (constant
   amplitude + noise = appears as a single cluster, not truly bimodal)
2. "Coherent phase" — FSK also has coherent phase (it's continuous)
3. "No two-tone structure" — The two tones may have been too close to resolve at
   the analysis frequency, or the carrier offset was wrong (was +11.23 MHz, not
   -8.733 MHz)

**Root cause**: The frequency offset was estimated incorrectly (+11.23 MHz instead
of -8.733 MHz). This led to incorrect carrier removal, which in turn led to
incorrect amplitude analysis.

---

## Confidence Reassessment

| Hypothesis | Previous | Current | Basis |
|-----------|----------|---------|-------|
| FSK | DISPROVEN | **REOPENED** | Constant amplitude, two-component spectrum |
| OOK/ASK | CONFIRMED | **REJECTED** | 14.4% amplitude variation (too low for OOK) |
| PSK | Not considered | POSSIBLE | Constant amplitude, coherent phase |
| Different protocol | POSSIBLE | STILL OPEN | 79 bursts, 5.3ms each |

---

## Firmware Context (Unchanged)

The SoftRF Legacy firmware specifies:
- **2-FSK (GFSK)** at 100 kbps
- **Deviation**: ±18 kHz (915 MHz)
- **Sync word**: `55 99 A5 A9 55 66 65 96`
- **Encryption**: XXTEA (btea)
- **CRC**: CCITT-F

This is **consistent with the new FSK findings**. The firmware says FSK, and the
signal now shows FSK characteristics.

---

## What This Means

1. **The original FSK decoder path may be valid** — it was "disproven" based on
   incorrect carrier offset analysis
2. **The SoftRF Legacy protocol may be the correct protocol** — FSK + known sync
   word + known encryption
3. **The 79 bursts in 30.4s** give much more data to work with than the 12 bursts
   previously identified
4. **SNR is actually ~29 dB** — this is good enough for reliable FSK demodulation!

---

## Recommended Next Steps

### Priority 1: FSK Demodulation (NEW)
1. Remove the -8.733 MHz carrier (NOT +11.23 MHz)
2. Apply FM demodulation (quadrature discriminator or arctangent)
3. Look for the SoftRF Legacy sync word: `55 99 A5 A9 55 66 65 96`
4. Apply XXTEA decryption
5. Verify CRC

### Priority 2: Burst Analysis
1. Extract all 79 bursts from the 30.4s capture
2. Measure burst durations, spacing, and frequency content
3. Look for frame structure patterns

### Priority 3: Capture Analysis
1. Apply the same analysis to the 397s capture (4.6 GB)
2. More bursts = better statistics
3. Look for different frame types

---

## Documentation Status

| Document | Status | Action Needed |
|----------|--------|---------------|
| `FSK_HYPOTHESIS_DISPROVEN.md` | **SUPERSEDED** | Mark as superseded |
| `CRITICAL_FINDINGS_2026-10-12.md` | **PARTIALLY SUPERSEDED** | Add correction note |
| `SESSION_SUMMARY_2026-10-13.md` | **PARTIALLY SUPERSEDED** | Add correction note |
| `OOK_DECODING_ATTEMPT.md` | **SUPERSEDED** | Mark as superseded |
| `QUICK_REFERENCE.md` | **OUTDATED** | Update with FSK findings |
| `CURRENT_BLOCKERS.md` | **OUTDATED** | Update with new findings |
| `STATUS.md` | **OUTDATED** | Update with new findings |
| `DECODE_STATUS.md` | **OUTDATED** | Update with new findings |
| `REVERSE_ENGINEERING_NOTES.md` | **VALID** | FSK protocol spec still applies |
| `SESSION_FINDINGS.md` | **NEEDS UPDATE** | Add FSK re-examination |
| `CAPTURE_CONFIDENCE_REPORT.md` | **PARTIALLY SUPERSEDED** | Add correction |
| `DOCUMENTATION_COMPLIANCE_REPORT.md` | **PARTIALLY SUPERSEDED** | Add correction |

---

## Files Created/Updated

### New
- `SESSION_REPORT_2026-10-20.md` — This file
- `burst_analysis_detail.png` — Burst analysis visualization

### Updated
- `CURRENT_BLOCKERS.md` — Added new findings
- `SESSION_FINDINGS.md` — Added FSK re-examination
- `QUICK_REFERENCE.md` — Updated with FSK findings
- `STATUS.md` — Updated status
- `DECODE_STATUS.md` — Updated decode status

---

## Conclusion

**The signal is most likely FSK, not OOK/ASK.** The original "FSK disproven"
conclusion was based on an incorrect frequency offset estimate. With the corrected
offset (-8.733 MHz), the signal shows constant amplitude (FSK characteristic) and
a two-component spectrum consistent with FSK frequency deviation.

**The SoftRF Legacy firmware protocol (2-FSK, 100 kbps, XXTEA, CCITT) is the
most likely candidate.** The FSK decoder path should be re-examined with the
corrected carrier offset.

**SNR is actually ~29 dB** — this is sufficient for reliable FSK demodulation.

**Next step**: Apply FM demodulation with the corrected carrier offset and search
for the SoftRF Legacy sync word.

---

*End of session report — 2026-10-20 05:00 UTC*
