# SoftRF Decoder Project Notes

## Overview
Decoding SoftRF Legacy telemetry from SDR capture.

## Source References

All protocol facts below are derived from the SoftRF firmware source code.
Cloned locally for analysis at `~/SoftRF-firmware` (outside the decoder repo).

Firmware repo: `https://github.com/lyusupov/SoftRF.git`

| File | What it defines |
|------|----------------|
| `software/firmware/source/SoftRF/src/protocol/radio/Legacy.cpp` | Protocol constants: syncword, payload size, XXTEA keys, coordinate base |
| `software/firmware/source/SoftRF/src/protocol/radio/Legacy.h` | Protocol header: frame structure, CRC seed, key definitions |
| `software/firmware/source/SoftRF/src/driver/radio/radiolib_extra.cpp` | PHY setup: 2-FSK 100 kbps, 50 kHz deviation, GFSK filter |
| `software/firmware/source/libraries/CRC/lib_crc.cpp` | CRC implementation: CCITT-F poly 0x1021, seed 0xFFFF |
| `software/firmware/source/libraries/CRC/lib_crc.h` | CRC API definitions |
| `software/firmware/source/libraries/EasyLink/src/syscfg/ti_easylink_config.c` | PHY profile: `100KBPS2GFSK_LEG` |
| `software/firmware/source/libraries/EasyLink/src/syscfg/ti_easylink_freqplan.h` | US channel plan: 65 channels, 902.2 MHz start, 400 kHz spacing |

## Protocol (from firmware source)

- **Modulation**: 2-FSK (GFSK), 100 kbps bit rate, 50 kHz frequency deviation
  - Source: `radiolib_extra.cpp`, EasyLink PHY profile `100KBPS2GFSK_LEG`
  - FSK tones at carrier ±25 kHz
- **Channel Plan (US)**: 65 channels, 902.2 MHz + N×400 kHz
  - Source: `ti_easylink_freqplan.h`
  - Capture center 915.0 MHz = Channel 32 (915.0 MHz), offset 0.0 MHz
- **Manchester whitening**: Applied before FSK modulation
  - Source: `Legacy.cpp` TX pipeline
- **Syncword**: `55 99 A5 A9 55 66 65 96` (8 bytes, 64 bits, MSB first)
  - Source: `Legacy.cpp` `LEGACY_SYNCWORD`
- **Frame structure**: 8-byte sync + 24-byte encrypted payload + 2-byte CRC = 34 bytes total
  - Source: `Legacy.cpp` `LEGACY_PAYLOAD_SIZE = 24`, `LEGACY_CRC_SIZE = 2`
- **CRC**: CCITT-F (poly `0x1021`, seed `0xFFFF`)
  - Pre-seeded with bytes `0x31`, `0xFA`, `0xB6` before processing frame data
  - Source: `lib_crc.cpp` + `Legacy.cpp` CRC init sequence
- **Encryption**: XXTEA (delta `0x9E3779B9`)
  - Key derivation: XOR of `LEGACY_KEY1[0..7]` ^ `LEGACY_KEY2` ^ `LEGACY_KEY3` ^ `LEGACY_KEY4` ^ `LEGACY_KEY5` ^ `v6key`
  - `v6key = (time & 0x0FFFFFFF) ^ address`
  - Source: `Legacy.cpp` key assembly + `XXTEA.cpp` (in SoftRF libraries)
  - `LEGACY_KEY1 = {0xe43276df, 0xdca83759, 0x9802b8ac, 0x4675a56b, 0xfc78ea65, 0x804b90ea, 0xb76542cd, 0x329dfa32}`
  - `LEGACY_KEY2 = 0x045d9f3b`
  - Other keys in `Legacy.h`
- **Coordinates**: 4-byte signed integers = (degree × 10^7), delta from base 40.0°N / 40.0°W
  - Source: `Legacy.cpp` coordinate conversion

## Capture File
- File: `~/baseband_915000000Hz_20-35-24_03-10-2026.wav`
- Size: 898 MB
- Format: IEEE float32 stereo WAV (I/Q), 20 MHz sample rate, ~1.4 sec
- Date encoded in filename: 03-10-2026, time 20:35:24
- Center frequency: 915.0 MHz (from filename)
- Ground station: North America (exact location is blind test — user has ground truth)
- Total samples: ~112M (5.62 sec at 20 MHz)

## Decoding Attempts (2026-10-10)

### Attempt 1: Broadband PSD Analysis
- Full 1-second FFT, 20M points
- Dominant peaks: DC (~111 dB), -625 kHz, +5 MHz
- Interpretation: DC is offset artifact; -625 kHz and +5 MHz are likely the two FSK tones
- Tone spacing: 5.625 MHz (NOT ±25 kHz as expected from firmware)
- **Issue**: 5.6 MHz spacing is 112× the expected 50 kHz deviation

### Attempt 2: Centered at 2.1875 MHz (midpoint)
- FSK tones appeared at ±2.8125 MHz from center
- Same 5.625 MHz spacing
- **Issue**: Same discrepancy — tones are 56× the expected 50 kHz spacing

### Attempt 3: Channel Scan (all 65 US channels)
- Scanned all channel offsets from -12.8 to +12.8 MHz
- Best: Channel 52 (+8 MHz, carrier 923 MHz) at 52.0 dB
- Also strong at +8.07 MHz and +7.97 MHz
- **Issue**: +8 MHz offset is not a valid US channel in the 902.2+N×0.4 grid
  - 923.0 MHz = 902.2 + 52×0.4 = 923.0 ✓ (actually IS channel 52)

### Attempt 4: FSK Demod at +8 MHz Offset
- Rotate to baseband, 100 kHz low-pass, FM discriminant
- Demodulated: mean=-117.8 Hz, std=128,311 Hz
- 99,999 bits decoded: 50,430 zeros, 49,569 ones (~50/50 — looks like noise)
- Best syncword match (normal): 56/64 at bit 44,719
- Best syncword match (inverted): 48/64 at bit 45,751
- **Issue**: 56/64 is better than random (expected ~32/64) but not conclusive

### Attempt 5: Active Region Detection
- Threshold at 0.5×std: signal is active in bursts
- Need to isolate transmission bursts and decode each individually

## Key Issues & Open Questions

1. **Tone spacing discrepancy**: Firmware says 50 kHz deviation, but observed tones are ~5.6 MHz apart. Possible explanations:
   - The observed peaks are NOT the FSK data tones (they could be interference or the SDR's internal oscillator)
   - The firmware spec is for a different modulation mode
   - The actual deviation is much larger than documented
   - The signal is not 2-FSK but something else (e.g., MSK, GFSK with wider deviation)

2. **Very low SNR**: Signal is barely above noise floor. All attempts show ~50/50 bit distribution, consistent with decoding noise.

3. **DC offset**: Strong DC component in the capture. May need high-pass filtering before demod.

4. **Carrier frequency uncertainty**: The capture center is 915 MHz, but the actual signal could be at any of the 65 US channel offsets. The strongest response was at +8 MHz (channel 52, 923 MHz).

5. **Manchester whitening**: Not yet confirmed in the demodulated signal. If present, it would produce a characteristic spectral shape.

## Next Steps

- [ ] Try demod at multiple channel offsets and compare
- [ ] Apply high-pass filter to remove DC before FM demod
- [ ] Try different deviation values (25 kHz, 50 kHz, 100 kHz, 200 kHz) in the FM demod threshold
- [ ] Implement proper GFSK demodulator (Gaussian filter + FM discriminant)
- [ ] Try Manchester decode after FSK demod
- [ ] Implement Viterbi decoder for soft-decision FSK
- [ ] Implement proper CRC check (CCITT-F with pre-seed) to validate decoded frames
- [ ] Implement XXTEA decryption with time-based key
- [ ] Compare decoded coordinates with ground truth (blind test)

## Prototype Files
- `prototype/decode.py` — Main Python prototype (iterative)
- `prototype/` — Working directory for signal processing experiments

## For Future Agents / Takeover

1. **Start here**: Read this file + `REVERSE_ENGINEERING_NOTES.md` + `SYSTEM_FACTS.md`
2. **Firmware source**: At `~/SoftRF-firmware` (outside the decoder repo). Key files listed above.
3. **Capture file**: `~/baseband_915000000Hz_20-35-24_03-10-2026.wav` (898 MB)
4. **Current blocker**: Cannot reliably detect the FSK signal in the noisy capture. Best syncword match is 56/64 bits.
5. **What works**: The Python pipeline (load WAV → rotate → filter → FM demod → bit sample) is functional. It just needs the right parameters.
6. **What's been tried**: All 5 attempts above. Don't repeat them without changing the approach.
7. **Blind test**: The decoded coordinates should be in North America. User knows the ground truth.
