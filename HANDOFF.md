# Handoff Document - SoftRF Decoder Project

**Last Updated**: 2026-10-13

## Current State
**STATUS**: BLOCKED - Signal present but SNR too low for reliable decoding

## What We Discovered

### 1. Modulation Type: OOK/ASK (NOT 2-FSK)
- **Evidence**: Phase is coherent (not random), envelope shows bimodal distribution
- **Impact**: All FSK-specific decoders are OBSOLETE
- **Valid decoders**: OOK/ASK demodulators

### 2. Signal Characteristics
- **Center frequency**: 915.000 MHz (exactly)
- **Sample rate**: 20 MS/s
- **Bandwidth**: 20 MHz
- **Format**: I/Q interleaved float32 WAV
- **Burst pattern**: 100ms windows with ~8.5% duty cycle
- **SNR**: Poor (noise floor ~0.03, signal peaks ~0.25)

### 3. Why We Can't Decode
- Minimum burst durations are 1 sample (0.05 ms) = noise, not symbols
- Sync word not found in bitstream
- SNR too low for reliable symbol-level decoding

## Files to Read (In Order)

1. **`README.md`** - Project overview
2. **`STATUS.md`** - Current status
3. **`FSK_HYPOTHESIS_DISPROVEN.md`** - Why FSK was rejected
4. **`OOK_DECODING_ATTEMPT.md`** - OOK/ASK decoding attempt
5. **`RESUME_FROM_SCRATCH.md`** - Comprehensive handoff doc
6. **`SESSION_SUMMARY_2026-10-13.md`** - This session's findings

## Scripts (Valid)
- `characterize.py` - Spectral analysis
- `measure_symbols.py` - Symbol measurement
- `extract_bitstream.py` - Bitstream extraction
- `protocol_analysis.py` - Protocol analysis
- `check_signal.py` - Basic signal checks
- `reality_check.py` - Phase coherence check
- `COHERENT_demod.py` - Coherent demodulation
- `OOK_decoder_v2.py` / `v3.py` - OOK decoders

## Scripts (OBSOLETE)
- `fsk_demod.py` - FSK-specific
- `demodulate_hops.py` - FSK-specific
- `fft_analysis.py` - FSK-specific
- `fix_sync.py` - FSK-specific

## Next Steps (In Priority Order)

1. **Capture a better signal** (higher SNR)
2. **Retry OOK/ASK decoding** with advanced techniques
3. **Document findings** (reverse-engineering docs)
4. **Produce working decoder** (Python CLI + C/C++ reference)

## What NOT to Do

- ❌ Don't use FSK-specific decoders (they're OBSOLETE)
- ❌ Don't assume the signal is 2-FSK (it's OOK/ASK)
- ❌ Don't try to decode with the current capture (SNR too low)

## Success Criteria

1. **Decoded payload**: At least one valid 64-bit sync + data frame
2. **Reverse-engineering docs**: Protocol spec, frame format, CRC details
3. **Working decoder**: Python CLI + C/C++ reference decoder
4. **All deliverables**: Reports, code, docs in the repo

## Status
**BLOCKED**: Need a better capture to proceed.
