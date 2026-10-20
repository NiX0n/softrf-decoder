# SESSION STATE — 2026-10-20 (END OF SESSION)

**This is the authoritative state document for resuming work.**

If you are reading this in a new session, start here. Everything else is
superseded or historical.

---

## One-Paragraph Summary

We are decoding a 915 MHz SoftRF radio signal captured as baseband IQ WAV
files (20 MS/s, 32-bit float). The SoftRF firmware source (cloned from
`github.com/lyusupov/SoftRF`, commit `973a8d73`) specifies a **2-FSK @ 100 kbps**
protocol with **XXTEA encryption**, **CCITT-F CRC**, **2:1 channel encoding**,
and **LSB-first** bit order. The sync word is `55 99 A5 A9 55 66 65 96`.

Prior sessions (Oct 12–19) incorrectly concluded the signal was OOK/ASK
based on a wrong frequency offset estimate. On **Oct 20**, a corrected
frequency analysis revealed the true carrier offset is **-8.733 MHz**
(prior estimate: +11.23 MHz). After removing the correct carrier, the
signal shows **constant amplitude** (std/mean = 0.144), which **rejects
OOK/ASK** and is consistent with **FSK**. Burst SNR is **~29.1 dB** —
sufficient for FSK decoding.

**The SoftRF Legacy protocol is the most likely candidate. Decoding has not
yet succeeded. The next step is FM demodulation with the corrected carrier
offset and sync word search.**

---

## Current Status

| Item | Value |
|------|-------|
| **Modulation** | FSK (2-FSK, 100 kbps, GFSK, ±18 kHz dev) — NOT OOK/ASK |
| **Carrier offset** | **-8.733 MHz** (corrected Oct 20) |
| **Burst SNR** | **~29.1 dB** (sufficient for decoding) |
| **Bursts** | 79 regions, ~5.3 ms each |
| **Protocol** | SoftRF Legacy (firmware-verified) |
| **Sync word** | `55 99 A5 A9 55 66 65 96` (not yet found in signal) |
| **Decoding** | NOT YET SUCCEEDED |
| **Blockers** | None (prior blockers resolved by correction) |

---

## Next Steps (in priority order)

1. **FM demodulation** with corrected carrier offset (-8.733 MHz or -8.833 MHz)
2. **Search for sync word** `55 99 A5 A9 55 66 65 96` (8 bytes, LSB first)
3. **Parse frame structure**: sync + length + payload + CRC
4. **Decrypt payload** with XXTEA (key from `Legacy.cpp`)
5. **Verify CRC** (CCITT-F, pre-seed `0x31, 0xFA, 0xB6`)

---

## Key Files (read in this order)

| # | File | Purpose |
|---|------|---------|
| 1 | `SESSION_STATE_2026-10-20.md` | **THIS FILE** — current state |
| 2 | `SESSION_REPORT_2026-10-20.md` | Corrected analysis with evidence |
| 3 | `QUICK_REFERENCE.md` | Quick reference (all key facts) |
| 4 | `REVERSE_ENGINEERING_NOTES.md` | SoftRF Legacy protocol spec (firmware-verified) |
| 5 | `NOTES.md` | Firmware source citations with GitHub links |
| 6 | `SYSTEM_FACTS.md` | Verified protocol constants with file/line citations |
| 7 | `DEVELOPMENT_RULES.md` | Rules and methodology |
| 8 | `CAPTURE_CONFIDENCE_REPORT.md` | Capture inventory and quality |

### Superseded Documents (DO NOT USE for current understanding)

| File | Why superseded |
|------|---------------|
| `CRITICAL_FINDINGS_2026-10-12.md` | OOK/ASK conclusion rejected |
| `FSK_HYPOTHESIS_DISPROVEN.md` | Wrong offset estimate |
| `OOK_DECODING_ATTEMPT.md` | Wrong modulation |
| `OOK_DECODE_ATTEMPT.md` | Wrong modulation |
| `FINAL_SESSION_REPORT_2026-10-13.md` | OOK/ASK conclusion |
| `SESSION_SUMMARY_2026-10-13.md` | OOK/ASK conclusion |
| `ANALYSIS_INVALID_CAPTURE.md` | Based on wrong offset |
| `FHSS_REMEDIATION.md` / `FHSS_REMEDIATION_SUMMARY.md` | FHSS conclusion unverified |
| `BURST_ANALYSIS_2026-10-13.md` | Burst detection valid, OOK/ASK classification wrong |
| `analysis_long_sample.md` | Historical analysis |
| `stage0_signal_presence.md` | Historical analysis |
| `COMMIT_SUMMARY.md` | Historical commit log |

---

## Data Files

| File | Description |
|------|-------------|
| `/home/ubuntu/softrf-decoder/baseband_915000000Hz_20-35-24_03-10-2026.wav` | Primary capture (545 MB, 30s) |
| `/home/ubuntu/long_baseband_915000000Hz_18-26-17_19-10-2026.wav` | Long capture (4.6 GB, 397s) |
| `/home/ubuntu/.openclaw/workspace/baseband_915000000Hz_20-35-24_03-10-2026.wav` | Working copy |
| `silence_baseband_*.wav` | Noise floor references |

All captures: 20 MS/s, 32-bit float, I/Q interleaved WAV.

---

## Scripts

21 Python scripts in the repo root. Key ones:

| Script | Purpose |
|--------|---------|
| `deep_analysis.py` | Time/frequency/phase analysis |
| `fsk_demod.py` | FSK demodulator v2 |
| `COHERENT_demod.py` | Coherent demodulation |
| `realty_check.py` | Phase coherence check |
| `fft_analysis.py` | FFT-based FSK analysis |
| `characterize.py` | Signal characterization |
| `demodulate_hops.py` | Frequency hopping demodulation |
| `extract_bitstream.py` | Bitstream extraction |
| `protocol_analysis.py` | Protocol analysis |
| `verify_freqplan.py` | Frequency plan verification |

All scripts assume the OLD frequency offset. They need updating for the
corrected offset (-8.733 MHz).

---

## Key Technical Details

### SoftRF Legacy Protocol (Firmware-Verified)

| Parameter | Value | Source |
|-----------|-------|--------|
| Modulation | 2-FSK (GFSK) | `Legacy.h:145` |
| Data rate | 100 kbps | `Legacy.h:145` |
| Freq deviation | ±18 kHz (915 MHz) | `Legacy.h:145` |
| Sync word | `55 99 A5 A9 55 66 65 96` | `Legacy.h:145` |
| Encryption | XXTEA | `Legacy.cpp:90` |
| CRC | CCITT-F, pre-seed `0x31, 0xFA, 0xB6` | `Legacy.cpp:90` |
| Channel encoding | 2:1 repeat | `Legacy.cpp:90` |
| Bit order | LSB first | `Legacy.cpp:90` |
| Payload size | 10 bytes max | `Legacy.h:145` |
| Frame | Sync + Length + Payload + CRC | `Legacy.cpp:90` |

### XXTEA Key (from `Legacy.cpp:141`)

```
0xe43276df 0xdca83759 0x9802b8ac 0x9e3779b9
```

### CCITT-F CRC

- Polynomial: `0x1021`
- Initial value: `0xFFFF`
- Pre-seed: `0x31, 0xFA, 0xB6`
- Reference: `lib_crc.cpp:183`

### Frequency Plan (from `radiolib.cpp:1320`)

- Base: 915.0 MHz
- Channel spacing: 1 MHz (915.000, 916.000, ..., 927.000 MHz)
- US ISM band: 902–928 MHz

### XXTEA Constants

- Delta: `0x9e3779b9` (golden ratio)
- XXTEA key: `e43276df dca83759 9802b8ac 9e3779b9`

---

## Session History

| Date | Key Events |
|------|-----------|
| Oct 12 | Initial analysis. FSK hypothesis proposed then "disproven" (wrong). OOK/ASK concluded (wrong). |
| Oct 13 | Burst analysis. 12 consistent ~5.17ms bursts found. OOK/ASK "confirmed" (wrong). |
| Oct 19 | Long capture (397s) analyzed. 79 bursts found. FHSS "confirmed" (unverified). |
| **Oct 20** | **CRITICAL CORRECTION**: Frequency offset corrected to -8.733 MHz. OOK/ASK rejected. FSK re-opened. SNR ~29.1 dB. All documentation updated. |

---

## Rules and Constraints

1. **Source priority**: 1) Firmware source, 2) Validated RF captures, 3) `SYSTEM_FACTS.md`, 4) Project docs
2. **No speculation without citation**: All protocol claims must cite firmware source or RF capture evidence
3. **Stop researching when told**: Gateway-owner instruction takes priority
4. **No push**: User pushes manually
5. **Disposable instance**: Cloud instance, chat persists, code persists

---

## Repository Structure

```
softrf-decoder/
├── SESSION_STATE_2026-10-20.md   ← THIS FILE (start here)
├── SESSION_REPORT_2026-10-20.md  ← Corrected analysis
├── QUICK_REFERENCE.md            ← Quick reference
├── REVERSE_ENGINEERING_NOTES.md  ← Protocol spec
├── NOTES.md                      ← Firmware citations
├── SYSTEM_FACTS.md               ← Verified constants
├── DEVELOPMENT_RULES.md          ← Rules
├── CAPTURE_CONFIDENCE_REPORT.md  ← Capture inventory
├── DOCUMENTATION_COMPLIANCE_REPORT.md
├── HANDOFF.md                    ← Handoff document
├── STATUS.md                     ← Status
├── DECODE_STATUS.md              ← Decode status
├── CURRENT_BLOCKERS.md           ← Blockers (all resolved)
├── README.md                     ← Repo README
├── RESUME_FROM_SCRATCH.md        ← Starting guide
├── MVP_SCOPE.md                  ← MVP scope
├── PROJECT_CHARTER.md            ← Charter
├── PROJECT_SPEC.md               ← Spec
├── ARCHITECTURE.md               ← Architecture
├── FHSS_REMEDIATION.md           ← FHSS remediation (historical)
├── FHSS_REMEDIATION_SUMMARY.md   ← FHSS summary (historical)
├── COMMIT_SUMMARY.md             ← Commit log (historical)
├── analysis_long_sample.md       ← Historical analysis
├── stage0_signal_presence.md     ← Historical analysis
├── BURST_ANALYSIS_2026-10-13.md  ← Burst analysis (partially superseded)
├── CRITICAL_FINDINGS_2026-10-12.md ← SUPERSEDED
├── FSK_HYPOTHESIS_DISPROVEN.md   ← SUPERSEDED
├── OOK_DECODING_ATTEMPT.md       ← SUPERSEDED
├── OOK_DECODE_ATTEMPT.md         ← SUPERSEDED
├── FINAL_SESSION_REPORT_2026-10-13.md ← SUPERSEDED
├── SESSION_SUMMARY_2026-10-13.md ← SUPERSEDED
├── ANALYSIS_INVALID_CAPTURE.md   ← SUPERSEDED
├── SESSION_FINDINGS.md           ← Consolidated findings
├── prototype/                    ← Early prototype scripts
├── *.py                          ← 21 analysis scripts
├── *.png                         ← 7 analysis plots
└── *.wav                         ← (referenced, not in repo)
```
