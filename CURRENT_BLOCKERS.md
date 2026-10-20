# Current Blockers

> **⚠️ CORRECTED 2026-10-20:** Both blockers below have been resolved or
> superseded by the frequency-offset correction. The signal is FSK (not OOK/ASK),
> the SNR is ~29 dB (not "too low"), and the SoftRF Legacy 2-FSK protocol spec
> IS the applicable protocol. See `SESSION_REPORT_2026-10-20.md`.

**Last Updated**: 2026-10-20 (CORRECTED)

---

## Previous Blockers (RESOLVED / SUPERSEDED)

### 1. SNR Too Low for Symbol Decoding — **RESOLVED (2026-10-20)**

The "low SNR" conclusion was an artifact of analyzing the wrong carrier offset.
Burst-level SNR measured on the actual carrier component (-8.733 MHz) is
**~29.1 dB** — well above the ~20 dB needed for reliable FSK decoding.

**Status**: RESOLVED

### 2. Protocol Mismatch: Firmware Says 2-FSK, Signal Is OOK/ASK — **SUPERSEDED (2026-10-20)**

The OOK/ASK classification was wrong (based on a wrong carrier offset, which
left large residual phase rotation that mimicked amplitude variation). The
signal shows constant amplitude after carrier removal — FSK behavior. The
SoftRF Legacy 2-FSK @ 100 kbps spec IS the applicable protocol.

**Status**: SUPERSEDED

---

## Remaining Work (not blockers, just not yet done)

1. **FM demodulation not yet applied** with the corrected carrier offset
   (-8.733 MHz or -8.833 MHz).
2. **Sync word search** (`55 99 A5 A9 55 66 65 96`) not yet attempted on
   correctly-demodulated data.
3. **XXTEA + CCITT-F verification** not yet run.

These are normal "next steps", not blockers — the path to decode is now clear.

## Key Files

- `SESSION_REPORT_2026-10-20.md` — AUTHORITATIVE corrected analysis
- `QUICK_REFERENCE.md` — Quick reference (updated)
- `STATUS.md` — Status (updated)
- `DECODE_STATUS.md` — Decode status (updated)
