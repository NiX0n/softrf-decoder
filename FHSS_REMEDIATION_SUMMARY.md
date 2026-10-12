# Frequency Hopping Remediation Summary

**Date**: 2026-10-12
**Status**: Complete

## What Was Wrong

The documentation treated the signal as a **single fixed frequency** at 915.0 MHz, with optional channel offsets. This was incorrect.

## What Is Correct

The signal uses **frequency hopping spread spectrum (FHSS)** across the US 902-928 MHz ISM band:

- **65 channels** (verified from firmware source `freqplan.h`)
- **Range**: 902.2 MHz to 927.8 MHz (25.6 MHz total)
- **Spacing**: 400 kHz
- **Center**: 915.0 MHz (channel 32)

## Evidence

1. **Firmware source**: `freqplan.h` defines a 65-channel frequency hopping plan
2. **Signal evidence**: SDR waterfall and channel scan show hopping across multiple channels
3. **Protocol evidence**: SoftRF Legacy protocol uses FHSS with GFSK inner modulation

## Key Findings

### Frequency Deviation

- **Firmware spec**: ±50 kHz
- **Observed**: ~14 kHz (from frequency distribution analysis)
- **Implication**: The two FSK tones are at -15.0 kHz and +13.0 kHz relative to the hop center

### Bit Extraction

- **Natural threshold**: -1.0 kHz (midpoint between -15.0 kHz and +13.0 kHz)
- **Bit 0**: -15.0 kHz
- **Bit 1**: +13.0 kHz
- **Result**: Balanced bit stream (252 zeros, 248 ones) for the first burst

### First 16 Bits

```
01000000010100000101010101000100
```

Hex: `40 50 54`

This differs from the previous all-`01` pattern, suggesting valid data structure.

## Documentation Updates

### Files Modified

1. **SYSTEM_FACTS.md**: Updated frequency hopping statement (line 46)
2. **NOTES.md**: Updated frequency plan, channel calculation, transmission pipeline, and decoding pipeline
3. **FHSS_REMEDIATION.md**: New document with detailed remediation explanation

## Next Steps

1. **Demodulate all bursts**: Apply the new -1.0 kHz threshold to all 12 bursts
2. **Frame structure identification**: Locate header, payload, and CRC in decoded bit streams
3. **Hop pattern analysis**: Correlate decoded frames with frequency hop timing
4. **CRC verification**: Implement CRC checking to validate decoded frames

## References

- [Firmware source](https://github.com/lyusupov/SoftRF)
- [NiX0n/softrf-decoder](https://github.com/NiX0n/softrf-decoder)
- `freqplan.h` (US frequency plan definition)
- SDR waterfall observations
- Channel scan results
