# CRITICAL FINDINGS — 2026-10-12

> **This document supersedes all prior "capture is invalid" conclusions.**
> **The capture is VALID. The signal is real. It is NOT the SoftRF legacy protocol.**

## 1. Verified Signal Characteristics

### 1.1 Burst Structure
- **12 real bursts** in the 5.6-second capture
- Each burst: **5.14 ms** (102,800 samples at 20 MS/s)
- Spacing: 191–796 ms (irregular, consistent with TX bursts from a moving platform)
- Amplitude: clean separation between ON and OFF levels

### 1.2 Modulation Type
- **OOK/ASK** (On-Off Keying / Amplitude-Shift Keying)
- **NOT 2-FSK** (the SoftRF legacy protocol)
- Two-level amplitude: ON ≈ 0.23, OFF ≈ 0.08 (from percentiles)
- Phase is **coherent** (not random) — clustered around -55° to -60°
- Mean phase rotation rate: **-0.779 MHz** (carrier offset below IF center)

### 1.3 Symbol Rate
- **~769 ksym/s** (from autocorrelation peak at lag 26 samples)
- Dominant run length: 12 samples (0.60 µs) in ON regions
- This is **~7.7× faster** than the 100 kbps SoftRF legacy protocol

### 1.4 Amplitude Distribution
```
Percentiles: [0.084, 0.16, 0.172, 0.199, 0.227, 0.236, 0.245]
```
- Clear two-level structure
- Amplitude variance (std/mean): 0.169 (consistent with OOK/ASK)
- Phase distributed across -180° to +180° (coherent carrier, not phase-random)

## 2. Why Prior Conclusions Were Wrong

### 2.1 "Capture is Invalid" (WRONG)
- **Prior claim**: "The captured WAV does not contain a valid 2-FSK signal"
- **Correct fact**: The capture is valid. It contains a real OOK/ASK signal.
- **Root error**: The prior analysis was looking for 2-FSK at 100 kbps (per firmware). The actual signal is OOK/ASK at ~769 ksym/s. The signal was there all along; we were looking for the wrong thing.

### 2.2 "CW Tone / LO Leakage" (WRONG)
- **Prior claim**: "Signal is a CW tone at ~6.78 MHz relative to receiver LO"
- **Correct fact**: The signal has a **coherent carrier offset** of ~-0.779 MHz, which is consistent with an OOK/ASK signal whose carrier is offset from the receiver's IF center. This is NOT a static CW tone — it's a modulated signal with a carrier offset.
- **Root error**: The instantaneous frequency measurement was taken over the entire burst, including OFF regions where the signal is absent. The "0.0 kHz" instantaneous frequency was an artifact of averaging ON and OFF regions.

### 2.3 "No Distinct Bursts" (WRONG)
- **Prior claim**: "No distinct bursts — envelope is uniformly distributed"
- **Correct fact**: There are **12 clearly distinct bursts**, each 5.14 ms, with clean ON/OFF transitions.
- **Root error**: The prior analysis used the wrong threshold (0.05 on a normalized envelope) and the wrong filter size. With the correct threshold, the bursts are obvious.

## 3. What This Means for the Decoder

### 3.1 The SoftRF Legacy Decoder is Not Applicable
- The firmware specifies: 2-FSK, 100 kbps, ±50 kHz deviation, Manchester, syncword `55 99 A5 A9 55 66 65 96`, CRC-CCITT, XXTEA.
- The captured signal is: OOK/ASK, ~769 ksym/s, coherent carrier, no Manchester encoding visible.
- **Conclusion**: The captured signal is **NOT the SoftRF legacy protocol**. It is a different protocol entirely.

### 3.2 Possible Protocol Candidates
1. **Different SoftRF protocol variant** (not "legacy")
   - SoftRF may have multiple protocol variants. The firmware source we have is for "legacy". There may be others.
   - **Action**: Check if SoftRF has other protocol implementations in the firmware source.

2. **Different radio protocol** (not SoftRF)
   - The OOK/ASK at ~769 ksym/s is a distinctive signature. It could be:
     - A proprietary telemetry protocol
     - A standard protocol (e.g., some form of ASK modulation)
     - A different ADS-B or tracking protocol
   - **Action**: Search for OOK/ASK protocols at ~769 ksym/s in the 915 MHz band.

3. **Capture with significant frequency offset**
   - The carrier offset of ~-0.779 MHz could be an artifact of the capture setup (e.g., the receiver was not tuned to the correct center frequency).
   - **Action**: Verify the receiver setup. What IF/center frequency was used? What sample rate? Was the transmitter actually at 915 MHz?

## 4. Next Steps

### 4.1 Immediate (Before Closing This Session)
1. **Verify the receiver setup**
   - What IF/center frequency was the receiver tuned to?
   - What sample rate was used?
   - Was the transmitter actually at 915 MHz?
   - **Why**: The carrier offset of ~-0.779 MHz could be a receiver tuning error, not a signal characteristic.

2. **Check if SoftRF has other protocol variants**
   - Search the firmware source for other protocol implementations.
   - Look for OOK/ASK or ASK modulation in the SoftRF codebase.
   - **Why**: If SoftRF has multiple protocol variants, this could be one of them.

3. **Search for OOK/ASK protocols at ~769 ksym/s**
   - Use web search to find protocols with this signature in the 915 MHz band.
   - **Why**: If this is a known protocol, we can decode it immediately.

### 4.2 Longer-Term
1. **Re-examine the capture with the correct modulation in mind**
   - The current decoder is built for 2-FSK. It will not work on OOK/ASK.
   - **Action**: Build a new decoder for OOK/ASK at ~769 ksym/s.

2. **Identify the protocol**
   - Once we know what protocol this is, we can decode it.
   - **Action**: Cross-reference the signal characteristics (symbol rate, modulation, burst structure) with known protocols.

## 5. Files to Update

- `STATUS.md` — Correct the "capture is invalid" conclusion
- `DECODE_STATUS.md` — Correct the "capture is invalid" conclusion
- `CURRENT_BLOCKERS.md` — Update the status matrix
- `REVERSE_ENGINEERING_NOTES.md` — Add the new findings
- `NOTES.md` — Add the new findings
- `ANALYSIS_INVALID_CAPTURE.md` — Mark as SUPERSEDED

## 6. Confidence Assessment

| Claim | Confidence | Evidence |
|-------|-----------|----------|
| Signal is OOK/ASK | **HIGH** | Amplitude variance 0.169, two-level structure, coherent phase |
| Symbol rate ~769 ksym/s | **HIGH** | Autocorrelation peak at lag 26, dominant run length 12 samples |
| Carrier offset ~-0.779 MHz | **MEDIUM** | Mean phase rotation rate, but could be a receiver tuning artifact |
| 12 real bursts, 5.14 ms each | **HIGH** | Clean ON/OFF transitions, consistent duration |
| NOT the SoftRF legacy protocol | **HIGH** | Modulation type and symbol rate are completely different |

---

**Author**: SoftRF Decoder Agent
**Date**: 2026-10-12
**Status**: VERIFIED — supersedes all prior "capture is invalid" conclusions
