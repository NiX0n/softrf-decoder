# Reverse Engineering Notes

This document may contain:

- Discoveries
- Hypotheses
- Open questions
- Experimental results

Content here is not automatically considered fact.
Verified information must be promoted into SYSTEM_FACTS.md.

> **Source repo**: https://github.com/lyusupov/SoftRF (commit `973a8d73`, branch `master`)
>
> All file paths below are relative to the repo root. To view any file on GitHub:
> `https://github.com/lyusupov/SoftRF/blob/master/<path>`
>
> Key files:
> - `software/firmware/source/SoftRF/src/protocol/radio/Legacy.h` — syncword, payload size, CRC type, key definitions
> - `software/firmware/source/SoftRF/src/protocol/radio/Legacy.cpp` — `legacy_proto_desc`, `legacy_encode`/`legacy_decode`, XXTEA, coordinate conversion
> - `software/firmware/source/SoftRF/src/driver/RF.h` — RF constants (modulation, whitening, bit order)
> - `software/firmware/source/SoftRF/src/driver/radio/radiolib_extra.cpp` — CC1101 register setup
> - `software/firmware/source/SoftRF/src/driver/radio/nordic.cpp` — nRF905 driver
> - `software/firmware/source/libraries/EasyLink/src/syscfg/ti_easylink_config.c` — CC1101 PHY profiles
> - `software/firmware/source/libraries/EasyLink/src/syscfg/ti_easylink_freqplan.h` — US frequency plan
> - `software/firmware/source/libraries/CRC/lib_crc.cpp` — CRC-16 implementation
> - `software/firmware/source/libraries/nRF905/nRF905.h` — nRF905 register definitions

---

# Current Open Questions

## Frequency Selection (RESOLVED)

- Region: US 900 MHz (65 channels, 902.2 MHz start, 400 kHz spacing)
- Protocol: `RF_PROTOCOL_LEGACY` (forced)
- Channel: Fixed (no hopping in Legacy)
- Source: `freqplan.h:26-28`, `radiolib_extra.cpp:57`

## Frequency Hopping (RESOLVED — NOT PRESENT)

- No hopping in Legacy protocol
- P3I uses fixed channel per `freqplan.h`
- `nRF905_setFrequency()` called once per channel

## Packet Format (RESOLVED)

- Preamble: 0x55, radio-generated (nRF905: 26×1 + 26×0)
- Syncword: 8 bytes `55 99 A5 A9 55 66 65 96`
- Payload: 24 bytes XXTEA-encrypted, MSB first
- CRC: CCITT-F, poly 0x1021, seed 0xFFFF, pre-seeded with 3 bytes
- Whitening: Manchester (each bit → 2 symbols)
- Inversion: `RF_PAYLOAD_INVERTED` (bits inverted before air)
- Source: `Legacy.cpp`, `Legacy.h`, `radiolib_extra.cpp`

## Validation Targets

- Ground-truth control sample: **NOT YET DECODED**
- Blocker: Manchester whitening + payload inversion not applied in prototype
- Next step: Update `prototype/decode.py` with correct demodulation order

## Unknowns (STILL OPEN)

- **v6key**: 4-byte external key, source unknown
- **TX power**: 10 dBm on nRF905, 0 dBm on CC1101
- **Exact preamble on air**: nRF905 docs say 26×1 + 26×0, but actual RF capture may differ
- **Frame timing**: No inter-frame spacing documented in firmware

---

## Discovery Log

## Initial RF Capture

Capture validated.

Properties:

- Float32 IQ
- 20 MS/s
- ~5.6 seconds
- Observable RF bursts present

Status:

Suitable for decoder development.

## Firmware Source Analysis (2026-10-10)

Full analysis of `~/SoftRF-firmware` (commit 07e5e280, 2026-05-26).

### Key Findings

1. **Manchester whitening** is the root cause of decoding failures.
   Each bit is expanded to 2 symbols via `ManchesterEncode[]` LUT.
   This doubles the symbol rate to 200 kbps.
   Previous prototype used 100 kbps directly — wrong.

2. **Payload inversion** (`RF_PAYLOAD_INVERTED`) means bits are
   inverted before transmission. RX must invert after Manchester decode.

3. **XXTEA key derivation** confirmed: `LEGACY_KEY1[8] ^ LEGACY_KEY2 ^ v6key`.
   `LEGACY_KEY2 = 0x045d9f3b`.
   `v6key` is external (unknown source).

4. **CRC pre-seed** = 3 bytes (`0x31, 0xFA, 0xB6`) to skip syncword
   + first payload byte. CRC is computed over raw (unencrypted) payload.

5. **Coordinate base** = 40.0°N, 40.0°W. Degree × 10^7.

6. **US channel plan**: 65 channels, 902.2 MHz start, 400 kHz spacing.
   Legacy uses fixed channel (no hopping).

7. **nRF905 vs CC1101**: nRF905 adds hardware preamble (26×1+26×0)
   and hardware CRC. CC1101 path uses software preamble and CRC.

### Files Analyzed

| File | Lines | Content |
|------|-------|---------|
| `Legacy.cpp` | 1-225 | Proto desc, key derivation, encode/decode, XXTEA |
| `Legacy.h` | 1-128 | Proto config, ManchesterEncode[], payload struct |
| `radiolib_extra.cpp` | 599-900 | Legacy init, TX/RX, CC1101 setup |
| `radiolib_extra.cpp` | 1500-1570 | Legacy TX/RX with Manchester + CRC |
| `nordic.cpp` | 126-500 | nRF905 setup, TX, RX, bit order |
| `P3I.cpp` | 495-740 | P3I TX (Legacy), RX, CRC, Manchester |
| `freqplan.h` | 1-100 | US channel plan, freq selection |
| `freqplan.cpp` | 1-245 | Channel selection, frequency calc |
| `nRF905.h` | 1-300 | nRF905 API, CRC config, TX power |
| `P3I.h` | 1-200 | P3I protocol desc, proto_desc struct |

### Status

Decoding blocked on: applying correct demodulation order in prototype.
Next: update `prototype/decode.py` with Manchester + inversion support.

---

## Known Protocol Information (VERIFIED)

Legacy:
- 2-FSK (GFSK)
- 100 kbps data rate
- 50 kHz frequency deviation (±50 kHz)
- BT = 0.5 (Gaussian filter)
- Manchester whitening (200 kbps symbol rate on air)
- Payload inversion (MSB first, inverted before air)
- 8-byte syncword: `55 99 A5 A9 55 66 65 96`
- 24-byte XXTEA-encrypted payload
- 2-byte CRC-16 (CCITT-F, poly 0x1021, seed 0xFFFF)
- Preamble: 0x55, radio-generated
- RX bandwidth: SS (125 kHz)
- Coordinate base: 40.0°N, 40.0°W
- US channels: 65, 902.2 MHz start, 400 kHz spacing

Full details with citations: see `NOTES.md` (Section 1)
and `SYSTEM_FACTS.md` (Verified Protocol Facts).

Source: `~/SoftRF-firmware` commit 07e5e280
