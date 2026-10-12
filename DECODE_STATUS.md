# Decode Status

**Last updated:** 2026-10-12

## Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Modulation | ✅ Known | OOK/ASK (NOT 2-FSK) — see CRITICAL_FINDINGS |
| Symbol rate | ✅ Known | ~769 ksym/s (NOT 100 kbps) |
| Carrier offset | ⚠ PARTIAL | ~-0.779 MHz (could be receiver tuning artifact) |
| Phase | ✅ Known | Coherent (-55° to -60°) |
| Bursts | ✅ Known | 12 real bursts, 5.14 ms each |
| Syncword | ❌ UNKNOWN | Not yet identified (current syncword is for 2-FSK) |
| Payload structure | ❌ UNKNOWN | Not yet identified |
| CRC | ❌ UNKNOWN | Not yet identified |
| Encryption | ❌ UNKNOWN | Not yet identified |
| WAV capture | ✅ VALID | Supersedes prior "INVALID" conclusion |
| Decode | ❌ NOT STARTED | Need to identify protocol first |

## Key Finding (2026-10-12)

**The captured signal is OOK/ASK at ~769 ksym/s. This is NOT the SoftRF legacy protocol.**

The prior "capture is invalid" conclusion was wrong. The capture is valid, but the signal is a different protocol than the one we were trying to decode.

### What We Know
- 12 real bursts, 5.14 ms each
- OOK/ASK modulation (two-level amplitude)
- Coherent phase (-55° to -60°)
- Carrier offset ~-0.779 MHz
- Symbol rate ~769 ksym/s

### What We Don't Know
- What protocol this is
- What the syncword is
- What the payload structure is
- Whether it's encrypted
- What the carrier offset means (signal characteristic vs receiver artifact)

## Next Steps

1. **Verify the receiver setup** — What IF/center frequency was used?
2. **Check if SoftRF has other protocol variants** — Search the firmware source
3. **Search for OOK/ASK protocols at ~769 ksym/s** in the 915 MHz band
4. **Build a new decoder** for OOK/ASK at ~769 ksym/s
5. **Identify the protocol** — Cross-reference with known protocols

## Key Files

- `CRITICAL_FINDINGS_2026-10-12.md` — **THE AUTHORITATIVE DOCUMENT**
- `REVERSE_ENGINEERING_NOTES.md` — SoftRF legacy protocol spec (NOT applicable to current signal)
- `softrf_decoder.py` — Decoder for 2-FSK (NOT applicable to current signal)
- `measure_symbols.py` — Symbol rate measurement
- `extract_bitstream.py` — Bitstream extraction

## Superseded Documents

- `ANALYSIS_INVALID_CAPTURE.md` — **SUPERSEDED** — prior "capture is invalid" conclusion was wrong
- Prior sections of this document claiming the capture is invalid — **SUPERSEDED**
