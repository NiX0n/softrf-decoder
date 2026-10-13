# FINAL SESSION REPORT — 2026-10-13

## Executive Summary

**Status:** BLOCKED — Signal captured but SNR too low for reliable decoding

## What We Discovered

### 1. ❌ 2-FSK Hypothesis DISPROVEN
- **Phase is coherent** (not random) — FSK should have phase discontinuities
- **Envelope shows bimodal distribution** — characteristic of OOK/ASK, not FSK
- **Frequency spread is wide** (0–90 kHz) — not the clean two-cluster pattern of FSK
- **Spectral width** (26.12 kHz) is inconsistent with 769 ksym/s 2-FSK

### 2. ✅ OOK/ASK is the Correct Modulation
- **100ms bursts** with ~8.5% duty cycle above noise floor
- **Bimodal envelope** distribution (noise floor + signal peaks)
- **Coherent phase** consistent with continuous carrier + amplitude modulation

### 3. ⚠️ SNR is the Blocker
- **Noise floor**: ~0.030 (72.4% of samples)
- **Signal peaks**: ~0.25–0.27 (0.6% of samples)
- **Minimum burst duration**: 1 sample (0.05ms) — this is noise, not symbols
- **Result**: Cannot reliably extract bitstream or find sync word

## What We Delivered

### Documentation
- ✅ `FSK_HYPOTHESIS_DISPROVEN.md` — Formal proof that FSK is wrong
- ✅ `OOK_DECODING_ATTEMPT.md` — Full record of OOK/ASK decoding effort
- ✅ `SESSION_SUMMARY_2026-10-13.md` — Complete session log
- ✅ `HANDOFF.md` — Comprehensive handoff document
- ✅ `QUICK_REFERENCE.md` — One-page summary for quick reference
- ✅ `RESUME_FROM_SCRATCH.md` — Updated with latest findings
- ✅ All FSK scripts marked OBSOLETE with clear warnings

### Code
- ✅ `COHERENT_demod.py` — Coherent demodulation (valid)
- ✅ `OOK_decoder_v2.py` — OOK/ASK decoder (needs better SNR)
- ✅ `OOK_decoder_v3.py` — OOK/ASK decoder v3 (needs better SNR)
- ✅ `reality_check.py` — Signal analysis utilities (valid)

### Git
- ✅ 5 commits on `main` branch (latest: `6529029`)
- ⚠️ Git push failing due to credential issues (HTTPS helper not available)

## What We Did NOT Deliver

- ❌ Working decoder (SNR too low)
- ❌ Reverse-engineering documentation (can't decode without working decoder)
- ❌ Git push to remote (credential issues)

## Next Steps (for next session)

1. **Capture a higher-SNR signal**
   - Move antenna closer to transmitter
   - Reduce background noise
   - Increase TX power if possible
   - **Goal**: Noise floor < 0.010, signal peaks > 0.5

2. **Retry OOK/ASK decoding**
   - Run `OOK_decoder_v3.py` on new capture
   - If sync word found → produce reverse-engineering docs
   - If not found → try more advanced techniques (correlators, Viterbi)

3. **Verify against SoftRF firmware**
   - Confirm OOK/ASK parameters match `Legacy.cpp`
   - Check symbol rate, baud rate, preamble pattern
   - Validate XXTEA decryption with recovered bitstream

## Key Files (in order to read)

1. **`QUICK_REFERENCE.md`** — Start here (2 minutes)
2. **`HANDOFF.md`** — Deep dive (10 minutes)
3. **`FSK_HYPOTHESIS_DISPROVEN.md`** — Why FSK was rejected (5 minutes)
4. **`OOK_DECODING_ATTEMPT.md`** — What we tried (5 minutes)
5. **`SESSION_SUMMARY_2026-10-13.md`** — Full session log (10 minutes)

## Signal Parameters

- **Center frequency**: 915.000 MHz
- **Sample rate**: 20 MS/s
- **Bandwidth**: 20 MHz
- **Duration**: ~5.6 seconds (112,328,704 samples)
- **Modulation**: OOK/ASK (confirmed)
- **Duty cycle**: ~8.5% (above noise floor)
- **Burst duration**: ~100 ms
- **Symbol rate**: Unknown (can't measure due to SNR)

## Conclusion

We made significant progress by **correctly identifying the modulation** (OOK/ASK, not FSK) and **documenting the evidence** thoroughly. However, the **SNR is the blocker** preventing us from completing the reverse engineering.

**The path forward is clear**: capture a better signal, then retry decoding with the OOK/ASK decoders we've already built.

---

*End of session report — 2026-10-13 02:30 UTC*
