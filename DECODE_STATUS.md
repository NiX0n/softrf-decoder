# Decode Status

> **⚠️ CORRECTED 2026-10-20:** The OOK/ASK classification below was based on an
> incorrect frequency offset estimate. With the corrected carrier removal
> (-8.733 MHz), the signal shows constant amplitude (std/mean = 0.144), which
> **rejects OOK/ASK** and is consistent with FSK. The SNR is ~29 dB, not
> "limited". See `SESSION_REPORT_2026-10-20.md` for the full analysis.

**Last updated:** 2026-10-20 (CORRECTED)

## Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Modulation | ✅ KNOWN (corrected) | **FSK** (NOT OOK/ASK — constant amplitude after carrier removal) |
| Carrier offset | ✅ Known | **-8.733 MHz** (corrected from prior estimates) |
| Residual offset | ⚠ Measured | -47.3 kHz (consistent with FSK) |
| Bursts | ✅ Known | 79 regions, ~5.3 ms each |
| SNR | ✅ KNOWN (corrected) | **~29.1 dB** — sufficient for decoding |
| Protocol | 🔄 CANDIDATE | SoftRF Legacy (2-FSK, 100 kbps, XXTEA, CCITT) |
| Syncword | ❌ NOT SEARCHED | `55 99 A5 A9 55 66 65 96` (candidate, not yet verified) |
| WAV capture | ✅ VALID | 30.4s, 79 burst regions |
| Decode | 🔄 IN PROGRESS | FSK demodulation with corrected offset — next step |

## Corrected Findings (2026-10-20)

1. **Frequency offset was wrong.** Prior analyses estimated +11.23 MHz or
   -0.779 MHz. The actual dominant component is **-8.733 MHz** (with a second
   strong component at -8.833 MHz).
2. **Amplitude is constant after carrier removal.** std/mean = 0.144 (mean
   magnitude 1.225065, std 0.176278). OOK/ASK requires large amplitude
   variation between symbols — it is **rejected**.
3. **Two-component spectrum** at -8.733 / -8.833 MHz is consistent with FSK
   frequency deviation (two frequency states).
4. **Residual phase rotation** after carrier removal averages -47.3 kHz
   rotation — consistent with FSK, not a stationary carrier.

## Next Steps (corrected)

1. **Apply FM demodulation with carrier offset -8.733 MHz** (or -8.833 MHz)
2. **Search for SoftRF Legacy sync word** `55 99 A5 A9 55 66 65 96`
3. **Verify with XXTEA + CCITT-F CRC** (key from `Legacy.cpp`)
4. If SoftRF Legacy fails, try other 915 MHz FSK protocols

## Key Files

- `SESSION_REPORT_2026-10-20.md` — **AUTHORITATIVE** corrected analysis
- `QUICK_REFERENCE.md` — Quick reference (updated)
- `REVERSE_ENGINEERING_NOTES.md` — SoftRF Legacy protocol spec (2-FSK, XXTEA, CCITT)
- `FSK_HYPOTHESIS_DISPROVEN.md` — SUPERSEDED (based on wrong offset)
- `OOK_DECODING_ATTEMPT.md` — SUPERSEDED (wrong hypothesis)

## Superseded Documents

- `ANALYSIS_INVALID_CAPTURE.md` — **SUPERSEDED** — capture is valid
- `CRITICAL_FINDINGS_2026-10-12.md` — **PARTIALLY SUPERSEDED** (OOK/ASK claim rejected)
- `FSK_HYPOTHESIS_DISPROVEN.md` — **SUPERSEDED** (wrong carrier offset)
- `OOK_DECODING_ATTEMPT.md` — **SUPERSEDED** (wrong modulation hypothesis)
