# OOK/ASK Decode Attempt

**Date:** 2026-10-13
**Status:** IN PROGRESS - Signal present but SNR too low for basic OOK demodulation

## Signal Characteristics

From detailed envelope analysis:

1. **Envelope is bimodal**:
   - Noise floor: ~0.030 (72.40% of samples)
   - Signal: ~0.225 (0.06% of samples)
   - **10% duty cycle signal at ~0.05 level (1.84% of samples)**

2. **Burst structure**:
   - 100ms windows with ~8.5% duty cycle at 0.05 level
   - Within each 100ms window, 100+ sub-bursts of 30-32ms
   - Sub-bursts at 0.05-0.07 level

3. **Key measurements**:
   - SNR: ~1.67 (0.05 signal / 0.03 noise)
   - Duty cycle: 8.5% (within 100ms windows)
   - Burst duration: 30-32ms
   - Peak envelope: 0.2734

## Problem

**SNR is too low for basic OOK demodulation.**

The signal (0.05 level) is only 1.67x the noise floor (0.03 level). Basic thresholding at 0.05 doesn't give clean bits.

## What I Tried

1. **Basic OOK at 769 ksym/s**: 
   - Extracted 25,089 symbols
   - Got 136 "1" bits out of 25,089
   - Bits are mostly 0, with occasional 1s
   - No clear pattern or sync word

2. **Manchester decode**:
   - No valid Manchester pairs found
   - No sync word detected

## Next Steps (If Time Permits)

1. **Matched filtering**: Correlate with a known pattern (if we can identify one)
2. **Frequency-domain OOK**: Use the carrier frequency to improve SNR
3. **Coherent detection**: Use the known carrier phase (from FSK analysis)
4. **Averaging**: Average multiple bursts to improve SNR
5. **Adaptive thresholding**: Use a threshold that adapts to the noise level

## Files

- `OOK_decoder_v2.py`: First OOK attempt (didn't work)
- `OOK_decoder_v3.py`: Better OOK with burst extraction (still SNR-limited)

## Key Insight

**The signal IS present, but it's very weak.** The 10% duty cycle is real, but the SNR is too low for basic OOK. We need a more sophisticated decoder that can extract the signal from the noise.
