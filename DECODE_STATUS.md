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
