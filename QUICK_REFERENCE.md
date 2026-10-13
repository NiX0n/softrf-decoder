# Quick Reference Card - SoftRF 915 MHz Decoder

## What We Know
- **Modulation**: OOK/ASK (NOT FSK)
- **Frequency**: 915.000 MHz
- **Sample rate**: 20 MS/s
- **Burst pattern**: 100ms windows, ~8.5% duty cycle
- **SNR**: Poor (can't decode reliably)

## What We DON'T Know
- Symbol rate
- Bitstream content
- Why 26.12 kHz spectral width

## Key Files
- **Read first**: `HANDOFF.md`, `RESUME_FROM_SCRATCH.md`
- **Why FSK was rejected**: `FSK_HYPOTHESIS_DISPROVEN.md`
- **OOK attempt**: `OOK_DECODING_ATTEMPT.md`
- **Session log**: `SESSION_SUMMARY_2026-10-13.md`

## Valid Scripts
- `characterize.py` - spectral analysis
- `COHERENT_demod.py` - coherent demodulation
- `OOK_decoder_v3.py` - OOK decoder

## OBSOLETE Scripts
- `fsk_demod.py`, `demodulate_hops.py`, `fft_analysis.py`, `fix_sync.py`

## Next Step
**Capture a better signal** (higher SNR), then retry OOK/ASK decoding.

## Status
**BLOCKED**: Signal present but SNR too low.
