# Quick Reference Card - SoftRF 915 MHz Decoder

**Last Updated: 2026-10-20 (CRITICAL CORRECTION)**

## What We Know (CORRECTED)

| Parameter | Value | Confidence |
|-----------|-------|------------|
| **Modulation** | **FSK (most likely)** | HIGH — constant amplitude after carrier removal |
| ~~OOK/ASK~~ | ~~"Confirmed"~~ | **REJECTED** — 14.4% amplitude variation (too low for OOK) |
| **Frequency** | 915.000 MHz | HIGH |
| **Carrier offset** | **-8.733 MHz** (corrected from +11.23 MHz) | HIGH |
| **Residual freq offset** | -47.3 kHz | HIGH |
| **Sample rate** | 20 MS/s | HIGH |
| **Burst count** | 79 regions in 30.4s | HIGH |
| **Burst duration** | ~5.3 ms | HIGH |
| **Burst SNR** | ~29.1 dB | MEDIUM (better than previously estimated 13.3 dB) |
| **Protocol** | Possibly SoftRF Legacy (2-FSK, 100 kbps, XXTEA, CCITT) | MEDIUM — consistent with firmware |

## What We DON'T Know
- Exact symbol rate (after carrier correction)
- Bitstream content (FSK demodulation not yet attempted with corrected offset)
- Frame structure
- Whether it's SoftRF Legacy or different protocol

## Key Files
- **Read first**: `SESSION_REPORT_2026-10-20.md` (CRITICAL CORRECTION)
- **Protocol spec**: `REVERSE_ENGINEERING_NOTES.md` (FSK, XXTEA, CCITT — still valid)
- **Session history**: `SESSION_SUMMARY_2026-10-13.md` (partially superseded)
- **Why FSK was (wrongly) rejected**: `FSK_HYPOTHESIS_DISPROVEN.md` (SUPERSEDED)
- **OOK attempt**: `OOK_DECODING_ATTEMPT.md` (SUPERSEDED)

## Valid Scripts
- `characterize.py` - spectral analysis
- `COHERENT_demod.py` - coherent demodulation
- `softrf_decoder.py` - FSK decoder (RE-EXAMINE with corrected offset)

## SUPERSEDED Scripts
- `OOK_decoder_v2.py`, `OOK_decoder_v3.py` - OOK (rejected hypothesis)

## Next Step
**Apply FM demodulation with corrected carrier offset (-8.733 MHz)** and search for
the SoftRF Legacy sync word: `55 99 A5 A9 55 66 65 96`.

## Status
**REOPENED**: FSK hypothesis is back in play. SNR ~29 dB is sufficient for decoding.
The SoftRF Legacy protocol (2-FSK, 100 kbps, XXTEA, CCITT) is the most likely candidate.
