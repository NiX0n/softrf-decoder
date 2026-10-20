# Long Sample Analysis (2026-01-15)

## Source
- File: `long_baseband_915000000Hz_15-01-19_12-10-2026.wav`
- Size: 4.31 GB (26.92 seconds at 20 MS/s)
- Sample rate: 20,000,000 Hz (from header)
- Data format: float32 interleaved I/Q

## Header Discrepancy
- **Header declares**: 11,534,336 bytes (0.07 seconds)
- **Actual file**: 4,306,501,676 bytes (26.92 seconds)
- **Ratio**: 373x larger than declared
- **Implication**: The header is corrupted or the file was written with an incorrect size field
- **Workaround**: Use actual file size for analysis

## Signal Detection

### Method
1. Read file in 2M-sample chunks (100ms each)
2. Compute RMS and P99/P99.9 for each chunk
3. Identify chunks with RMS > 3x median baseline

### Results
- **Baseline RMS**: 0.0399 (noise floor)
- **Signal RMS**: 0.12-0.39 (3-10x higher than baseline)
- **Total signal regions**: 53 (vs 12 in short sample)
- **Burst spacing**: ~200-600ms (irregular, not uniform)
- **Burst duration**: ~5-10ms each

### Frequency Analysis

#### Original 12 Bursts (Short Sample)
| Burst | F1 (kHz) | F2 (kHz) | Sep (kHz) | RMS |
|-------|----------|----------|-----------|-----|
| 0 | -729.8 | -829.8 | 100 | 0.197 |
| 1 | -4030.0 | -3930.0 | 100 | 0.187 |
| 2 | +5270.3 | +5170.3 | 100 | 0.207 |
| 3 | +870.2 | +770.2 | 100 | 0.207 |
| 4 | +9670.4 | +9570.4 | 100 | 0.213 |
| 5 | -3630.0 | -3530.0 | 100 | 0.189 |
| 6 | +8070.3 | +7970.3 | 100 | 0.206 |
| 7 | +4770.2 | +4870.2 | 100 | 0.210 |
| 8 | -1529.8 | -1629.8 | 100 | 0.187 |
| 9 | +2470.2 | +2370.2 | 100 | 0.212 |
| 10 | +7670.3 | +7570.3 | 100 | 0.205 |
| 11 | -9529.6 | -9629.6 | 100 | 0.210 |

**All bursts show exactly 100 kHz FSK separation** (matches SoftRF spec)

#### New Signal Regions (Long Sample)
| Time (ms) | F1 (kHz) | F2 (kHz) | Sep (kHz) | RMS |
|-----------|----------|----------|-----------|-----|
| 575-585 | -5130.3 | -5230.3 | 100 | 0.205 |
| 735-745 | -2330.3 | -2430.3 | 100 | 0.275 |
| 1380-1390 | -1130.2 | -1230.2 | 100 | 0.273 |
| 1740-1750 | -9630.0 | -9530.0 | 100 | 0.205 |

**Also 100 kHz FSK separation** (consistent with SoftRF spec)

## Key Findings

1. **FSK Confirmed**: 100 kHz separation in all bursts (both samples)
2. **FHSS Confirmed**: Frequencies spread across the 902-928 MHz band
3. **Long Sample Has More Data**: 53 signal regions vs 12 in short sample
4. **Different Gain Settings**: Long sample has higher RMS (0.27-0.39 vs 0.19-0.21)
5. **Irregular Burst Timing**: ~200-600ms spacing (not uniform like the 20ms in short sample)
6. **Header Corruption**: Long sample has incorrect data size in header

## Implications for Demodulation

### Problem
The current approach of measuring F0/F1 in the middle of a burst fails because:
- The frequency is changing rapidly (FHSS)
- A 10ms burst spans multiple frequency hops
- The "middle" of the burst is arbitrary and may be in a transition

### Solution: Divide and Conquer Strategy

Instead of trying to demodulate the entire burst at once, we should:

1. **Identify frequency hops** within each burst
2. **Estimate F0/F1 per hop** (not per burst)
3. **Demodulate each hop segment** separately
4. **Stitch the results** together

### Alternative: Correlation-Based Demodulation

Instead of measuring F0/F1, use correlation with known FSK templates:
- Generate reference FSK waveforms for each possible frequency
- Correlate the received signal with each reference
- The frequency with the highest correlation is the transmitted tone

This approach is more robust to frequency drift and noise.

## Next Steps

1. **Implement per-hop F0/F1 estimation** within each burst
2. **Implement correlation-based demodulation** as an alternative
3. **Test both approaches** on the long sample
4. **Compare results** with the 12-burst sample to validate

## References
- SoftRF FSK spec: 100 kHz separation
- SoftRF FHSS spec: 25.6 MHz band (902.2-927.8 MHz)
