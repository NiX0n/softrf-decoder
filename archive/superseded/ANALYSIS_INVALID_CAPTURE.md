# Analysis: Invalid Capture Diagnosis

**Date:** 2026-10-12
**Analyst:** Assistant
**Status:** ❌ **SUPERSEDED** — See CRITICAL_FINDINGS_2026-10-12.md

> **CORRECTION (2026-10-20):** This document is fully superseded. The "signal is OOK/ASK"
> conclusion was based on a wrong frequency offset estimate. With the corrected carrier
\u003> removal (-8.733 MHz), the signal shows constant amplitude — it is **FSK**, not OOK/ASK.
\u003> See `SESSION_REPORT_2026-10-20.md`.

> **IMPORTANT:** This analysis was based on the incorrect assumption that the SoftRF
> legacy protocol uses 2-FSK modulation. The signal in the capture is VALID but is
> OOK/ASK at ~769 ksym/s, not 2-FSK at 100 kbps. The "invalid capture" conclusion
> was wrong — the capture is valid, it just contains a different modulation type
> than expected.

---

## Executive Summary (SUPERSEDED)

The captured WAV file (`baseband_915000000Hz_20-35-24_03-10-2026.wav`) does **NOT** contain a valid 2-FSK signal. The signal is a **continuous wave (CW) tone** with very small variations, consistent with LO leakage or a beacon signal. Standard FSK demodulation is impossible with this capture.

---

## Evidence

### 1. Time Domain Analysis

**DC Offset:**
- I mean: +0.0223
- Q mean: −0.0321
- Combined magnitude: 0.0393

**After DC Removal:**
- Mean magnitude: 0.0086
- Std magnitude: 0.0214
- Ratio (std/mean): 2.5 (highly variable)

**Key Finding:** The signal is a **continuous tone** with very small variations. There are **NO distinct bursts** — the "bursts" detected by envelope detection were noise fluctuations.

### 2. Frequency Domain Analysis

**Top FFT Peaks (DC removed):**
| Frequency (kHz) | Magnitude | Interpretation |
|-----------------|-----------|----------------|
| +625.0 | 22,576 | Spur (1/32 of 20 MHz sample rate) |
| +5000.0 | 19,568 | Spur (1/4 of 20 MHz sample rate) |
| +6775.9 | 5,780 | Possible real signal (non-integer frequency) |
| +11250.0 | 4,926 | Spur (9/16 of 20 MHz sample rate) |
| +15000.0 | 3,478 | Spur (3/4 of 20 MHz sample rate) |

**Key Finding:** The dominant energy is at **integer fractions of the sample rate**, which indicates **spurs from the ADC or mixing process**, not a modulated signal. The 6775.9 kHz peak is a possible real signal, but its magnitude (5,780) is much lower than the spurs.

### 3. Phase Analysis

**Instantaneous Frequency:**
- Mean: 0.0 kHz (over 200-sample windows)
- All 11 windows showed 0.0 kHz

**Key Finding:** The phase is **not changing** over time. This is a **CW tone**, not a frequency-modulated signal.

### 4. Envelope Analysis

**Magnitude Over Time (1-second windows):**
| Time (s) | Mean | Std | Max |
|----------|------|-----|-----|
| 0.0-1.0 | 0.0084 | 0.0191 | 0.2209 |
| 1.0-2.0 | 0.0085 | 0.0213 | 0.2410 |
| 2.0-3.0 | 0.0084 | 0.0200 | 0.2332 |
| 3.0-4.0 | 0.0086 | 0.0220 | 0.2480 |
| 4.0-5.0 | 0.0084 | 0.0204 | 0.2377 |
| 5.0-6.0 | 0.0099 | 0.0268 | 0.2460 |

**Key Finding:** The envelope is **uniformly distributed** with no clear burst structure. The 99th percentile (0.185) is only 21x the mean (0.0086), indicating no strong signal peaks.

---

## Conclusion

**The capture is INVALID for FSK demodulation.**

The signal is a **CW tone at ~6.78 MHz relative to the receiver LO**, with very small variations. This is consistent with:
1. **LO leakage** — the receiver's local oscillator is leaking into the baseband
2. **Beacon signal** — a continuous wave beacon from a device
3. **Test tone** — a test signal from the SDR or receiver

**None of these contain the expected 2-FSK modulation with ±50 kHz deviation.**

---

## Root Cause Analysis

The decoder fails at **Stage 3: Carrier Identification** (per `CURRENT_BLOCKERS.md`).

The root cause is **not** in the decoder implementation, but in the **input signal**. The capture does not contain a valid FSK signal.

---

## Recommendations

### Immediate Actions

1. **Document this finding** (done — this document)
2. **Verify the SDR setup** — check that the SDR is configured correctly for 915 MHz reception
3. **Recapture the signal** with a known-good SDR setup

### Diagnostic Steps

To diagnose the SDR setup:
1. **Check the SDR configuration** — ensure the gain, sample rate, and frequency are set correctly
2. **Capture a known signal** — use a signal generator to generate a known FSK signal and capture it
3. **Compare the captures** — if the known signal also shows a CW tone, the SDR is misconfigured
4. **Check the receiver** — ensure the receiver is tuned to the correct frequency

### Alternative Approach

If the capture cannot be fixed, consider:
1. **Find a reference capture** — use a published SoftRF/ADS-B transmission as a test signal
2. **Simulate the signal** — generate a synthetic FSK signal matching the SoftRF spec and test the decoder
3. **Test with a different SDR** — use a different SDR (e.g., RTL-SDR, HackRF, BladeRF) to capture the signal

---

## Next Steps

1. **Confirm the SDR setup** with the user
2. **Recapture the signal** with a known-good setup
3. **Re-run the decoder** with the new capture
4. **Verify the results** — check for syncword, CRC, and payload

---

## Appendix: Signal Analysis Code

The analysis was performed using the following scripts:
- `deep_analysis.py` — time domain, frequency domain, and phase analysis
- `fft_analysis.py` — FFT peak analysis
- `verify_freqplan.py` — frequency plan verification

All scripts are available in the `softrf-decoder` directory.
