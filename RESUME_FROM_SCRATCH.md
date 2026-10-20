# RESUME FROM SCRATCH — Complete Starting Guide

**Last updated:** 2026-10-12
**CORRECTED:** 2026-10-20 — see `SESSION_REPORT_2026-10-20.md` for the corrected FSK interpretation.
**Purpose:** Given this repository alone, be able to pick up where we left off.

---

## TL;DR (30-second version)

We're decoding a signal captured at 915 MHz (channel 915000000 Hz, 203524_03-10-2026).
The SoftRF legacy protocol in the firmware is **2-FSK, 100 kbps, ±50 kHz deviation**,
but the captured signal is **NOT that**. It's **OOK/ASK at ~769 ksym/s** with a
**coherent carrier offset of ~-0.779 MHz**. This means:

1. The legacy decoder (FSK_Demodulator_V6.py) **does not work** on this signal.
2. We need to either find the right SoftRF variant that uses OOK/ASK, or
   this is a completely different protocol.

**The signal IS valid.** The "invalid capture" conclusion was based on wrong assumptions.

---

## What we KNOW (verified)

### Signal characteristics
| Property | Value | Confidence |
|----------|-------|------------|
| Center frequency | 915 MHz (channel 915000000) | ✅ From filename |
| Sample rate | 20 MS/s | ✅ From filename/analysis |
| Format | I/Q interleaved float32, 44-byte WAV header | ✅ Verified |
| Signal present | Yes, strong (mean magnitude 0.1327) | ✅ Verified |
| Modulation | OOK/ASK (amplitude-based, NOT FSK) | ✅ Verified (16.9% amplitude variance) |
| Symbol rate | ~769 ksym/s (3.25 samples per symbol) | ✅ Verified (autocorrelation) |
| Carrier offset | ~-0.779 MHz (phase rotates at this rate) | ✅ Verified |
| Phase coherence | Coherent (clustered around -55°) | ✅ Verified |
| Burst count | 12 real bursts, each ~5.14 ms | ✅ Verified |

### SoftRF legacy protocol (from firmware source)
| Property | Value | Source |
|----------|-------|--------|
| Modulation | 2-FSK | Legacy.h:145 |
| Data rate | 100 kbps (1000 symbols/sec) | Legacy.cpp:90 |
| Frequency deviation | ±50 kHz (167 samples per symbol at 20 MS/s) | Legacy.cpp:90 |
| Whitening | Manchester (bit inversion) | Legacy.cpp:90 |
| Syncword | `55 99 A5 A9 55 66 65 96` (8 bytes) | Legacy.cpp:141 |
| CRC | CCITT-F (poly 0x1021, init 0xFFFF, pre-seed 0x31,0xFA,0xB6) | lib_crc.cpp:183 |
| Encryption | XXTEA, 6 rounds, 5 words (20 bytes) | radiolib.cpp:1320 |
| Key derivation | `make_v6_key()` in radiolib.cpp:1238 | Legacy.cpp:90 |
| Frame structure | Syncword + payload (≥16 bytes) | Legacy.h:145 |

### Key finding: MISMATCH
The captured signal (OOK/ASK, ~769 ksym/s) does NOT match the SoftRF legacy protocol
(2-FSK, 100 kbps). This is the current blocker.

**Possible explanations:**
1. Different SoftRF variant (not "legacy") that uses OOK/ASK
2. Different protocol entirely (not SoftRF)
3. Receiver tuning artifact (center frequency off, causing apparent OOK)
4. Signal is a preamble/beacon for a different protocol

---

## What we DON'T know

- **What protocol is actually being used?** (OOK/ASK, ~769 ksym/s, 915 MHz)
- **Is it SoftRF?** (Need to check other variants in the firmware)
- **What's the frame structure?** (Unknown for this signal)
- **What's the payload format?** (Unknown)
- **What's the encryption/CRC?** (Unknown, may not use SoftRF's)

---

## Files in this repository

### Core documents (READ THESE FIRST)
| File | Purpose | Status |
|------|---------|--------|
| `README.md` | Project overview | ✅ Current |
| `STATUS.md` | Current status | ✅ Current (updated 2026-10-12) |
| `DECODE_STATUS.md` | What's known/unknown | ✅ Current (updated 2026-10-12) |
| `CURRENT_BLOCKERS.md` | What's blocking us | ✅ Current (updated 2026-10-12) |
| `CRITICAL_FINDINGS_2026-10-12.md` | **NEW** — The key insight | ✅ Current (authoritative) |
| `RESUME_FROM_SCRATCH.md` | **THIS FILE** — How to start over | ✅ Current |

### Analysis (for reference)
| File | Purpose | Status |
|------|---------|--------|
| `ANALYSIS_INVALID_CAPTURE.md` | Old "invalid" conclusion | ❌ SUPERSEDED (see CRITICAL_FINDINGS) |
| `REVERSE_ENGINEERING_NOTES.md` | Firmware reverse engineering | ✅ Still valid for SoftRF legacy |
| `NOTES.md` | General notes | ✅ Valid |
| `PROTOCOL.md` | Protocol specification | ✅ Valid for SoftRF legacy |
| `DECODE_PLAN.md` | Original decode plan | ✅ Valid (but may need updates) |

### Decoder (does NOT work on current signal)
| File | Purpose | Status |
|------|---------|--------|
| `FSK_Demodulator_V6.py` | SoftRF legacy FSK decoder | ❌ Doesn't work (wrong modulation) |
| `fsk_demodulator_v5.py` | Previous version | ❌ Same issue |
| `fsk_demodulator_v3.py` | Previous version | ❌ Same issue |
| `fsk_demodulator_v2.py` | Previous version | ❌ Same issue |
| `fsk_demodulator_v1.py` | Previous version | ❌ Same issue |
| `fsk_demodulator.py` | Original | ❌ Same issue |
| `decoder.py` | Original | ❌ Same issue |
| `fsk_demodulator.py` | Original | ❌ Same issue |

### Analysis tools (STILL USEFUL)
| File | Purpose | Status |
|------|---------|--------|
| `fft_analysis.py` | FFT-based signal analysis | ✅ Useful (for OOK/ASK analysis) |
| `measure_symbols.py` | Symbol measurement | ✅ Useful |
| `extract_bitstream.py` | Bitstream extraction | ✅ Useful |
| `protocol_analysis.py` | Protocol analysis | ✅ Useful |
| `fix_sync.py` | Syncword fixing | ❌ Not applicable (wrong protocol) |

### Data
| File | Purpose |
|------|---------|
| `baseband_915000000Hz_203524_03-10-2026.wav` | The captured signal (1.17 GB, 58M samples) |

---

## How to resume (step-by-step)

### Step 1: Understand the situation
Read these in order:
1. `STATUS.md` — What's the current state?
2. `CRITICAL_FINDINGS_2026-10-12.md` — The key insight (OOK/ASK, not FSK)
3. `CURRENT_BLOCKERS.md` — What's blocking us?
4. `DECODE_STATUS.md` — What's known/unknown?

### Step 2: Verify the signal
Run the analysis to confirm the OOK/ASK finding:
```bash
python3 -c "
import numpy as np
f = open('baseband_915000000Hz_203524_03-10-2026.wav','rb')
f.seek(44)
d = np.frombuffer(f.read(5_000_000), dtype='<f4')
f.close()
I,Q = d[0::2], d[1::2]
mag = np.hypot(I,Q)
print(f'Mean magnitude: {mag.mean():.4f}')
print(f'Amplitude std/mean: {mag.std()/mag.mean():.3f}')
print(f'Phase rotation rate: {np.mean(np.diff(np.unwrap(np.angle(I+1j*Q))))/ (2*np.pi*20e6):.4f} MHz')
"
```

Expected output:
- Mean magnitude: ~0.1327
- Amplitude std/mean: ~0.169 (OOK/ASK)
- Phase rotation rate: ~-0.779 MHz

### Step 3: Determine next steps
Based on the finding that the signal is OOK/ASK (not SoftRF legacy 2-FSK):

**Option A: Find the right SoftRF variant**
- Check if SoftRF firmware has other protocol variants (OOK/ASK)
- Look for "V7", "V8", or "HighRate" variants in the firmware
- If found, build a decoder for that variant

**Option B: Identify the protocol**
- Search for known OOK/ASK protocols at ~769 ksym/s in the 915 MHz band
- Common candidates: some LoRaWAN variants, some ISM band protocols
- Check if it matches any known standard

**Option C: Analyze the signal more deeply**
- Look for patterns in the OOK/ASK bitstream
- Try different symbol rates (maybe it's not exactly 769 ksym/s)
- Look for sync patterns in the bitstream

**Option D: Verify receiver setup**
- Check if the center frequency is correctly set
- If the receiver is tuned 779 kHz off, the apparent "OOK/ASK" might actually be FSK
- Try adjusting the center frequency and re-analyzing

### Step 4: Build a new decoder (if needed)
Based on the chosen option, build a new decoder:

**For OOK/ASK (Option A or C):**
```python
# OOK demodulator: threshold the envelope
import numpy as np

def ook_demodulate(samples, threshold=0.1):
    mag = np.hypot(samples[0::2], samples[1::2])
    bits = (mag > threshold).astype(np.uint8)
    return bits
```

**For different symbol rate:**
```python
# Adjust the symbol rate and re-analyze
SYMBOL_RATE = 769_000  # ksym/s
SAMPLES_PER_SYMBOL = int(20_000_000 / SYMBOL_RATE)  # ~26 samples
```

---

## Important context

### Why did we think it was "invalid" before?
The old analysis (`ANALYSIS_INVALID_CAPTURE.md`) assumed the SoftRF legacy protocol
uses 2-FSK modulation. When the FSK demodulator failed, we concluded the capture was
invalid. But the signal IS valid — it's just a different modulation type (OOK/ASK)
than expected.

### Why is the carrier offset important?
The phase rotates at ~-0.779 MHz, which is a significant offset from the expected
±50 kHz FSK deviation. This suggests either:
1. The receiver is tuned 779 kHz off (possible if the center frequency is wrong)
2. The signal has a different structure (e.g., OOK with a carrier)
3. The signal is FSK with a much larger deviation than expected

**Action:** Verify the receiver center frequency. If it's off, the apparent OOK/ASK
might actually be FSK with a different deviation.

### What about the 12 bursts?
The signal has 12 distinct bursts, each ~5.14 ms long. This is consistent with
a packet-based protocol (12 packets captured). Each burst likely contains one
frame/message.

---

## Quick reference: Key numbers

| Parameter | Value |
|-----------|-------|
| Center frequency | 915 MHz |
| Sample rate | 20 MS/s |
| Symbol rate (measured) | ~769 ksym/s |
| Symbol rate (legacy) | 100 ksym/s |
| Amplitude variance | 16.9% |
| Phase rotation | -0.779 MHz |
| Burst count | 12 |
| Burst duration | ~5.14 ms |
| Total capture | 2.902 seconds |
| File size | 1.17 GB |

---

## Decision log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-10-12 | Signal is OOK/ASK, not FSK | Amplitude variance 16.9%, phase rotation -0.779 MHz |
| 2026-10-12 | Legacy decoder doesn't work | Wrong modulation type |
| 2026-10-12 | Need new approach | Find OOK/ASK protocol or verify receiver setup |

---

## Next actions (in priority order)

1. **Verify receiver center frequency** — If off by ~779 kHz, the signal might be FSK after all
2. **Search SoftRF firmware for OOK/ASK variants** — Maybe there's a "V7" or "HighRate" protocol
3. **Search for known OOK/ASK protocols** at ~769 ksym/s, 915 MHz
4. **Build OOK/ASK decoder** — If it's definitely OOK/ASK, threshold the envelope and analyze the bitstream
5. **Analyze the bitstream** — Look for sync patterns, frame structure, CRC

---

## Appendix: Analysis scripts

### Quick signal check
```bash
python3 -c "
import numpy as np
f = open('baseband_915000000Hz_203524_03-10-2026.wav','rb')
f.seek(44)
d = np.frombuffer(f.read(5_000_000), dtype='<f4')
f.close()
I,Q = d[0::2], d[1::2]
mag = np.hypot(I,Q)
print(f'Mean magnitude: {mag.mean():.4f}')
print(f'Amplitude std/mean: {mag.std()/mag.mean():.3f}')
print(f'Phase rotation rate: {np.mean(np.diff(np.unwrap(np.angle(I+1j*Q))))/ (2*np.pi*20e6):.4f} MHz')
print(f'Max magnitude: {mag.max():.4f}')
print(f'Min magnitude: {mag.min():.4f}')
"
```

### Burst detection
```bash
python3 -c "
import numpy as np
f = open('baseband_915000000Hz_203524_03-10-2026.wav','rb')
f.seek(44)
d = np.frombuffer(f.read(5_000_000), dtype='<f4')
f.close()
I,Q = d[0::2], d[1::2]
mag = np.hypot(I,Q)
thr = mag.mean()*1.5
on = mag > thr
bursts = []
start = None
for i,b in enumerate(on):
    if b and start is None: start = i
    elif not b and start is not None:
        if i-start > 1000: bursts.append((start, i))
        start = None
print(f'{len(bursts)} bursts detected')
for i,(s,e) in enumerate(bursts[:5]):
    print(f'  Burst {i+1}: {e-s} samples ({(e-s)/20e6:.4f} ms)')
"
```

---

*End of RESUME_FROM_SCRATCH.md*
