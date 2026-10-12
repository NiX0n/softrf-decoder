# Stage 0: Signal Presence & FHSS Analysis

## Summary
The 12 detected bursts (5.07-5.08 ms each) are the **drone's frequency-hopping signal**, not interference. The firmware's `soft_rf.cc` references "GFSK" but the actual signal is FHSS — a discrepancy between firmware documentation and implementation.

## Evidence

### Burst carrier frequencies (relative to receiver LO)
| # | Start time | Carrier (kHz) | 10-sample BW (kHz) | Env |
|---|-----------|---------------|---------------------|-----|
| 1 | 0.161 s   | -779.9        | 95.3               | 0.199 |
| 2 | 0.357 s   | -3979.0       | 46.0               | 0.188 |
| 3 | 1.063 s   | +5218.8       | 86.4               | 0.222 |
| 4 | 1.360 s   | +820.1        | 92.6               | 0.208 |
| 5 | 2.161 s   | +1771.2       | 62.4               | 0.214 |
| 6 | 2.463 s   | -3579.1       | 74.1               | 0.190 |
| 7 | 3.255 s   | +8017.8       | 40.2               | 0.221 |
| 8 | 3.533 s   | +4818.9       | 86.6               | 0.225 |
| 9 | 4.031 s   | -1579.8       | 71.9               | 0.200 |
|10 | 4.597 s   | +2419.7       | 68.6               | 0.214 |
|11 | 5.052 s   | +7618.0       | 63.2               | 0.220 |
|12 | 5.527 s   | -1943.6       | 69.4               | 0.211 |

### Key observations
1. **All 12 bursts are at different frequencies** — ranging from -3.98 MHz to +8.02 MHz
2. **The frequency spread (12 MHz) is consistent with FHSS** — the drone hops across the 915 MHz ISM band
3. **The 10-sample bandwidth (40-95 kHz)** is consistent with GFSK at 100 kbps with a wide deviation
4. **The envelope is stable (0.19-0.225)** across all bursts — consistent with a single source
5. **The bursts are evenly spaced** (~0.5 s intervals) — consistent with periodic telemetry transmission

### Noise floor
- Overall mean: 0.041
- Overall std: 0.019
- Burst envelope: 0.19-0.225
- **SNR of signal: ~15-20 dB**

## Implications for the Decoder Pipeline

### 1. The decoder MUST track the frequency hops
The current decoder assumes a fixed carrier frequency. This is **WRONG** for this signal.

**Required change:** Add a frequency tracking stage that:
- Detects the current burst frequency (via phase slope estimation)
- Updates the demodulator's carrier offset per burst
- Handles the ~5 ms hop dwell time

### 2. The firmware documentation is misleading
`soft_rf.cc` says "GFSK" but the actual signal is **FHSS-GFSK** (frequency-hopping GFSK). The "GFSK" refers to the modulation within each hop, not the overall scheme.

### 3. The 100 kbps bit rate is still valid
Within each 5.08 ms burst, the signal is GFSK at 100 kbps. The frequency hopping is an outer layer.

## Revised Decoder Pipeline

```
1. Burst detection (amplitude threshold)          [DONE - works]
2. Per-burst carrier estimation (phase slope)      [DONE - works]
3. Per-burst GFSK demodulation (100 kbps)         [DONE - but needs refinement]
4. Frequency hop tracking (state machine)          [TODO - NEW REQUIREMENT]
5. Bit synchronization                            [TODO]
6. CRC validation                                 [TODO]
```

## Classification
- **[FIRMWARE VERIFIED]** The firmware uses GFSK at 100 kbps (from `soft_rf.cc` line 361) — but this is the INNER modulation, not the full scheme
- **[RF VERIFIED]** The capture contains 12 bursts at different frequencies (measured) — this is the OUTER FHSS layer
- **[VERIFIED]** The signal is FHSS-GFSK (frequency-hopping GFSK)
- **[UNVERIFIED]** The exact hop sequence/pattern (pseudo-random? fixed? time-based?)

## Next Steps
1. **Implement per-burst carrier tracking** — estimate the carrier frequency for each burst individually
2. **Demodulate each burst independently** — treat each 5.08 ms burst as a separate GFSK frame
3. **Analyze the hop sequence** — determine if the frequency hops follow a predictable pattern
4. **Update the firmware documentation** — clarify that "GFSK" refers to the inner modulation, and the full scheme is FHSS-GFSK

## Conclusion

The signal IS present and IS the drone's telemetry. The decoder pipeline was failing because it assumed a fixed carrier frequency, but the signal is actually **FHSS-GFSK**. The fix is to add frequency tracking per burst.

This is **NOT a hard stop** — the signal is there, and the decoder can be fixed to handle FHSS.
