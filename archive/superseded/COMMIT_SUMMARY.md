# Commit Summary — 2026-10-12

## Pending Push (5 commits ahead of origin)

### 1. `8953549` — Add: deep signal analysis and FSK demodulator v2 scripts
- `deep_analysis.py` — Time domain, frequency domain, and phase analysis
- `fsk_demod.py` — FSK demodulator v2 with robust burst detection

### 2. `370218c` — Update status: capture invalid, decoder implementation complete
- `DECODE_STATUS.md` — Updated with analysis findings and recommendations

### 3. `b348674` — Add analysis: capture is invalid (CW tone, not FSK)
- `ANALYSIS_INVALID_CAPTURE.md` — Detailed analysis with evidence

### 4. `273e18d` — Add FFT-based FSK analysis script with validated threshold
- `fft_analysis.py` — FFT peak analysis script

### 5. `549c62a` — Fix: Correct FHSS frequency plan (65ch 902.2-927.8MHz, 400kHz spacing)
- `SYSTEM_FACTS.md` — Corrected frequency plan

## Key Files

### Python Scripts
- `deep_analysis.py` — Signal analysis (time, frequency, phase domain)
- `fft_analysis.py` — FFT peak analysis
- `fsk_demod.py` — FSK demodulator v2
- `prototype/decode.py` — Decoder prototype (complete)
- `verify_freqplan.py` — Frequency plan verification

### Documentation
- `ANALYSIS_INVALID_CAPTURE.md` — **NEW** — Analysis showing capture is invalid
- `DECODE_STATUS.md` — Updated status with recommendations
- `SYSTEM_FACTS.md` — Verified protocol facts + corrections
- `CURRENT_BLOCKERS.md` — Status matrix (accurate)
- `REVERSE_ENGINEERING_NOTES.md` — Protocol research
- `NOTES.md` — Full protocol research with citations

## Key Finding

**The captured WAV file does NOT contain a valid 2-FSK signal.**

- Signal is a CW tone at ~6.78 MHz relative to receiver LO
- No distinct bursts — envelope uniformly distributed
- FFT shows spurs at integer fractions of sample rate
- Phase is not changing (instantaneous frequency = 0.0 kHz)

**The decoder implementation is complete. The input signal is the problem.**

## Next Steps

1. Verify SDR setup with user
2. Recapture signal with known-good setup
3. Re-run decoder with new capture
4. Verify results (syncword, CRC, payload)
