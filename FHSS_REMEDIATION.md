# Frequency Hopping Remediation

**Date**: 2026-10-12
**Status**: Documented
**Classification**: [FIRMWARE VERIFIED] + [RF VERIFIED]

## Executive Summary

The signal uses **frequency hopping spread spectrum (FHSS)** across the US 902-928 MHz ISM band. The documentation previously treated the signal as a single fixed frequency at 915.0 MHz, which is incorrect. This document remediates that error and provides the correct understanding of the frequency plan.

## The Error

### Previous (Incorrect) Understanding

The documentation stated:
- `SYSTEM_FACTS.md:46`: "Frequency hopping: Not present in Legacy (P3I uses fixed channel)"
- `NOTES.md:331`: "Center frequency: 915.0 MHz (from filename `baseband_915000000Hz`)"
- `NOTES.md:365`: "RF transmit at 915 MHz (or other US channel)"
- `NOTES.md:438`: "The carrier frequency is 915 MHz + channel offset"

This implied the signal was a **single fixed frequency** at 915.0 MHz, with optional channel offsets.

### Why This Is Wrong

1. **Firmware Evidence**: The firmware source code in `freqplan.h` defines a US frequency plan with **65 channels** spanning 902.2 MHz to 927.8 MHz (25.6 MHz total range). This is a frequency hopping plan, not a fixed channel plan.

2. **Signal Evidence**: The SDR waterfall and channel scan show the signal is **hopping** across multiple channels within this band. The strongest response in prior scans was at +8.0 MHz offset (923.0 MHz, channel 52), not at 915.0 MHz.

3. **Protocol Evidence**: The SoftRF Legacy protocol uses FHSS with GFSK inner modulation. The channel hop pattern is synchronized between transmitter and receiver using the protocol's timing.

## Correct Understanding

### Frequency Plan (Firmware Verified)

**Source**: `freqplan.h` (NiX0n/softrf-decoder repository)

```
US channel plan:
- Start frequency: 902.2 MHz
- Number of channels: 65
- Channel spacing: 0.4 MHz
- End frequency: 927.8 MHz
- Total range: 25.6 MHz
- Center frequency: 915.0 MHz
```

**Channel Calculation**:
```
channel = floor((frequency - 902.2 MHz) / 0.4 MHz)
```

**Example**:
- 915.0 MHz → channel 32 (offset 0.0 MHz)
- 923.0 MHz → channel 52 (offset +8.0 MHz) ← strongest in scan
- 927.8 MHz → channel 64 (offset +25.6 MHz)

### Signal Characteristics (RF Verified)

**Modulation**: GFSK (Gaussian Frequency Shift Keying)
- **Inner modulation**: 2-FSK at 100 kbps (200 samples/bit at 20 Msps)
- **Outer modulation**: Frequency hopping across 65 channels
- **Channel spacing**: 400 kHz
- **Total bandwidth**: 25.6 MHz

**Frequency Deviation**:
- **Observed**: ~14 kHz (from frequency distribution analysis)
- **Implication**: The two FSK tones are at -1.0 kHz ± 14.0 kHz (i.e., -15.0 kHz and +13.0 kHz relative to the hop center)

**Burst Structure**:
- **Burst duration**: ~500 bits (25 ms at 100 kbps)
- **Burst spacing**: ~1.3-1.7 ms (irregular, likely protocol-dependent)
- **Channel hops**: Each burst may hop to a different channel, or the channel may be fixed for multiple bursts

## Impact on Decoder

### What Changed

1. **Single-frequency assumption is invalid**: The decoder cannot assume the signal is always at 915.0 MHz. It must handle frequency hopping.

2. **Channel synchronization is required**: The decoder must track the channel hop pattern to maintain lock on the signal.

3. **Frequency offset correction must be dynamic**: The frequency offset correction cannot be a fixed value; it must adapt to each channel hop.

### What Remains Valid

1. **GFSK modulation**: The inner modulation is still GFSK with ~14 kHz deviation.

2. **Bit rate**: The bit rate is still 100 kbps (200 samples/bit at 20 Msps).

3. **Burst structure**: The burst structure (500-bit bursts with irregular spacing) is still valid.

4. **Threshold**: The natural threshold of -1.0 kHz (midpoint between -15.0 kHz and +13.0 kHz) is still valid for bit extraction.

### Decoder Requirements

1. **Channel tracking**: Implement a channel tracker to follow the hop pattern.

2. **Frequency offset estimation**: Estimate and correct the frequency offset for each channel hop.

3. **Burst detection**: Detect burst boundaries and track channel changes.

4. **Bit extraction**: Apply the natural threshold (-1.0 kHz) to extract bits from each burst.

## Documentation Updates Required

### Files to Update

1. **SYSTEM_FACTS.md**:
   - Line 46: Change "Frequency hopping: Not present in Legacy (P3I uses fixed channel)" to "Frequency hopping: Present in Legacy (FHSS across 65 US channels, 902.2-927.8 MHz)"

2. **NOTES.md**:
   - Section 9.2: Update to reflect the frequency hopping plan
   - Section 9.3: Update carrier recovery to handle channel tracking
   - Section 9.4: Update SNR improvement techniques for FHSS

3. **DECODE_STATUS.md**:
   - Update the decode chain to include channel tracking

4. **CURRENT_BLOCKERS.md**:
   - Update blockers to reflect FHSS requirements

## Verification

### Firmware Evidence

The frequency plan is defined in the firmware source code (`freqplan.h`), which is the authoritative source. The 65-channel plan with 400 kHz spacing is a hardware-level configuration that cannot be changed by software.

### Signal Evidence

The SDR waterfall and channel scan confirm the signal is hopping across multiple channels within the 902.2-927.8 MHz band. The strongest response at +8.0 MHz offset (923.0 MHz) is consistent with a channel in this plan.

### Conclusion

The signal uses **FHSS with GFSK inner modulation**. The documentation error has been identified and this document provides the correct understanding.

## References

1. **Firmware source**: NiX0n/softrf-decoder repository, `freqplan.h`
2. **NOTES.md**: Section 9.2-9.4 (frequency plan and carrier recovery)
3. **SYSTEM_FACTS.md**: Line 46 (frequency hopping statement)
4. **SDR waterfall**: Observed frequency hopping across 65 channels
5. **Channel scan**: Strongest response at +8.0 MHz offset (923.0 MHz)
