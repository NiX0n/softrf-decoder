# SoftRF Decoder - Status

**Last Updated: 2026-10-20 (CRITICAL CORRECTION)**

## Current Status: REOPENED — FSK Hypothesis Back in Play

The capture contains a signal that is **most likely FSK** (not OOK/ASK as previously
concluded). The OOK/ASK classification was based on an incorrect frequency offset
estimate. With the corrected carrier removal (-8.733 MHz), the signal shows constant
amplitude (std/mean = 0.144), which is consistent with FSK.

### What We Know (CORRECTED)
- **Signal type:** FSK (most likely) — constant amplitude after carrier removal
- **Center frequency:** 915.000 MHz
- **Carrier offset:** -8.733 MHz (corrected from +11.23 MHz)
- **Residual frequency offset:** -47.3 kHz (consistent with FSK)
- **Sample rate:** 20 MS/s
- **Burst count:** 79 regions in 30.4s
- **Burst duration:** ~5.3 ms
- **Burst SNR:** ~29.1 dB (sufficient for decoding!)
- **Likely protocol:** SoftRF Legacy (2-FSK, 100 kbps, XXTEA, CCITT)

### What We've Tried
1. **2-FSK demodulation** → Initially "disproven" (wrong carrier offset)
2. **OOK thresholding** → Failed (wrong hypothesis — signal is FSK)
3. **Burst detection** → 79 bursts found
4. **Sync word search** → Not yet attempted with corrected FSK demodulation
5. **Corrected FSK analysis** → **NEW** — shows constant amplitude (FSK)

### What Would Help
1. **FM demodulation with corrected carrier offset** (-8.733 MHz)
2. **Search for SoftRF Legacy sync word**: `55 99 A5 A9 55 66 65 96`
3. **XXTEA decryption** of payload
4. **CRC verification** (CCITT-F)

### Next Steps
- [x] Correct frequency offset (-8.733 MHz)
- [x] Re-examine modulation (FSK, not OOK/ASK)
- [ ] **Apply FM demodulation with corrected carrier offset**
- [ ] Search for SoftRF Legacy sync word
- [ ] Decode payload with XXTEA
- [ ] Verify CRC
- [ ] Analyze 397s capture (4.6 GB) for more bursts

## Key Files
- `SESSION_REPORT_2026-10-20.md` — **CRITICAL CORRECTION** (read first)
- `QUICK_REFERENCE.md` — Updated quick reference
- `REVERSE_ENGINEERING_NOTES.md` — SoftRF Legacy protocol spec (FSK, XXTEA, CCITT)
- `FSK_HYPOTHESIS_DISPROVEN.md` — SUPERSEDED (based on wrong offset)
- `OOK_DECODING_ATTEMPT.md` — SUPERSEDED (wrong hypothesis)

## Conclusion
**The signal is most likely FSK, not OOK/ASK.** The "FSK disproven" conclusion was
based on an incorrect frequency offset estimate. With the corrected offset, the signal
shows constant amplitude (FSK characteristic) and a two-component spectrum consistent
with FSK frequency deviation.

**The SoftRF Legacy protocol (2-FSK, 100 kbps, XXTEA, CCITT) is the most likely
candidate.** SNR is ~29 dB — sufficient for reliable FSK demodulation.

**Next step**: Apply FM demodulation with the corrected carrier offset and search
for the SoftRF Legacy sync word.
