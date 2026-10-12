# SoftRF Legacy Protocol — Reverse-Engineering Notes

> Authoritative source: SoftRF firmware @ commit `973A8D73` (branch master),
> repo `https://github.com/lyusupov/SoftRF`.
>
> Files consulted:
> - `software/firmware/source/SoftRF/src/protocol/radio/Legacy.cpp` (decode/encode, btea, key)
> - `software/firmware/source/SoftRF/src/protocol/radio/Legacy.h` (packet struct, syncword, keys, CRC)
> - `software/firmware/source/SoftRF/src/driver/radio/radiolib.cpp` (RX path: CRC, Manchester decode)
> - `software/firmware/source/libraries/CRC/lib_crc.cpp` (update_crc_ccitt)
> - `software/firmware/source/libraries/OGN/manchester.h` (ManchesterDecode table)
>
> This file is the **single source of truth** for the decoder. Anything not
> written here must be verified against the firmware before use.

---

## 1. Air Interface

| Parameter | Value |
|-----------|-------|
| Modulation | 2-FSK (GFSK), 915 MHz |
| Bit rate (raw) | 100 kbps |
| Deviation | 50 kHz |
| Whitening | **Manchester** (each 1 data-bit → 2 symbols) |
| Symbol rate | 200 ksym/s |
| Preamble | `0x55` × 1 (`RF_PREAMBLE_TYPE_55`) |
| Syncword (air) | `55 99 A5 A9 55 66 65 96` (8 bytes) |
| Payload size | **24 bytes** (after syncword) |
| CRC | **CCITT-F (poly 0x1021, init 0xFFFF)**, 2 bytes |
| Bit inversion | **NO** (only for `RF_WHITENING_NONE`/`NICERF`, not Manchester) |

## 2. RX Decode Order (radiolib.cpp:1320-1475)

```
Air → FM demod → Manchester decode → [no inversion for Manchester]
    → CRC-CCITT over payload → success
```

**CRITICAL**: The inversion step (`payload_type == RF_PAYLOAD_INVERTED ? ~val : val`)
only happens in the `RF_WHITENING_NONE`/`RF_WHITENING_NICERF` path. For the
**Legacy protocol (Manchester)**, there is **NO bit inversion**.

## 3. CRC (lib_crc.cpp:183-204)

```c
crc = 0xFFFF;                        // seed (CCITT_FFFF)
crc = update_crc_ccitt(crc, 0x31);  // pre-seed (NRF905/FLARM address)
crc = update_crc_ccitt(crc, 0xFA);
crc = update_crc_ccitt(crc, 0xB6);
// ... then over payload bytes (all but last 2)
crc = update_crc_ccitt(crc, payload[i]);
```

```c
unsigned short update_crc_ccitt(unsigned short crc, char c) {
  tmp = (crc >> 8) ^ (0xFF & c);
  crc = (crc << 8) ^ crc_tabccitt[tmp];
  return crc;
}
```

**CRC covers**: the `size - 4` bytes of the Manchester-decoded buffer (i.e., the
raw payload minus the last 2 CRC bytes).

## 4. Packet Structure (legacy_v6_packet_t, Legacy.h:145-195)

```c
typedef struct {
  // Word 0: 4 bytes (NOT encrypted)
  unsigned int addr:24;
  unsigned int type:4;          // 0 = Air V6 position
  unsigned int addr_type:3;
  unsigned int _unk1:1;
  // Words 1-5: 20 bytes (encrypted with btea, 5 words)
  int vs:10; unsigned int _unk2:2;
  unsigned int airborne:1; unsigned int stealth:1;
  unsigned int no_track:1; unsigned int parity:1;
  unsigned int gps:12; unsigned int aircraft_type:4;
  unsigned int lat:19; unsigned int alt:13;
  unsigned int lon:20; unsigned int _unk3:10; unsigned int smult:2;
  int8_t ns[4];
  int8_t ew[4];
} __attribute__((packed)) legacy_v6_packet_t;   // 24 bytes total
```

**Layout** (little-endian ARM):
- Bytes 0-3: Word 0 = `addr` (24 bits, LSB) + `type` (4 bits, MSB of byte 3)
  - `addr` = 24-bit LSB (bytes 0,1,2 + low 4 bits of byte 3)
  - `type` = high 4 bits of byte 3 (bits 4-7)
- Bytes 4-23: Words 1-5 (XXTEA-encrypted)

## 5. XXTEA Encryption (btea, Legacy.cpp:90-140)

```c
#define DELTA 0x9e3779b9
#define ROUNDS 6    // 6 rounds, NOT 32
#define MX (((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4)) ^ ((sum ^ y) + (key[(p & 3) ^ e] ^ z)))

// encrypt:  btea((uint32_t*)pkt + 1, +5, key);   // 5 words at offset 1
// decrypt:  btea((uint32_t*)pkt + 1, -5, key);   // 5 words at offset 1
```

**Key** (make_v6_key, Legacy.cpp:141-150):
```c
static const uint32_t table[12] = LEGACY_KEY1;   // 8 words

void make_v6_key(uint32_t key[4], uint32_t timestamp, uint32_t address) {
  for (i = 0; i < 4; i++) {
    ndx = ((timestamp >> 23) & 1) ? i+4 : i;
    key[i] = obscure(table[ndx] ^ ((timestamp >> 6) ^ address), LEGACY_KEY2) ^ LEGACY_KEY3;
  }
}

long obscure(uint32_t key, uint32_t seed) {
  uint32_t m1 = seed * (key ^ (key >> 16));
  uint32_t m2 = (seed * (m1 ^ (m1 >> 16)));
  return m2 ^ (m2 >> 16);
}
```

**Address** for key derivation: `(pkt->addr << 8) & 0xffffff` — the 24-bit addr
shifted left by 8 (i.e., `addr * 256`) masked to 24 bits.

**Timestamp**: `(uint32_t) this_aircraft->timestamp` — Unix epoch seconds.

## 6. Manchester Encoding (OGN manchester.h)

TX (encode, 1 bit → 2 symbols):
```c
0x01  0x02  0x04  0x08  0x10  0x20  0x40  0x80
0x01  0x02  0x04  0x08  0x10  0x20  0x40  0x80
0x80  0x40  0x20  0x10  0x08  0x04  0x02  0x01
0x80  0x40  0x20  0x10  0x08  0x04  0x02  0x01
```

RX (decode, 2 symbols → 1 bit):
```c
00, 01, 01, 02, 01, 02, 02, 03,
01, 02, 02, 03, 02, 03, 03, 04,
01, 02, 02, 03, 02, 03, 03, 04,
02, 03, 03, 04, 03, 04, 04, 05,
01, 02, 02, 03, 02, 03, 03, 04,
02, 03, 03, 04, 03, 04, 04, 05,
02, 03, 03, 04, 03, 04, 04, 05,
03, 04, 04, 05, 04, 05, 05, 06
```

The radio reads 2 bytes per data byte:
- byte 1 → `val1 = ManchesterDecode[byte1]` (4-bit value, top nibble)
- byte 2 → `val2 = ManchesterDecode[byte2]` (4-bit value, bottom nibble)
- `data = (val1 << 4) | val2`

**To decode the air stream**: each 2 raw bits → 1 symbol (0 or 1), group into
16 symbols per byte, look up the 2-byte pair in the decode table.

## 7. Complete RX Decode Pipeline (authoritative)

```
1. FM demodulate 2-FSK (915 MHz, 100 kbps, 50 kHz dev)
2. Manchester decode (16 symbols/byte → 1 data byte)
3. [NO inversion for Manchester]
4. Find syncword: 55 99 A5 A9 55 66 65 96
5. Extract 24-byte payload after syncword
6. CRC-CCITT:
   - crc = 0xFFFF
   - crc = update(crc, 0x31); update(crc, 0xFA); update(crc, 0xB6)
   - crc = update(crc, payload[i]) for i in 0..21 (22 bytes)
   - Compare: payload[22] == crc>>8, payload[23] == crc&0xFF
7. If CRC OK:
   - addr = (payload[0] | payload[1]<<8 | payload[2]<<16) & 0xFFFFFF
   - type = (payload[3] >> 4) & 0x0F
   - If type != 0: not Air V6 position
   - btea((uint32_t*)payload + 1, -5, key)   // decrypt 5 words at offset 1
   - Verify parity
   - Extract lat/lon/alt/speed/course from words 1-5
```

## 8. Known Correct Constants

| Constant | Value |
|----------|-------|
| `LEGACY_SYNCWORD` | `55 99 A5 A9 55 66 65 96` |
| `LEGACY_PAYLOAD_SIZE` | 24 |
| `LEGACY_KEY1` | `0xe43276df 0xdca83759 0x9802b8ac 0x4675a56b 0xfc78ea65 0x804b90ea 0xb76542cd 0x329dfa32` |
| `LEGACY_KEY2` | `0x045d9f3b` |
| `LEGACY_KEY3` | `0x87b562f4` |
| `LEGACY_KEY4` | `0x956F6C77` |
| `LEGACY_KEY5` | `0xA5F9B21C 0xAB3F9D12 0xC6F34E34 0xD72FA378` |
| `DELTA` | `0x9e3779b9` |
| `ROUNDS` | 6 |
| CRC poly | `0x1021` |
| CRC init | `0xFFFF` |
| CRC pre-seed | `0x31 0xFA 0xB6` |

## 9. Open Questions / TODO

- [ ] Confirm exact bit ordering in Manchester decode (MSB-first vs LSB-first)
- [ ] Confirm whether `addr << 8` in key derivation is correct (vs. just `addr`)
- [ ] Test decoder against captured WAV
- [ ] Verify CRC pre-seed interpretation (skip 8-byte syncword + first payload byte)
- [ ] Check if the `LEGACY_PREAMBLE_SIZE = 1` means 1 byte of `0x55` before syncword

---

## 10. Signal Analysis Findings (2026-10-12)

### WAV File Properties
- File: `/home/ubuntu/.openclaw/workspace/baseband_915000000Hz_20-35-24_03-10-2026.wav`
- Sample rate: 20 MS/s (20,000,000 Hz)
- Channels: 2 (I/Q baseband)
- Format: 32-bit float
- Duration: ~5.6 seconds
- Total samples: ~112,328,704 per channel

### Signal Diagnosis
**The captured WAV file does NOT contain the expected ±50 kHz FSK tones.**

Evidence:
1. **FFT analysis**: Dominant DC peak (magnitude 4851.55) with negligible sidebands. No significant energy at ±50 kHz.
2. **Phase derivative histogram**: Peaks at ~2 kHz and ±98 kHz, but NOT at ±50 kHz.
3. **I/Q channel statistics**: Both channels static around (0.02, -0.03) with negligible variance (std ~0.004).
4. **I channel quantization**: Values quantized to 5 discrete levels (0.015625, 0.023438, 0.031250, etc.), suggesting a heavily quantized or improperly conditioned signal.

### Conclusion
The recording appears to be a **static DC offset** or an **improperly conditioned baseband signal**, not a valid time-varying FSK modulated signal. Standard demodulation is impossible on this raw data.

### Failed Demodulation Attempts
1. **Standard FM demodulation**: Produced all-zero bits (no signal variation).
2. **Phase derivative method**: Frequency histogram showed no energy at ±50 kHz.
3. **Direct I/Q thresholding**: I channel quantized to 5 levels; bit pattern regular (100 samples/bit) but not Manchester.
4. **AGC + DC removal**: No improvement; signal remains static.

### Likely Causes
- **Hardware issue**: Capture hardware/software may have logged a static level instead of the modulated signal.
- **DC coupling**: The baseband signal may have been DC-coupled, resulting in a constant offset.
- **Wrong port/interface**: The signal may have been captured on the wrong channel or interface.
- **Gain stage failure**: The AGC or gain stage may have failed, clamping the signal to a fixed level.

### Next Steps (for future sessions)
1. **Recapture the signal** with a known-good SDR setup (RTL-SDR, HackRF, or similar).
2. **Verify the capture chain**: Ensure the SDR is properly configured for 915 MHz, 2-FSK, 50 kHz deviation.
3. **Test with a known transmitter**: Send a test packet from a known aircraft/ADS-B transmitter and verify the decoder works.
4. **Alternative**: Find a known-good reference capture of a SoftRF/ADS-B signal and test the decoder against it.

### Reference
- Skill: `~/.openclaw/agents/fi/agent/workshop-skills/rf-baseband-analysis/SKILL.md`
- Firmware: `/tmp/SoftRF-firmware/` (commit 973A8D73)
- Protocol: 2-FSK 100 kbps, 50 kHz deviation, Manchester, 8-byte syncword, 24-byte payload, CRC16 CCITT-F, XXTEA
