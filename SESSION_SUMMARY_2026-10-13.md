# R&D Session Summary - 2026-10-13

## Mission
Decode the SoftRF 915 MHz signal and produce a working decoder + reverse-engineering docs.

## Key Discovery: 2-FSK Hypothesis DISPROVEN

### Evidence
1. **Phase is coherent** (not random)
   - `reality_check.py`: phase offset = 0.94 rad (-0.94 rad from expected)
   - `COHERENT_demod.py`: residual frequency offset = 0.0 Hz after rotation
   - This rules out FSK, which would have random phase per frequency hop

2. **Envelope shows bimodal distribution**
   - Noise floor: ~0.030 (92.76% of samples)
   - Signal peaks: ~0.225-0.273 (1.23% of samples)
   - 100ms windows with 8.5% duty cycle above 0.05 threshold
   - This is characteristic of OOK/ASK, not FSK

3. **Spectral width is suspicious**
   - 26.12 kHz (6.5 ms timescale)
   - Too narrow for 2-FSK with 769 ksym/s symbol rate
   - More consistent with OOK pulse width or narrowband noise

### Conclusion
**The signal is OOK/ASK (On-Off Keying / Amplitude Shift Keying), NOT 2-FSK.**

## OOK/ASK Decoding Attempt

### What We Tried
1. **Coherent demodulation** - rotated by +0.94 rad
2. **Threshold calibration** - tried Otsu, percentiles, sweep
3. **Symbol extraction** - found 4.5M ON runs and 4.5M OFF runs
4. **Sync word search** - failed to find 64-bit sync pattern

### Problem
**SNR is too low for reliable symbol-level decoding.**

- Minimum ON run: 1 sample (0.05 ms)
- Minimum OFF run: 1 sample (0.05 ms)
- This is noise, not real OOK symbols
- The 100ms bursts are present, but individual symbols are buried in noise

## What We Know for Certain

### ✅ Verified Facts
1. **Receiver configuration**
   - Center frequency: **915.000 MHz** (exactly, as specified)
   - Sample rate: **20 MS/s**
   - Bandwidth: **20 MHz**
   - I/Q interleaved float32 WAV (44-byte header)

2. **Signal modulation**
   - **OOK/ASK** (not FSK)
   - Coherent phase (can use coherent demodulation)
   - 100ms bursts with ~8.5% duty cycle

3. **Signal presence**
   - Present in capture (100ms windows with elevated envelope)
   - SNR is poor (noise floor ~0.03, signal peaks ~0.25)

### ❌ Unknown
1. **Exact symbol rate** (couldn't measure reliably due to noise)
2. **Bitstream content** (couldn't decode due to SNR)
3. **Why 26.12 kHz spectral width** (could be OOK pulse shape, or narrowband noise)

## Files Created/Updated

### Key Documentation
- `FSK_HYPOTHESIS_DISPROVEN.md` - formal record of why FSK was rejected
- `OOK_DECODING_ATTEMPT.md` - OOK/ASK decoding attempt and findings
- `STATUS.md` - current status (updated)
- `RESUME_FROM_SCRATCH.md` - comprehensive handoff doc (updated)
- `CURRENT_BLOCKERS.md` - updated with OOK SNR issue

### Scripts (OBSOLETE)
- `fsk_demod.py` - marked OBSOLETE
- `demodulate_hops.py` - marked OBSOLETE
- `fft_analysis.py` - marked OBSOLETE
- `fix_sync.py` - marked OBSOLETE

### Scripts (VALID)
- `characterize.py` - spectral analysis
- `measure_symbols.py` - symbol measurement
- `extract_bitstream.py` - bitstream extraction
- `protocol_analysis.py` - protocol analysis
- `check_signal.py` - basic signal checks
- `reality_check.py` - phase coherence check
- `COHERENT_demod.py` - coherent demodulation
- `OOK_decoder_v2.py` / `v3.py` - OOK decoders
- `OOK_calibrate.py` / `OOK_threshold_sweep.py` - threshold calibration

## Recommendations for Next Session

1. **Capture a better signal** (higher SNR)
   - Move antenna closer to transmitter
   - Use a better receiver (lower noise figure)
   - Increase integration time

2. **Try advanced OOK demodulation**
   - Matched filtering
   - Energy detection
   - Adaptive thresholding

3. **Consider other modulations**
   - Could it be PWM (Pulse Width Modulation)?
   - Could it be PPM (Pulse Position Modulation)?
   - Could it be a narrowband FSK we misidentified?

4. **Check the 26.12 kHz spectral width**
   - What causes this?
   - Is it the OOK pulse shape?
   - Or is it narrowband interference?

## Status
**BLOCKED**: Signal present but SNR too low for reliable decoding.

**Next step**: Capture a cleaner signal, then retry OOK/ASK decoding.

## Git
All work committed locally (branch `main`).
Push to GitHub failing due to credential issues (HTTPS helper not available).
