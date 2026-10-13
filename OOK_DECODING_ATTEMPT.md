# OOK/ASK Decoding Attempt

**Date**: 2026-10-13

## Findings

### 1. Signal is OOK/ASK (NOT FSK)
- ✅ Phase is coherent (not random) → NOT FSK
- ✅ Envelope shows clear bimodal distribution (0.03 noise floor, 0.05-0.25 signal peaks)
- ✅ 100ms windows with ~8.5% duty cycle above 0.05 threshold

### 2. Coherent Demodulation
- Rotated by +0.94 rad (phase offset from reality_check.py)
- I channel shows bimodal: -0.026 (92% = OFF) and -0.001 (8% = ON)
- Residual frequency offset: 0.0 Hz

### 3. Threshold Calibration
- Otsu threshold: +0.228 (gives 0% ON - too high)
- 90th percentile: -0.005 (gives 4.3% ON - close to 10%)
- 10th percentile: -0.021 (gives 9.1% ON - close to 10%)

### 4. Problem: Minimum Burst Duration
- Minimum ON run: 1 sample (0.05 ms)
- Minimum OFF run: 1 sample (0.05 ms)
- This is **noise**, not a real OOK symbol

### 5. Conclusion
**The signal has extremely poor SNR.** The OOK bursts are present (100ms windows with 8.5% duty cycle), but the individual symbol-level transitions are buried in noise.

## What We Know
- ✅ Signal is OOK/ASK (not FSK)
- ✅ Signal is present (100ms bursts, 8.5% duty cycle)
- ✅ Phase is coherent (can use coherent demodulation)
- ❌ SNR too low for reliable symbol-level decoding
- ❌ Cannot find sync word in the bitstream

## Possible Next Steps
1. **Use a better demodulation technique** (e.g., matched filter, energy detection)
2. **Average multiple 100ms bursts** to improve SNR
3. **Check if the signal is actually 2-FSK after all** (the phase could be coherent but frequency-varying)
4. **Give up on this capture** - the SNR is too low

## Status
**BLOCKED**: Signal present but SNR too low for reliable decoding.
