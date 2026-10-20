# softrf-decoder

Decoder for SoftRF 915 MHz radio protocol (EasyLink-compatible).

> **⚠️ START HERE: [SESSION_STATE_2026-10-20.md](SESSION_STATE_2026-10-20.md)**
> That file is the authoritative current-state document. Everything else is
> historical or superseded.

> **CORRECTION (2026-10-20):** The signal in the capture IS the SoftRF Legacy
> protocol (2-FSK, 100 kbps, XXTEA, CCITT). The prior "signal is OOK/ASK, not
> SoftRF" conclusion was based on a wrong frequency offset (-8.733 MHz, not
> +11.23 MHz). See `SESSION_REPORT_2026-10-20.md` for the full corrected analysis.

## Current Status (2026-10-20)

- **Modulation**: FSK (2-FSK, 100 kbps, GFSK, ±18 kHz) — OOK/ASK rejected
- **Carrier offset**: -8.733 MHz (corrected)
- **Burst SNR**: ~29.1 dB (sufficient for decoding)
- **Protocol**: SoftRF Legacy (firmware-verified)
- **Decoding**: NOT YET SUCCEEDED — next step is FM demodulation + sync search

## Documentation Index

### Read First (Current)

| File | Purpose |
|------|---------|
| [`SESSION_STATE_2026-10-20.md`](SESSION_STATE_2026-10-20.md) | **AUTHORITATIVE current state** — start here |
| [`SESSION_REPORT_2026-10-20.md`](SESSION_REPORT_2026-10-20.md) | Corrected analysis with evidence |
| [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) | Quick reference — all key facts in one page |
| [`REVERSE_ENGINEERING_NOTES.md`](REVERSE_ENGINEERING_NOTES.md) | SoftRF Legacy protocol spec (firmware-verified) |
| [`NOTES.md`](NOTES.md) | Firmware source citations with GitHub links |
| [`SYSTEM_FACTS.md`](SYSTEM_FACTS.md) | Verified protocol constants with file/line citations |
| [`DEVELOPMENT_RULES.md`](DEVELOPMENT_RULES.md) | Rules and methodology |
| [`CAPTURE_CONFIDENCE_REPORT.md`](CAPTURE_CONFIDENCE_REPORT.md) | Capture inventory and quality assessment |

### Project Management

| File | Purpose |
|------|---------|
| [`STATUS.md`](STATUS.md) | Current status summary |
| [`DECODE_STATUS.md`](DECODE_STATUS.md) | Decode progress tracking |
| [`CURRENT_BLOCKERS.md`](CURRENT_BLOCKERS.md) | Blockers (all resolved) |
| [`HANDOFF.md`](HANDOFF.md) | Handoff document |
| [`RESUME_FROM_SCRATCH.md`](RESUME_FROM_SCRATCH.md) | Starting guide for new sessions |
| [`MVP_SCOPE.md`](MVP_SCOPE.md) | MVP scope definition |
| [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) | Project charter |
| [`PROJECT_SPEC.md`](PROJECT_SPEC.md) | Project specification |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | System architecture |

### Historical (Superseded — read only for context)

| File | Why superseded |
|------|---------------|
| [`CRITICAL_FINDINGS_2026-10-12.md`](CRITICAL_FINDINGS_2026-10-12.md) | OOK/ASK conclusion rejected (2026-10-20) |
| [`FSK_HYPOTHESIS_DISPROVEN.md`](FSK_HYPOTHESIS_DISPROVEN.md) | Wrong offset estimate |
| [`OOK_DECODING_ATTEMPT.md`](OOK_DECODING_ATTEMPT.md) | Wrong modulation |
| [`OOK_DECODE_ATTEMPT.md`](OOK_DECODE_ATTEMPT.md) | Wrong modulation |
| [`FINAL_SESSION_REPORT_2026-10-13.md`](FINAL_SESSION_REPORT_2026-10-13.md) | OOK/ASK conclusion |
| [`SESSION_SUMMARY_2026-10-13.md`](SESSION_SUMMARY_2026-10-13.md) | OOK/ASK conclusion |
| [`ANALYSIS_INVALID_CAPTURE.md`](ANALYSIS_INVALID_CAPTURE.md) | Based on wrong offset |
| [`BURST_ANALYSIS_2026-10-13.md`](BURST_ANALYSIS_2026-10-13.md) | Burst detection valid, OOK/ASK classification wrong |
| [`FHSS_REMEDIATION.md`](FHSS_REMEDIATION.md) | FHSS conclusion unverified |
| [`FHSS_REMEDIATION_SUMMARY.md`](FHSS_REMEDIATION_SUMMARY.md) | FHSS conclusion unverified |
| [`analysis_long_sample.md`](analysis_long_sample.md) | Historical analysis |
| [`stage0_signal_presence.md`](stage0_signal_presence.md) | Historical analysis |
| [`COMMIT_SUMMARY.md`](COMMIT_SUMMARY.md) | Historical commit log |
| [`SESSION_FINDINGS.md`](SESSION_FINDINGS.md) | Consolidated findings (superseded by SESSION_STATE) |
| [`DOCUMENTATION_COMPLIANCE_REPORT.md`](DOCUMENTATION_COMPLIANCE_REPORT.md) | Compliance snapshot |

### SoftRF Firmware (external, not committed)

The SoftRF firmware source is **not** a dependency of this repo. All citations reference
the public firmware repository:

- **Repo**: https://github.com/lyusupov/SoftRF
- **Commit**: `973a8d73`, branch `master`
- **Base URL for file links**: `https://github.com/lyusupov/SoftRF/blob/master/`

Key files (append to base URL):

| File | What it contains |
|------|-----------------|
| `software/firmware/source/SoftRF/src/protocol/radio/Legacy.h` | Syncword, payload size, CRC type, key definitions |
| `software/firmware/source/SoftRF/src/protocol/radio/Legacy.cpp` | `legacy_proto_desc`, `legacy_encode`/`legacy_decode`, XXTEA, coordinate conversion |
| `software/firmware/source/SoftRF/src/driver/RF.h` | RF constants (modulation, whitening, bit order) |
| `software/firmware/source/SoftRF/src/driver/radio/radiolib_extra.cpp` | CC1101 register setup |
| `software/firmware/source/SoftRF/src/driver/radio/radiolib.cpp` | Frequency plan |
| `software/firmware/source/SoftRF/src/protocol/crc/lib_crc.cpp` | CRC implementation |

## Scripts

21 Python analysis scripts in the repo root. See `SESSION_STATE_2026-10-20.md` for details.

## Prototype

`prototype/` directory contains early Python reference implementation:
- `decode.py` — initial decoder
- `decode_v2.py` — improved decoder
- Plus analysis plots (`.png`)
