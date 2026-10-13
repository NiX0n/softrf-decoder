# SoftRF Decoder - Status

## Current Status: SNR-LIMITED

The capture at `/home/ubuntu/.openclaw/workspace/baseband_915000000Hz_20-35-24_03-10-2026.wav`
contains a very weak OOK/ASK signal that is **below the decode threshold** for basic
demodulation techniques.

### What We Know
- **Signal type:** OOK/ASK (envelope modulation, NOT FSK)
- **Center frequency:** 915 MHz exact
- **Sample rate:** 20 MS/s
- **Bandwidth:** 20 MHz
- **Duty cycle:** ~10% (per task description)
- **SNR:** < 1 dB (signal buried in noise)

### What We've Tried
1. **2-FSK demodulation** → Disproven (frequency not modulated, only envelope)
2. **Basic OOK thresholding** → Fails (SNR too low, noise and signal indistinguishable)
3. **Burst detection** → No clear bursts (signal spread across entire capture)
4. **Sync word search** → No sync pattern found (bits are random-looking due to noise)
5. **Multiple symbol rates** → No improvement (all hit same SNR wall)

### What Would Help
1. **Longer capture** (10+ seconds) for noise averaging
2. **Better receiver** with lower noise figure
3. **Known reference frame** for matched filtering
4. **OR:** Accept that this capture is below the decode threshold

### Next Steps
- [ ] Obtain a stronger capture or better receiver
- [ ] If possible, record a known command frame for matched filtering
- [ ] Try averaging multiple captures if signal is coherent
- [ ] Consider time-domain correlation with expected protocol patterns

## Key Files
- `FSK_HYPOTHESIS_DISPROVEN.md` - Why FSK is wrong
- `CHECK_SIGNAL_REPORT.md` - Detailed SNR analysis
- `RESUME_FROM_SCRATCH.md` - How to start fresh
- `check_signal.py` - Quick signal characterization

## Conclusion
This is not a decoder bug. This is a **signal quality limitation**. The tools are correct;
the signal is just too weak to decode without additional processing or a better capture.
