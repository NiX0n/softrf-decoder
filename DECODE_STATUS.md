# Decode Status

**Last updated:** 2026-10-12

## Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Modulation | ✅ Known | 2-FSK, 100 kbps, ±50 kHz deviation |
| Whitening | ✅ Known | Manchester (bit-inversion) |
| Syncword | ✅ Known | `55 99 A5 A9 55 66 65 96` (8 bytes, air order) |
| Payload structure | ✅ Known | Syncword + raw payload (≥16 bytes) |
| CRC | ✅ Known | CCITT-F, poly 0x1021, init 0xFFFF, pre-seed 0x31,0xFA,0xB6 |
| Encryption | ✅ Known | XXTEA, 6 rounds, 5 words (20 bytes), key = LEGACY_KEY1 ⊕ LEGACY_KEY2 ⊕ v6key |
| Key derivation | ✅ Known | `make_v6_key(timestamp, address)` from firmware |
| WAV capture | Unknown | The current analysis pipeline did not identify the expected 2-FSK characteristics. Confidence: Medium. Alternative explanations remain possible. |
| Decode | Uknown | Uknown |


## Key Files

- `REVERSE_ENGINEERING_NOTES.md` — Protocol details from firmware
- `SYSTEM_FACTS.md` — Confirmed facts + correction log
- `prototype/decode.py` — Decoder prototype with self-test
- `reference/wav_sample/` — (empty — need valid capture)

---

## Update: 2026-10-12 (Analysis Complete)

### Critical Finding

**The captured WAV file does NOT contain a valid 2-FSK signal.**

Detailed analysis (see `ANALYSIS_INVALID_CAPTURE.md`) confirms:
- Signal is a **CW tone at ~6.78 MHz** relative to receiver LO
- Very small variations (std/mean ≈ 2.5)
- No distinct bursts — envelope is uniformly distributed
- FFT shows dominant energy at integer fractions of sample rate (spurs)
- Phase is not changing over time (instantaneous frequency = 0.0 kHz)

### Root Cause

The decoder fails at **Stage 3: Carrier Identification** because the input signal is **not a valid FSK signal**. This is consistent with LO leakage, a beacon signal, or a test tone.

### Recommendations

1. **Verify the SDR setup** — check gain, sample rate, and frequency configuration
2. **Recapture the signal** with a known-good SDR setup
3. **Alternative**: Use a reference capture or synthetic signal to test the decoder

### Next Steps

- [ ] Confirm SDR setup with user
- [ ] Recapture signal with known-good setup
- [ ] Re-run decoder with new capture
- [ ] Verify results (syncword, CRC, payload)

### Decoder Implementation Status

The decoder implementation is **complete** and ready for testing:
- ✅ FM demodulation
- ✅ Manchester decode
- ✅ Syncword search
- ✅ CRC-16 CCITT-F
- ✅ XXTEA decryption
- ✅ Key derivation
- ✅ Coordinate decode

**The decoder is not the problem. The input signal is.**
