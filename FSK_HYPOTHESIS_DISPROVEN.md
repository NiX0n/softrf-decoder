# FSK Hypothesis — DISPROVEN

**Date:** 2026-10-12
**Status:** **DISPROVEN**

## What Was Assumed

For most of the session, the capture was assumed to be a **2-FSK (GFSK) signal**
based on the SoftRF legacy firmware protocol documentation:

- **Modulation:** 2-FSK (Gaussian-filtered FSK)
- **Symbol rate:** 100 kbps
- **Deviation:** ±50 kHz (documented) / ±14 kHz (observed in earlier analysis)
- **Encoding:** Manchester
- **Syncword:** `55 99 A5 A9 55 66 65 96`
- **Cipher:** XXTEA
- **CRC:** CCITT

## Why It Was Disproven

On 2026-10-12, signal analysis revealed that the captured signal does **NOT**
exhibit the characteristics of a 2-FSK signal:

1. **No two-tone FSK structure**: FFT shows a single dominant peak, not two
   distinct frequency tones separated by ~28-100 kHz.
2. **Amplitude variation present**: The signal has ~17% amplitude variance
   (min 0.019, max 0.033), which is inconsistent with FSK (which preserves
   constant envelope).
3. **Symbol rate wrong**: The dominant run length is ~26 samples (0.39 µs
   per symbol at 20 Msps = ~2.56 Msps), not 20 µs per symbol (100 kbps).
4. **Coherent phase structure**: The phase rotates in a coherent way,
   consistent with OOK/ASK or PSK, not FSK.

## Consequence

The **legacy 2-FSK decoder** (`softrf_decoder.py`) is **NOT applicable** to this
signal. The decoder is built for a different modulation scheme.

## Affected Scripts (FSK-specific)

The following scripts were written for the FSK hypothesis and should be treated
as **obsolete** or **not applicable** to the current capture:

| Script | Purpose | Status |
|--------|---------|--------|
| `fsk_demod.py` | FSK demodulator v2 | **OBSOLETE** — FSK disproven |
| `demodulate_hops.py` | FHSS-FSK demodulator | **OBSOLETE** — FSK disproven |
| `fft_analysis.py` | FFT-based FSK analysis | **OBSOLETE** — FSK disproven |
| `fix_sync.py` | FSK sync word alignment | **OBSOLETE** — FSK disproven |

## What Was Verified Instead

The signal is **OOK/ASK** (on-off keying / amplitude shift keying):
- ~10% duty cycle
- ~769 ksym/s symbol rate
- Coherent carrier offset (~-0.779 MHz)
- 12 distinct bursts, each ~5.14 ms long

See `CRITICAL_FINDINGS_2026-10-12.md` for the full evidence.

## Scripts That Remain Valid

These scripts are **NOT FSK-specific** and can still be used:

| Script | Purpose | Status |
|--------|---------|--------|
| `characterize.py` | Signal characterization (amplitude, frequency, phase) | **VALID** |
| `measure_symbols.py` | Symbol rate measurement | **VALID** |
| `extract_bitstream.py` | Bitstream extraction (generic) | **VALID** |
| `protocol_analysis.py` | Protocol analysis (generic) | **VALID** |
| `check_signal.py` | Signal check (generic) | **VALID** |
| `OOK_Demodulator_v1.py` | OOK/ASK demodulator prototype | **NEW** — current hypothesis |

## How to Proceed

1. **Do NOT use** the FSK-specific scripts for the current capture.
2. **Use** the OOK/ASK demodulator (`OOK_Demodulator_v1.py`) or build a new
   one based on the OOK/ASK hypothesis.
3. **Search** for other SoftRF protocols (OOK/ASK, ASK, PSK) in the firmware.
4. **Verify** the receiver center frequency to ensure the carrier is within
   the IF bandwidth.

## References

- `CRITICAL_FINDINGS_2026-10-12.md` — Full evidence for OOK/ASK
- `ANALYSIS_INVALID_CAPTURE.md` — Marked as SUPERSEDED
- `STATUS.md` — Current status
- `RESUME_FROM_SCRATCH.md` — How to proceed
