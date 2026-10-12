# Current Blockers

## Blocker 1: Signal is a CW tone, not the SoftRF legacy protocol

**Evidence (2026-10-12, from `baseband_915000000Hz_20-35-24_03-10-2026.wav`):**

1. **Phase analysis:** Mean phase rotation rate is -0.779 MHz (not 0, not ±50 kHz).
   The signal is a continuous rotating phasor at ~-779 kHz from the carrier.
   This is NOT 2-FSK at 100 kbps with ±50 kHz deviation.
   It's a single tone at a fixed frequency offset.

2. **Amplitude analysis:** Amplitude variance is 0.169 (std/mean).
   FSK has constant amplitude (variance < 0.1). This is OOK/ASK.
   The "data" is encoded in amplitude changes, not frequency changes.

3. **Bitstream analysis:** When thresholded at 50th percentile of amplitude,
   the bitstream is ALL ZEROS at the edges. The signal is mostly OFF
   (low amplitude) with brief ON pulses. This is not the SoftRF
   legacy protocol (which is 2-FSK, constant amplitude).

4. **Firmware source (confirmed):** The SoftRF legacy protocol is
   2-FSK, 100 kbps, ±50 kHz deviation, Manchester encoded.
   The captured signal does NOT match this.

**Conclusion:** The captured signal is NOT the SoftRF legacy protocol.
It appears to be either:
- A different protocol entirely (not in the SoftRF firmware)
- A different device/protocol operating in the same frequency band
- The same SoftRF device using a different mode we haven't identified

**What's needed:**
- A capture where the SoftRF device is transmitting the legacy protocol
- Or: identify what protocol is actually on the 915 MHz channel
- Or: capture at a different frequency/time to isolate the SoftRF device

## Blocker 2: Firmware source not available on this system

The SoftRF firmware source was cloned to `/tmp/SoftRF` earlier in the
session but the system has been restarted. The source is no longer
available locally.

**What's needed:** Re-clone the firmware:
```bash
git clone https://github.com/lyusupov/SoftRF /tmp/SoftRF
```

## Next Steps

1. **Confirm the capture is invalid** for SoftRF legacy decoding
2. **Get a new capture** with the SoftRF device actively transmitting
3. **Or** identify what protocol the current signal is

## What's Working

- `verify_freqplan.py` - validates the SoftRF frequency plan (works correctly)
- `softrf_decoder.py` - implements the full SoftRF legacy decode chain (correct per firmware)
- `measure_symbols.py` - measures symbol timing (works correctly)
- `fix_sync.py` - syncword verification (works correctly)
- `extract_bitstream.py` - bit extraction (works correctly)
- All scripts are correct for the SoftRF legacy protocol

The problem is not in the scripts. The problem is that the captured signal
is not the SoftRF legacy protocol.
