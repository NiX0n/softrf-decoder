# Session Findings

**Date**: 2026-10-19 (consolidated from 2026-10-13 + 2026-10-19 sessions)
**CORRECTED**: 2026-10-20 — see correction note below; several findings in this document are superseded.

---

> ## ⚠️ CRITICAL CORRECTION (2026-10-20)
>
> The frequency offset analysis was wrong in all prior sessions.
> - **Corrected carrier offset: -8.733 MHz** (prior estimates: +11.23 MHz, -0.779 MHz)
> - **After removing the correct carrier, amplitude is constant** (std/mean = 0.144)
>   → **OOK/ASK classification REJECTED**
>   → **Signal is FSK**, consistent with the SoftRF Legacy protocol spec
> - **Burst SNR: ~29.1 dB** (not "low") — sufficient for FSK decoding
> - **Two-component spectrum** (-8.733 / -8.833 MHz) consistent with FSK deviation
>
> See `SESSION_REPORT_2026-10-20.md` for full analysis. Documents claiming
> "OOK/ASK", "SNR too low", or "FSK disproven" are superseded.

---

## Proven Findings

### 1. SoftRF Legacy Firmware Is 2-FSK @ 100 kbps (FIRMWARE VERIFIED)

**Source**: `Legacy.h:145`, `Legacy.cpp:90`, `NOTES.md`

The firmware source code specifies:
- **Modulation**: 2-FSK (Gaussian Frequency Shift Keying / GFSK)
- **Data rate**: 100 kbps
- **Frequency deviation**: ±30 kHz (433 MHz), ±25 kHz (868 MHz), ±18 kHz (915 MHz)
- **Sync word**: `55 99 A5 A9 55 66 65 96` (8 bytes)
- **Frame structure**: Sync + Length + Payload + CRC-16 (CCITT-F, pre-seed `0x31, 0xFA, 0xB6`)
- **Channel encoding**: 2:1 repeat (each bit transmitted twice)
- **Bit order**: LSB first

**Citation**:
```
Legacy.h:145:
  "100 kbps
   2-FSK
   Gaussian Frequency Shift Keying (GFSK) modulation"

Legacy.cpp:90:
  "Data rate: 100 kbps
   2-FSK"
```

**Classification**: `[FIRMWARE VERIFIED]` — This is what the firmware code specifies, not what the captured signal shows.

---

### 2. Captured Signal Is OOK/ASK, Not FSK (RF VERIFIED)

**Source**: Direct analysis of `baseband_915000000Hz_20-35-24_03-10-2026.wav` and `silence_baseband_915000000Hz_18-23-16_19-10-2026.wav`

**Evidence**:
1. **Phase is coherent** (not random as required for FSK)
2. **FFT shows single dominant peak** (not two FSK tones)
3. **Envelope is bimodal** (0.03 noise floor, 0.05–0.25 signal peaks)
4. **Coherent demodulation** shows I channel with clear ON/OFF structure

**Classification**: `[RF VERIFIED]` — This is what the captured signal actually contains.

**Conclusion**: The captured signal is **NOT** using the SoftRF Legacy firmware's 2-FSK protocol. The signal is OOK/ASK (On-Off Keying / Amplitude Shift Keying).

---

### 3. Burst Structure (RF VERIFIED)

**Source**: Analysis using silence capture as noise floor (2026-10-19)

**Burst count**: 12 consistent bursts

**Burst duration**: ~5.17 ms (σ = 0.010 ms, very tight)

**Burst spacing**: Irregular (190–796 ms)

**Duty cycle**: ~1.1%

**SNR**: ~13.3 dB

**Burst timings** (relative to capture start):
```
1:  12.34 ms
2:  137.12 ms
3:  215.51 ms
4:  354.08 ms
5:  455.16 ms
6:  585.11 ms
7:  685.39 ms
8:  806.08 ms
9:  985.97 ms
10: 1067.08 ms
11: 1230.01 ms
12: 1396.86 ms
```

**Classification**: `[RF VERIFIED]` — Measured directly from the captures.

**Important**: This contradicts the earlier "100ms bursts" estimate. The correct structure is **12 × 5.17ms bursts**, not continuous 100ms windows.

---

## Disproven Hypotheses

### 1. 2-FSK Hypothesis (DISPROVEN)

**Hypothesis**: The captured signal uses 2-FSK modulation as specified in the SoftRF Legacy firmware.

**Evidence Against**:
1. **Coherent phase** — FSK signals have random phase transitions (GFSK), but this signal has coherent phase
2. **Single FFT peak** — FSK should show two tones (mark + space), but only one dominant peak is present
3. **Bimodal envelope** — FSK has constant envelope, but this signal has clear ON/OFF amplitude structure

**Conclusion**: The signal is **NOT 2-FSK**. It is **OOK/ASK**.

**Status**: **DISPROVEN** (2026-10-13)

**Implication**: The SoftRF Legacy firmware's 2-FSK decoder path is **not applicable** to this captured signal. A different protocol or device variant must be involved.

---

### 2. "100ms Bursts" Hypothesis (DISPROVEN)

**Hypothesis**: The signal contains ~100ms burst windows with ~8.5% duty cycle.

**Evidence Against**:
- Direct measurement using silence capture as noise floor reveals **12 × 5.17ms bursts** with irregular spacing
- The 100ms estimate was an artifact of thresholding too low, causing noise to be counted as signal

**Conclusion**: The actual burst structure is **12 short bursts (~5.17ms each)**, not long 100ms windows.

**Status**: **DISPROVEN** (2026-10-19)

---

## Confidence Levels

| Finding | Confidence | Basis |
|---------|------------|-------|
| Firmware is 2-FSK @ 100kbps | **HIGH** | Direct firmware source code (`Legacy.h:145`, `Legacy.cpp:90`) |
| Captured signal is OOK/ASK | **MEDIUM-HIGH** | Multiple independent tests (phase, FFT, envelope) all agree |
| Burst structure (12 × 5.17ms) | **MEDIUM** | Measured from one capture, but consistent across analysis methods |
| SNR is the blocker | **HIGH** | Consistent across all demodulation attempts |
| Firmware ≠ captured signal | **MEDIUM** | Different modulation types, but could be different firmware variant or misconfiguration |

---

## Next Steps

### Immediate (Blocking)
1. **Obtain higher-SNR capture** — The current SNR (~13.3 dB) is too low for reliable OOK/ASK bit-level decoding
2. **Analyze the new 397s capture** (`long_baseband_915000000Hz_18-26-17_19-10-2026.wav`) — May have better SNR or more burst samples
3. **Verify device type** — Is this actually a SoftRF device, or a different OOK/ASK transponder?

### Investigation
4. **Search SoftRF firmware for OOK/ASK paths** — The `P3I` and other modules may support OOK in addition to FSK
5. **Check if 100kbps 2-FSK is actually being transmitted** — The OOK could be a preamble or different protocol layer
6. **Compare with known OOK/ASK protocols** — Could be a different transponder entirely (not SoftRF)

### Documentation
7. **Create `CAPTURE_CONFIDENCE_REPORT.md`** — Assess all captures including the new 397s one
8. **Update `SYSTEM_FACTS.md`** — Add the OOK/ASK finding and the discrepancy with firmware
9. **Update `CURRENT_BLOCKERS.md`** — Reflect the new state (SNR, OOK/ASK mismatch)

---

## Open Questions

1. **Is this actually a SoftRF device?** The firmware specifies 2-FSK, but the signal is OOK/ASK. Could be:
   - A different SoftRF firmware variant
   - A different device entirely
   - A misconfiguration
   - A different protocol layer (OOK preamble + FSK payload?)

2. **What is the actual data rate?** 100kbps FSK would give 10μs bits. OOK at ~769 ksym/s (from earlier analysis) would give ~1.3μs symbols. Which is it?

3. **What is the frame structure?** No sync word has been found in the OOK signal. Is there a different sync mechanism?

4. **Why 12 bursts with irregular spacing?** This is unusual for a telemetry system. Could be:
   - A handshake protocol
   - Location ping (12 = 12 satellites?)
   - A different communication pattern

---

## Summary

| Item | Status |
|------|--------|
| Protocol identified | **NO** — Firmware says 2-FSK, signal shows OOK/ASK |
| Signal decoded | **NO** — SNR too low |
| Sync word found | **NO** — No sync word in OOK signal |
| Firmware source traced | **YES** — `Legacy.h`, `Legacy.cpp`, `radiolib_extra.cpp` |
| Confidence in firmware spec | **HIGH** |
| Confidence in signal type | **MEDIUM-HIGH** |
| **Overall status** | **BLOCKED** — SNR + protocol mismatch |
