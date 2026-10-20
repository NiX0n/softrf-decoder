# Handoff Document - SoftRF Decoder Project

**Last Updated**: 2026-10-20 (CORRECTED)

## Current State
**STATUS**: FSK RE-OPENED — SoftRF Legacy protocol is the most likely candidate

> **⚠️ CORRECTION (2026-10-20):** Prior "BLOCKED / OOK/ASK / SNR too low" status was
> based on an incorrect frequency offset estimate. With the corrected carrier removal
> (-8.733 MHz), the signal shows constant amplitude (std/mean = 0.144) — **FSK, not
> OOK/ASK** — and burst SNR ~29.1 dB. See `SESSION_REPORT_2026-10-20.md`.

## What We Know (CORRECTED)

### 1. Modulation Type: **FSK** (not OOK/ASK)
- Constant amplitude after carrier removal (std/mean = 0.144)
- Two-component spectrum at -8.733 / -8.833 MHz (consistent with FSK deviation)
- Residual phase rotation of -47.3 kHz after carrier removal (consistent with FSK)

### 2. Signal Characteristics
- **Center frequency**: 915.000 MHz
- **Carrier offset**: -8.733 MHz (corrected)
- **Sample rate**: 20 MS/s
- **Burst pattern**: 79 regions, ~5.3 ms each
- **Burst SNR**: ~29.1 dB (sufficient for decoding)

### 3. Most Likely Protocol
**SoftRF Legacy** (from firmware source `Legacy.h`/`Legacy.cpp`):
- 2-FSK, 100 kbps, GFSK, ±18 kHz deviation (915 MHz)
- Sync word: `55 99 A5 A9 55 66 65 96`
- XXTEA encryption, CCITT-F CRC, 2:1 channel encoding, LSB first

## Next Steps (in order)

1. **FM demodulation with corrected carrier offset** (-8.733 MHz or -8.833 MHz)
2. **Search for sync word** `55 99 A5 A9 55 66 65 96` (8 bytes, LSB first)
3. **Parse frame structure**: sync + length + payload + CRC
4. **Decrypt payload** with XXTEA (key from `Legacy.cpp`)
5. **Verify CRC** (CCITT-F, pre-seed `0x31, 0xFA, 0xB6`)

## Key Files

| File | Role |
|------|------|
| `SESSION_REPORT_2026-10-20.md` | **AUTHORITATIVE** — corrected analysis |
| `QUICK_REFERENCE.md` | Quick reference (updated) |
| `STATUS.md` | Status (updated) |
| `DECODE_STATUS.md` | Decode status (updated) |
| `CURRENT_BLOCKERS.md` | Blockers (all resolved) |
| `REVERSE_ENGINEERING_NOTES.md` | SoftRF Legacy protocol spec |
| `NOTES.md` | Firmware source citations |
| `FSK_HYPOTHESIS_DISPROVEN.md` | SUPERSEDED |
| `OOK_DECODING_ATTEMPT.md` | SUPERSEDED |

## Superseded Documents

- `ANALYSIS_INVALID_CAPTURE.md` — SUPERSEDED (capture is valid)
- `CRITICAL_FINDINGS_2026-10-12.md` — PARTIALLY SUPERSEDED (OOK/ASK rejected)
- `FSK_HYPOTHESIS_DISPROVEN.md` — SUPERSEDED (wrong offset)
- `OOK_DECODING_ATTEMPT.md` — SUPERSEDED (wrong modulation)
- `SESSION_SUMMARY_2026-10-13.md` — SUPERSEDED (conclusion reversed)
