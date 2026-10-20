# Capture Confidence Report

**Date**: 2026-10-19
**CORRECTED**: 2026-10-20 — see correction note below.

> ## ⚠️ CRITICAL CORRECTION (2026-10-20)
>
> Quality assessments in this report that referenced "low SNR" or "OOK/ASK" were
\u003> based on an incorrect frequency offset. Corrected results (see
> `SESSION_REPORT_2026-10-20.md`):
> - Carrier offset: **-8.733 MHz**
\u003> - Burst SNR: **~29.1 dB** (sufficient for FSK decoding)
\u003> - Modulation: **FSK** (constant amplitude after carrier removal), not OOK/ASK
\u003> - SoftRF Legacy protocol spec IS the applicable protocol

---

## Purpose

Classify every RF capture by quality and confidence, define the primary analysis target, and document limitations.

Per `DEVELOPMENT_RULES.md` Rule 12: this report is **mandatory before implementation**.

---

## Capture Inventory

| # | File | Duration | Date | Size | Quality | Confidence |
|---|------|----------|------|------|---------|------------|
| 1 | `baseband_915000000Hz_20-35-24_03-10-2026.wav` | 30s | 2026-10-03 | ~545 MB | **LOW** | LOW |
| 2 | `baseband_915000000Hz_15-06-12_12-10-2026.wav` | 60s | 2026-10-12 | ~1.1 GB | **UNKNOWN** | UNANALYZED |
| 3 | `silence_baseband_915000000Hz_12-43-41_12-10-2026.wav` | 120s | 2026-10-12 | ~2.1 GB | **NOISE FLOOR** | N/A (reference) |
| 4 | `long_baseband_915000000Hz_18-26-17_19-10-2026.wav` | 397s | 2026-10-19 | **4.6 GB** | **UNANALYZED** | UNANALYZED |
| 5 | `silence_baseband_915000000Hz_18-23-16_19-10-2026.wav` | — | 2026-10-19 | 886 MB | **NOISE FLOOR** | N/A (reference) |

All captures: 20 MS/s, 32-bit float, baseband IQ (I,Q interleaved).

---

## Capture Assessments

### Capture 1: `baseband_915000000Hz_20-35-24_03-10-2026.wav`

**Duration**: 30 seconds (600M samples, 545 MB)

**Analysis Status**: ✅ FULLY ANALYZED (2026-10-13)

**Findings**:
- Signal present: 12 OOK/ASK bursts × ~5.17 ms
- SNR: ~13.3 dB
- Modulation: OOK/ASK (NOT FSK)
- Bit-level decoding: **FAILED** (SNR too low)
- Sync word: **NOT FOUND**

**Quality**: LOW
- Short duration limits burst statistics
- SNR borderline for symbol-level detection
- Sufficient for modulation identification and burst structure

**Confidence**: LOW for decoding, MEDIUM-HIGH for modulation type identification

**Classification**: `[RF VERIFIED]` for modulation type; `[UNVERIFIED]` for bit-level content

---

### Capture 2: `baseband_915000000Hz_15-06-12_12-10-2026.wav`

**Duration**: 60 seconds (1.2B samples, ~1.1 GB)

**Analysis Status**: ❌ NOT ANALYZED

**Quality**: UNKNOWN
- May contain signal or noise (not determined)
- Longer than Capture 1, potentially more burst samples

**Confidence**: UNKNOWN — needs analysis

**Action Required**: Analyze to determine if signal is present and at what SNR

---

### Capture 3: `silence_baseband_915000000Hz_12-43-41_12-10-2026.wav`

**Duration**: 120 seconds (2.4B samples, ~2.1 GB)

**Analysis Status**: ✅ USED AS NOISE FLOOR REFERENCE

**Findings**:
- No signal present (confirmed noise-only)
- Used as reference for SNR calculations in Capture 1 analysis

**Quality**: N/A (reference capture)

**Classification**: `[RF VERIFIED]` noise floor reference

---

### Capture 4: `long_baseband_915000000Hz_18-26-17_19-10-2026.wav`

**Duration**: 397 seconds (~7.9B samples, **4.6 GB**)

**Analysis Status**: ❌ NOT ANALYZED (NEW — 2026-10-19)

**Quality**: UNKNOWN
- **Longest capture** in the set
- Potentially contains many more burst events
- May have different SNR than Capture 1
- Taken from the same receiver (RTL-SDR) at 915 MHz

**Confidence**: UNKNOWN — needs analysis

**Action Required**: 
1. Check signal presence (energy detection)
2. Measure SNR
3. Count and characterize bursts
4. Compare with Capture 1

---

### Capture 5: `silence_baseband_915000000Hz_18-23-16_19-10-2026.wav`

**Duration**: Unknown (886 MB ≈ 21.7 seconds at 20 MS/s)

**Analysis Status**: ✅ USED AS NOISE FLOOR REFERENCE (2026-10-19)

**Findings**:
- Used as noise floor for the 2026-10-19 burst analysis
- Confirmed: noise floor ~0.03 (3σ = 0.0015)

**Quality**: N/A (reference capture)

**Classification**: `[RF VERIFIED]` noise floor reference

---

## Primary Analysis Capture

**Primary**: Capture 1 (`baseband_915000000Hz_20-35-24_03-10-2026.wav`)
- Only capture with completed analysis
- Established OOK/ASK modulation and burst structure

**Secondary (pending)**: Capture 4 (`long_baseband_915000000Hz_18-26-17_19-10-2026.wav`)
- Most promising for improved statistics
- Needs analysis before implementation can proceed

**Reference**: Captures 3 and 5 (noise floor)

---

## SNR Limitation

**Current best SNR**: ~13.3 dB (Capture 1)

**Impact**:
- Cannot reliably extract individual OOK/ASK symbols
- Cannot find sync word in the bitstream
- Cannot validate frame structure
- Cannot decode payload

**Required for reliable decoding**: ≥ 20 dB (typical for OOK/ASK with 2:1 bit repeat)

**Gap**: ~6.7 dB improvement needed

**Possible mitigations**:
1. Longer capture → more burst samples to average (Capture 4)
2. Better antenna placement / gain
3. Lower noise figure receiver
4. Narrower bandpass filter (if signal bandwidth allows)

---

## Confidence Summary

| Capture | Signal Present | SNR | Decodable | Confidence |
|---------|---------------|-----|-----------|------------|
| 1 | YES | 13.3 dB | NO | LOW |
| 2 | UNKNOWN | UNKNOWN | UNKNOWN | UNANALYZED |
| 3 | NO (noise) | N/A | N/A | N/A |
| 4 | UNKNOWN | UNKNOWN | UNKNOWN | UNANALYZED |
| 5 | NO (noise) | N/A | N/A | N/A |

---

## Conclusion

**No capture currently supports reliable decoding.** The primary capture (1) confirms the signal is OOK/ASK with 12 × 5.17ms bursts, but SNR is too low for bit-level extraction. Capture 4 (397s, new) is the most promising candidate for improved statistics and must be analyzed before implementation.

**BLOCKER**: No capture has sufficient SNR for reliable OOK/ASK symbol decoding.
