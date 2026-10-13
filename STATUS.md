# SoftRF Decoder — Status & Findings

> **CRITICAL UPDATE (2026-10-12): The capture is VALID. The signal is OOK/ASK at ~769 ksym/s. This is NOT the SoftRF legacy protocol. See `CRITICAL_FINDINGS_2026-10-12.md` for details.**

## Signal Analysis (2026-10-12)

### WAV File
- File: `baseband_915000000Hz_20-35-24_03-10-2026.wav`
- Sample rate: 20 MS/s, I/Q baseband, 32-bit float
- Duration: ~5.6 seconds
- **Status: VALID** (supersedes prior "INVALID" conclusion)

### Signal Diagnosis: OOK/ASK (NOT 2-FSK)

| Property | Measured | Expected (SoftRF legacy) |
|----------|----------|-------------------------|
| Modulation | OOK/ASK (two-level amplitude) | 2-FSK (two-frequency) |
| Symbol rate | ~769 ksym/s | 100 kbps |
| Phase | Coherent (-55° to -60°) | Two frequency clusters |
| Carrier offset | ~-0.779 MHz | ±50 kHz |
| Bursts | 12 real, 5.14 ms each | N/A |

**Root cause of prior error**: The prior analysis was looking for 2-FSK at 100 kbps (per firmware). The actual signal is OOK/ASK at ~769 ksym/s. The signal was there all along; we were looking for the wrong thing.

## Decoder Implementation

### Completed
- [x] `softrf_decoder.py` — Full decoder (FM demod, Manchester, sync, CRC, XXTEA)
- [x] `fix_decoder.py` — Alternative Manchester approach
- [x] `fix_decoder2.py` — Phase-based FM demod
- [x] `fix_sync.py` — Sync word detection with Manchester
- [x] `check_signal.py` — Signal diagnostics

### Decoder Pipeline (firmware-verified)
```
1. FM demodulate 2-FSK (100 kbps, 50 kHz dev)
2. Manchester decode (2 bits → 1 bit)
3. Group into bytes (8 bits, MSB first)
4. Find preamble 0x55 + sync word 55 99 A5 A9 55 66 65 96
5. Extract 24-byte payload
6. CRC-CCITT (poly 0x1021, init 0xFFFF, pre-seed 31 FA B6)
7. XXTEA decrypt 5 words (6 rounds, DELTA=0x9e3779b9)
8. Extract addr, type, lat/lon/alt/speed/course
```

### Key Constants
```python
SYNC = [0x55, 0x99, 0xA5, 0xA9, 0x55, 0x66, 0x65, 0x96]
KEY1 = [0xe43276df, 0xdca83759, 0x9802b8ac, 0x4675a56b,
        0xfc78ea65, 0x804b90ea, 0xb76542cd, 0x329dfa32]
KEY2 = 0x045d9f3b
KEY3 = 0x87b562f4
DELTA = 0x9e3779b9
ROUNDS = 6
```

## Next Steps

1. **Verify the receiver setup** — What IF/center frequency was used? Was the transmitter actually at 915 MHz?
2. **Check if SoftRF has other protocol variants** — Search the firmware source for OOK/ASK or ASK modulation
3. **Search for OOK/ASK protocols at ~769 ksym/s** in the 915 MHz band
4. **Build a new decoder** for OOK/ASK at ~769 ksym/s (the current decoder is for 2-FSK)
5. **Identify the protocol** — Cross-reference the signal characteristics with known protocols

## Files
- `CRITICAL_FINDINGS_2026-10-12.md` — **THE AUTHORITATIVE DOCUMENT** for the current state
- `REVERSE_ENGINEERING_NOTES.md` — Full protocol spec (SoftRF legacy)
- `softrf_decoder.py` — Main decoder (for 2-FSK, NOT applicable to current signal)
- `measure_symbols.py` — Symbol rate measurement
- `extract_bitstream.py` — Bitstream extraction
- `ANALYSIS_INVALID_CAPTURE.md` — **SUPERSEDED** — prior "capture is invalid" conclusion

## 2026-10-13: OOK/ASK Decode Attempt

**Result:** Signal present but SNR too low for basic OOK demodulation.

**Key findings:**
- 10% duty cycle confirmed (8.5% within 100ms windows)
- Signal at 0.05 level, noise at 0.03 level (SNR=1.67)
- 100+ sub-bursts of 30-32ms per 100ms window
- Basic OOK at 769 ksym/s: 25,089 symbols, 136 "1" bits, no sync word

**Next steps:**
- Matched filtering or coherent detection needed
- Average multiple bursts to improve SNR
- Use carrier frequency for better SNR

**Files:** `OOK_DECODE_ATTEMPT.md`, `OOK_decoder_v3.py`
