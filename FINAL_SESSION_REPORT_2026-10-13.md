# FINAL SESSION REPORT — 2026-10-13 (UPDATED)

## Executive Summary

**Status:** PARTIAL SUCCESS — Signal characterized, modulation confirmed as OOK/ASK, burst structure identified. Decoding still blocked by SNR, but we now have a clear path forward.

## Key Breakthrough (Late Session)

**Noise subtraction using the silent control sample** revealed the true signal structure:
- **12 consistent bursts** of ~5.17 ms each (not 100 ms as previously estimated)
- **Irregular spacing** (190–796 ms) — likely event-driven, not periodic
- **Duty cycle**: ~1.1% (not 8.5% as previously estimated)
- This changes the entire decoding strategy

## What We Discovered

### 1. ❌ 2-FSK Hypothesis DISPROVEN
- **Phase is coherent** (not random) — FSK should have phase discontinuities
- **Envelope shows bimodal distribution** — characteristic of OOK/ASK, not FSK
- **Frequency spread is wide** (0–90 kHz) — not the clean two-cluster pattern of FSK

### 2. ✅ OOK/ASK is the Correct Modulation
- **Bimodal envelope** distribution (noise floor + signal peaks)
- **Coherent phase** consistent with continuous carrier + amplitude modulation
- **12 consistent ~5.17 ms bursts** (revealed by noise subtraction)

### 3. ⚠️ SNR is Still the Blocker
- **Noise floor**: ~0.030
- **Signal peaks**: ~0.25–0.27
- **SNR**: ~4.6x (13.3 dB) — too low for reliable OOK decoding
- **Result**: Cannot reliably extract bitstream or find sync word

## What We Delivered

### Documentation
- ✅ `FSK_HYPOTHESIS_DISPROVEN.md` — Formal proof that FSK is wrong
- ✅ `OOK_DECODING_ATTEMPT.md` — Full record of OOK/ASK decoding effort
- ✅ `SESSION_SUMMARY_2026-10-13.md` — Complete session log
- ✅ `HANDOFF.md` — Comprehensive handoff document
- ✅ `QUICK_REFERENCE.md` — One-page summary
- ✅ `RESUME_FROM_SCRATCH.md` — Updated with latest findings
- ✅ `BURST_ANALYSIS_2026-10-13.md` — **NEW**: Detailed burst analysis
- ✅ All FSK scripts marked OBSOLETE with clear warnings

### Code
- ✅ `COHERENT_demod.py` — Coherent demodulation (valid)
- ✅ `OOK_decoder_v2.py` — OOK/ASK decoder (needs better SNR)
- ✅ `OOK_decoder_v3.py` — OOK/ASK decoder v3 (needs better SNR)
- ✅ `reality_check.py` — Signal analysis utilities (valid)

### Git
- ✅ 6 commits on `main` branch (latest: `c1f0b19`)
- ⚠️ Git push failing due to credential issues (HTTPS helper not available)

## What We Did NOT Deliver

- ❌ Working decoder (SNR too low)
- ❌ Reverse-engineering documentation (can't decode without working decoder)
- ❌ Git push to remote (credential issues)

## Next Steps (for next session)

### Priority 1: Fix Git Push
```bash
# Set up SSH keys
ssh-keygen -t ed25519 -C "openclaw"
# Add public key to GitHub
# Update remote URL
git remote set-url origin git@github.com:NiX0n/softrf-decoder.git
git push -u origin main
```

### Priority 2: Retry Decoding with Better SNR
1. **Capture a higher-SNR signal**
   - Move antenna closer to transmitter
   - Reduce background noise
   - **Goal**: Noise floor < 0.010, signal peaks > 0.5

2. **Use the noise-subtraction approach**
   - Subtract silent control sample (mean) from signal
   - Threshold at +0.020 to find true signal regions
   - This revealed 12 consistent bursts in the 5.6s capture

3. **Focus on the 12 bursts**
   - Each burst is ~5.17 ms long
   - Extract and analyze each burst individually
   - Look for sync word, preamble, payload

### Priority 3: Verify Against SoftRF Firmware
- Confirm OOK/ASK parameters match `Legacy.cpp`
- Check symbol rate, baud rate, preamble pattern
- Validate XXTEA decryption with recovered bitstream

## Signal Parameters (Updated)

- **Center frequency**: 915.000 MHz
- **Sample rate**: 20 MS/s
- **Bandwidth**: 20 MHz
- **Duration**: ~5.6 seconds (112,328,704 samples)
- **Modulation**: OOK/ASK (confirmed)
- **Duty cycle**: ~1.1% (not 8.5%)
- **Burst duration**: ~5.17 ms (not ~100 ms)
- **Burst count**: 12 (not ~50)
- **Symbol rate**: Unknown (can't measure due to SNR)

## Conclusion

We made significant progress by:
1. **Correctly identifying the modulation** (OOK/ASK, not FSK)
2. **Documenting the evidence** thoroughly
3. **Using noise subtraction** to reveal the true burst structure
4. **Identifying 12 consistent bursts** as the signal of interest

**The path forward is clear**: capture a better signal, then retry decoding with the OOK/ASK decoders we've already built.

---

*End of session report — 2026-10-13 02:45 UTC (UPDATED)*
