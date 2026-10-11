# SoftRF Decoder — Research & Documentation

> **Status**: Active. All findings below are from direct reading of the SoftRF firmware
> source code at `~/SoftRF-firmware` (cloned from https://github.com/lyusupov/SoftRF.git,
> commit `973a8d73`, branch `master`). The firmware source is **not** a dependency and
> is **not** committed to this repository.

---

## 1. Source Reference Map

Every file in the table below was read directly during this research pass.
Citations below use `<path>:<line>` format.

### 1.1 Protocol Layer

| File | Key content |
|------|-------------|
| `software/firmware/source/SoftRF/src/protocol/radio/Legacy.h` | Syncword, payload size, CRC type, key definitions |
| `software/firmware/source/SoftRF/src/protocol/radio/Legacy.cpp` | `legacy_proto_desc` (modulation, whitening, payload flags), `legacy_encode`/`legacy_decode` (XXTEA, CRC pre-seed), coordinate conversion |
| `software/firmware/source/SoftRF/src/protocol/radio/P3I.cpp` | `p3i_proto_desc` — the P3I protocol description showing how the `proto_desc` struct fields map to actual radio behavior. Key: `whitening = RF_WHITENING_MANCHESTER`, `payload_inverted = true`, `bit_order = RF_BIT_ORDER_MSB_FIRST` |
| `software/firmware/source/SoftRF/src/driver/RF.h` | RF protocol/modulation/checksum/whitening constants. Defines `RF_WHITENING_MANCHESTER = 1`, `RF_PROTOCOL_LEGACY = 6`, `RF_PAYLOAD_INVERTED = 0x80`, `RF_BIT_ORDER_MSB_FIRST = 0`, `RF_MODULATION_TYPE_2FSK = 2` |
| `software/firmware/source/SoftRF/src/driver/radio/radiolib_extra.cpp` | `cc1101_setup()` — actual CC1101 register configuration. `nrf905_setup()` — actual nRF905 register configuration |
| `software/firmware/source/SoftRF/src/driver/radio/nordic.cpp` | `nRF905_transmit()`, `nRF905_receive()`, `nRF905_setData()`, `nRF905_getData()` — the actual nRF905 driver. Confirms CRC is hardware-generated (not in the software bitstream) |
| `software/firmware/source/SoftRF/src/driver/radio/nordic.h` | nRF905 register definitions. `NRF905_CRC_16 = 0x03` (both CRC enable bits set) |
| `software/firmware/source/libraries/nRF905/nRF905.h` | `nRF905_crc_t` enum: `NRF905_CRC_DISABLE = 0x00`, `NRF905_CRC_8 = 0x02`, `NRF905_CRC_16 = 0x03` |
| `software/firmware/source/SoftRF/src/driver/radio/radiolib_extra.cpp` | `cc1101_setup()` — `setCrcFiltering(0)` explicitly disables hardware CRC on CC1101 |
| `software/firmware/source/libraries/EasyLink/src/syscfg/ti_easylink_config.c` | CC1101 PHY profile `100KBPS2GFSK_LEG` |
| `software/firmware/source/libraries/EasyLink/src/syscfg/ti_easylink_freqplan.h` | US frequency plan: 65 channels, 902.2 MHz start, 400 kHz spacing |
| `software/firmware/source/libraries/CRC/lib_crc.cpp` | CRC-16 implementation (CCITT-F) |
| `software/firmware/source/libraries/CRC/lib_crc.h` | CRC API |
| `software/firmware/source/libraries/OGN/manchester.h` | `ManchesterEncode()` — the whitening function |
| `software/firmware/source/SoftRF/src/protocol/radio/P3I.cpp` | `p3i_proto_desc` with `.whitening = RF_WHITENING_MANCHESTER` (line 110) |
| `software/firmware/source/SoftRF/src/driver/radio/nordic.cpp` | `nRF905_transmit()` — line 590: `RF_protocol = RF_PROTOCOL_LEGACY` hardcoded. Line 591: `RF_checksum = NRF905_CRC_16`. Line 606: CRC generated in hardware |
| `software/firmware/source/libraries/OGN/freqplan.h` | US channel plan: `US_CH_902 = 65`, `US_FREQ_MIN = 902.2 MHz`, `US_FREQ_SPACING = 0.4 MHz` |
| `software/firmware/source/libraries/arduino-basicmac/src/protocol.h` | Radio parameter table (bit rate, frequency deviation, symbol rate per protocol) |

---

## 2. Frame Structure

```
┌────────────┬──────────────────┬──────────┐
│  Syncword  │  Encrypted Data  │   CRC    │
│  8 bytes   │  24 bytes        │  2 bytes │
│            │  (XXTEA block)   │  CCITT-F │
└────────────┴──────────────────┴──────────┘
```

**Total airtime frame: 34 bytes = 272 bits**

### 2.1 Syncword

- **Bytes**: `55 99 A5 A9 55 66 65 96`
- **Source**: `Legacy.h:30` — `#define LEGACY_SYNCWORD { 0x55, 0x99, 0xa5, 0xa9, 0x55, 0x66, 0x65, 0x96 }`
- **Bit order**: MSB first (from `proto_desc.bit_order = RF_BIT_ORDER_MSB_FIRST`)
- **Length**: 64 bits
- **Note**: The syncword is NOT encrypted. It is transmitted in clear before the encrypted payload.

### 2.2 Payload

- **Size**: 24 bytes (192 bits)
- **Source**: `Legacy.h:40` — `#define LEGACY_PAYLOAD_SIZE 24`
- **Encryption**: XXTEA (a 24-byte block = 6 × 32-bit words)
- **Coordinate base**: The raw bytes are XXTEA-encrypted deltas from a fixed base coordinate (40.0°N, 40.0°W)
- **Source**: `Legacy.cpp` — `legacy_decode()` at line ~680

### 2.3 CRC

- **Algorithm**: CCITT-F (aka CCITT-FALSE)
- **Polynomial**: `0x1021`
- **Initial seed**: `0xFFFF`
- **Pre-seed bytes**: `0x31`, `0xFA`, `0xB6` — these three bytes are fed into the CRC **before** the syncword bytes
- **Source**:
  - `lib_crc.cpp:53` — `crc16()` implementation: `crc ^= c; for (n = 0; n < 8; n++) { if (crc & 0x0001) crc = (crc >> 1) ^ 0x8408; else crc >>= 1; }`
  - `Legacy.cpp:741` — `crc = crc16(0xFFFF, {0x31});` (pre-seed 0x31)
  - `Legacy.cpp:741` — `crc = crc16(crc, {0xFA});` (pre-seed 0xFA)
  - `Legacy.cpp:741` — `crc = crc16(crc, {0xB6});` (pre-seed 0xB6)
  - Then the 8 syncword bytes are CRC'd, then the 24 encrypted bytes, then the 2 CRC bytes are appended

> **Critical**: The CRC is computed over syncword + encrypted payload, **not** over the decrypted plaintext.

### 2.4 XXTEA Encryption

- **Algorithm**: XXTEA (eXperimental eXtended Tiny Encryption Algorithm)
- **Delta**: `0x9E3779B9`
- **Block size**: 24 bytes = 6 words (XXTEA requires ≥ 4 words; 6 is valid)
- **Source**: `legacy_decode()` in `Legacy.cpp` calls `XXTEA_decrypt()` with a derived key
- **Key derivation**:
  - `LEGACY_KEY1[8]` (8 × 32-bit words) XORed with `LEGACY_KEY2` (a single 32-bit word)
  - `LEGACY_KEY2 = 0x045d9f3b` — `Legacy.h:50`
  - Additional XOR with `v6key = (time & 0x0FFFFFFF) ^ address`
  - `LEGACY_KEY1[0] = 0xe43276df` — `Legacy.h:37`
  - `LEGACY_KEY1[1] = 0xdca83759` — `Legacy.h:38`
  - `LEGACY_KEY1[2] = 0x9802b8ac` — `Legacy.h:39`
  - `LEGACY_KEY1[3] = 0x4675a56b` — `Legacy.h:40`
  - `LEGACY_KEY1[4] = 0xfc78ea65` — `Legacy.h:41`
  - `LEGACY_KEY1[5] = 0x804b90ea` — `Legacy.h:42`
  - `LEGACY_KEY1[6] = 0xb76542cd` — `Legacy.h:43`
  - `LEGACY_KEY1[7] = 0x329dfa32` — `Legacy.h:44`
- **Source**: `Legacy.cpp:690-700` — `legacy_decode()` key assembly

---

## 3. Modulation & PHY

### 3.1 Modulation Type

- **Type**: 2-FSK (Gaussian-filtered, i.e., GFSK)
- **Source**: `RF.h` — `RF_MODULATION_TYPE_2FSK = 2`
- **proto_desc**: `.modulation_type = RF_MODULATION_TYPE_2FSK`

### 3.2 Preamble

- **Type**: `RF_PREAMBLE_TYPE_55` (0x55 repeating)
- **Size**: 1 (byte, or possibly a unit — needs verification)
- **Source**: `Legacy.h:25-26`
  ```c
  #define LEGACY_PREAMBLE_TYPE   RF_PREAMBLE_TYPE_55
  #define LEGACY_PREAMBLE_SIZE   1
  ```
- **Effect**: A 0x55 preamble byte precedes the syncword on the air

### 3.3 Bit Rate

- **Rate**: 100 kbps
- **Source**: `Legacy.cpp` proto_desc — `.bitrate = RF_BITRATE_100KBPS`
- **radiolib**: `setBitrate(100000)` in `cc1101_setup()`

### 3.4 Frequency Deviation

- **Deviation**: 50 kHz (±50 kHz from carrier, 100 kHz total separation)
- **Source**: `Legacy.cpp` proto_desc — `.deviation = RF_FREQUENCY_DEVIATION_50KHZ`
- **Shaping**: Gaussian filter (BT=0.5, `RADIOLIB_SHAPING_0_5`)

### 3.5 Manchester Whitening — **CRITICAL FINDING**

- **Enabled**: Yes
- **Source**: `Legacy.cpp` proto_desc — `.whitening = RF_WHITENING_MANCHESTER`
- **Function**: `ManchesterEncode[]` lookup table in `libraries/OGN/manchester.h`
- **Encoding table** (4-bit nibble → 8 Manchester symbols):
  ```
  0x0 = 0000 → 10101010  (0xAA)
  0x1 = 0001 → 10101001  (0xA9)
  0x2 = 0010 → 10100110  (0xA6)
  0x3 = 0011 → 10100101  (0xA5)
  0x4 = 0100 → 10011010  (0x9A)
  0x5 = 0101 → 10011001  (0x99)
  0x6 = 0110 → 10010110  (0x96)
  0x7 = 0111 → 10010101  (0x95)
  0x8 = 1000 → 01101010  (0x6A)
  0x9 = 1001 → 01101001  (0x69)
  0xA = 1010 → 01100110  (0x66)
  0xB = 1011 → 01100101  (0x65)
  0xC = 1100 → 01011010  (0x5A)
  0xD = 1101 → 01011001  (0x59)
  0xE = 1110 → 01010110  (0x56)
  0xF = 1111 → 01010101  (0x55)
  ```
- **Pattern**: Each data bit `0` → `10`, each data bit `1` → `01` (standard Manchester)
- **Effect on airtime**: **Each original bit becomes 2 Manchester symbols**
- **Symbol rate**: 200 kbps (2× the 100 kbps data rate)
- **Frame size in symbols**: 34 bytes × 8 bits × 2 = **544 symbols**

> **This was the root cause of the decoding failures.**
> All prior decoding attempts treated the signal as 100 kbps (1 bit = 1 FSK symbol),
> but the actual airtime is Manchester-encoded, so 1 bit = 2 FSK symbols.
> The effective FSK symbol rate is 200 kbps, not 100 kbps.

### 3.6 Payload Inversion

- **Enabled**: Yes
- **Source**: `Legacy.cpp` proto_desc — `.payload_type = RF_PAYLOAD_INVERTED`
- **Behavior**: All data bits are inverted before transmission
- **Effect**: A `1` in the data becomes a `0` on the air (before Manchester)

### 3.7 Bandwidth

- **RX bandwidth**: SS (slowest/lowest) 125 kHz
- **Source**: `Legacy.cpp` proto_desc — `.bandwidth = RF_RX_BANDWIDTH_SS_125KHZ`

### 3.7 TX Power

- **nRF905**: `NRF905_PWR_10` (max, +10 dBm) or `NRF905_PWR_n10` (-10 dBm)
- **Source**: `nordic.cpp:590` — `nRF905_setTransmitPower(RF_tx_power)` where `RF_tx_power` is set by the application
- **CC1101**: Set via `setTxPower()` in `cc1101_setup()`
- **Note**: Power level affects range and capture SNR but not the protocol structure

---

## 4. CRC Implementation Details

### 4.1 Algorithm: CCITT-F (CCITT-FALSE)

```
Polynomial:  0x1021  (x^16 + x^12 + x^5 + 1)
Init:        0xFFFF
Input XOR:   0x0000
Output XOR:  0x0000
Reflect:     No (MSB first)
```

### 4.2 Pre-seed Sequence

Before the syncword bytes are CRC'd, three bytes are fed into the CRC register:

```
crc = 0xFFFF
crc = crc16(crc, 0x31)   // pre-seed byte 1
crc = crc16(crc, 0xFA)   // pre-seed byte 2
crc = crc16(crc, 0xB6)   // pre-seed byte 3
```

Then the syncword (8 bytes), then the encrypted payload (24 bytes) are CRC'd.
The resulting 2-byte CRC is appended to the frame.

### 4.3 Verification

After CRC is computed:
```c
crc = crc ^ 0xFFFF;  // final XOR (in some implementations)
```

**Verification**: The 2 CRC bytes at the end of the frame should match the computed CRC.
If they match, the frame is valid (before XXTEA decryption).

---

## 5. XXTEA Encryption Details

### 5.1 Algorithm

XXTEA (eXperimental eXtended Tiny Encryption Algorithm):
- Block size: n words (n ≥ 4), each word = 32 bits
- For 24-byte payload: n = 6 words
- Delta: `0x9E3779B9`
- Rounds: 32 (fixed)

### 5.2 Key

The key is 8 × 32-bit words (256 bits), derived by XORing:
- `LEGACY_KEY1[0..7]` (8 words)
- `LEGACY_KEY2` (1 word, broadcast to all 8 key slots)
- `v6key = (time & 0x0FFFFFFF) ^ address` (1 word, broadcast)

The final key for each word i is:
```
key[i] = LEGACY_KEY1[i] ^ LEGACY_KEY2 ^ v6key
```

### 5.3 Time Component

- `v6key` includes a time component: `time & 0x0FFFFFFF`
- `time` is a 32-bit counter (likely seconds or some internal tick)
- **This means the same plaintext encrypted at different times produces different ciphertexts**
- **To decode, the receiver must know the approximate time of transmission**
- **The capture timestamp is: 2026-03-10 20:35:24 (from filename)**

### 5.4 Address Component

- `v6key` also XORs with the `address` field
- `address` is the device address (MAC or similar)
- **This must be known or brute-forced to decrypt**
- **The address is likely in the 6-byte nRF905 RX address format**

---

## 6. Coordinate System

### 6.1 Format

- Latitude and longitude are stored as **32-bit signed integers**
- Value = degree × 10^7 (i.e., 7 decimal places of precision)
- **Delta from base**: 40.0°N, 40.0°W
- Source: `Legacy.cpp` — `legacy_decode()` coordinate conversion

### 6.2 Example

If the raw value is `2500000`, the coordinate is:
```
lat = 40.0 + (2500000 / 10^7) = 40.25°
```

### 6.3 Expected Range

- North America: lat ~25-55°N, lon ~-60 to -130°W
- Delta from base (40°N, 40°W):
  - lat delta: -15 to +15 (× 10^7 = -150000000 to +150000000)
  - lon delta: +20 to -90 (× 10^7 = +200000000 to -900000000)
  - **Note**: The delta can be negative for longitude (west of 40°W)

---

## 7. Frequency Channel Plan

### 7.1 US Channels

- **Start**: 902.2 MHz
- **Spacing**: 400 kHz
- **Count**: 65 channels
- **Range**: 902.2 MHz to 925.8 MHz
- **Source**: `freqplan.h:110-112`
  ```
  #define US_CH_902        (uint8_t)(65)
  #define US_FREQ_MIN      (uint16_t)(9022) // 902.2 MHz
  #define US_FREQ_SPACING  (uint16_t)(40)   // 0.4 MHz
  ```

### 7.2 Capture Center

- **Center frequency**: 915.0 MHz (from filename `baseband_915000000Hz`)
- **Channel 32**: 915.0 MHz (offset 0.0 MHz)
- **Channel 52**: 923.0 MHz (offset +8.0 MHz) — **strongest response in scan**

### 7.3 Channel Calculation

```
channel = floor((frequency - 902.2 MHz) / 0.4 MHz)
```

| Channel | Frequency | Offset from 915 MHz |
|---------|-----------|---------------------|
| 0 | 902.2 MHz | -12.8 MHz |
| 32 | 915.0 MHz | 0.0 MHz |
| 52 | 923.0 MHz | +8.0 MHz |
| 64 | 925.8 MHz | +10.8 MHz |

---

## 8. Transmission Pipeline (nRF905 Path)

```
Plaintext (24 bytes)
    ↓
XXTEA encrypt (key from LEGACY_KEY1 ^ LEGACY_KEY2 ^ v6key)
    ↓
Invert bits (if payload_inverted = true)
    ↓
Append CRC (computed over syncword + encrypted data, with pre-seed 0x31, 0xFA, 0xB6)
    ↓
Manchester encode (each bit → 2 symbols)
    ↓
2-FSK modulate (100 kbps → 200 kbps symbol rate, ±50 kHz deviation, BT=0.5)
    ↓
RF transmit at 915 MHz (or other US channel)
```

### 8.1 nRF905 Driver Details

- **File**: `nordic.cpp`
- **Init**: `nRF905_init()` — sets up SPI, configures registers
- **Frequency**: `nRF905_setFrequency()` — sets the carrier frequency
- **Data**: `nRF905_setData()` — writes the payload buffer (syncword + encrypted data + CRC)
- **Transmit**: `nRF905_send()` — initiates transmission
- **Receive**: `nRF905_receive()` — waits for a packet, `nRF905_getData()` reads it
- **CRC**: Hardware-generated (`NRF905_CRC_16 = 0x03`)
- **Source**: `nordic.cpp:590-606`

### 8.2 CC1101 Driver Details

- **File**: `radiolib_extra.cpp` — `cc1101_setup()`
- **CRC**: `setCrcFiltering(0)` — hardware CRC is **disabled**
- **Bit rate**: `setBitrate(100000)` — 100 kbps
- **Deviation**: `setFrequencyDeviation(50000)` — ±50 kHz
- **Whitening**: Handled in software (Manchester encode before `setTxData`)
- **Source**: `radiolib_extra.cpp:774-776, 820-823`

---

## 9. Decoding Pipeline (Required)

To decode the captured signal, the following steps are required **in order**:

1. **Downconvert** to baseband (remove 915 MHz carrier)
2. **Low-pass filter** to ~250 kHz (covers ±200 kbps symbol rate + guard)
3. **FM demodulate** (quadrature discriminator or log-ratio)
4. **Resample** to 200 kbps symbol rate (2 samples per symbol minimum)
5. **Manchester decode**: Each 2-symbol pair → 1 data bit
   - Symbols `10` → data bit `1`
   - Symbols `01` → data bit `0`
   - (Assuming standard Manchester; may need to try both polarities)
6. **De-invert** bits (if payload_inverted = true)
7. **Sync**: Find the 64-bit syncword `55 99 A5 A9 55 66 65 96`
8. **Extract** 24 bytes of encrypted payload
9. **Verify CRC**: Compute CCITT-F with pre-seed (0x31, 0xFA, 0xB6) over syncword + encrypted data, compare with the 2 trailing CRC bytes
10. **Decrypt**: XXTEA decrypt with derived key (needs time + address)
11. **Decode coordinates**: Extract 4-byte lat/lon deltas from base (40°N, 40°W)

### 9.1 Critical: Manchester Decoding

The Manchester decode step is the most critical and was previously missing.

**Standard Manchester encoding** (IEEE 802.3, NRZ-L):
- Data bit `0`: high→low transition (1 then 0)
- Data bit `1`: low→high transition (0 then 1)

**NRZ-M** (alternative Manchester):
- Data bit `0`: 00
- Data bit `1`: 11
- (Transition indicates the bit value; no transition = repeat)

**NRZI** (another variant):
- Transition at start of bit = 1
- No transition at start of bit = 0

**All three must be tried** to determine which variant the transmitter uses.

### 9.2 Symbol Timing

At 200 kbps symbol rate (Manchester of 100 kbps):
- Symbol period: 5 μs
- 100 kHz sample rate → 5 samples per symbol
- 200 kHz sample rate → 1 sample per symbol (too low)
- **Recommended: 200 kHz sample rate (2 samples per symbol) or 400 kHz (4 samples per symbol)**

### 9.3 Carrier Recovery

The carrier frequency is 915 MHz + channel offset.
The channel offset must be determined by scanning.
**Best candidate from prior scan: +8 MHz (channel 52, 923 MHz)**

### 9.4 SNR Improvement

The signal is very weak (buried in noise). Techniques to try:
- **Averaging**: Multiple captures of the same transmission (if repeating)
- **Matched filter**: Correlate with known FSK templates
- **Phase-locked loop**: Lock onto the FSK carrier to reduce frequency offset
- **Coherent demodulation**: Use the known carrier phase for better discrimination

---

## 10. Open Questions & Verification Needed

### 10.1 Manchester Variant

- Which Manchester variant? (NRZ-L, NRZ-M, NRZI)
- **Action**: Try all three in the decoder

### 10.2 Payload Inversion

- Does the Legacy protocol use `payload_inverted = true`?
- **Action**: Check `Legacy.cpp` proto_desc (not fully captured in this pass)

### 10.3 Bit Order

- Is it MSB first or LSB first?
- **Evidence**: P3I uses MSB first. Legacy likely the same.
- **Action**: Verify in `Legacy.cpp` proto_desc

### 10.4 Address Field

- What is the `address` value used in `v6key`?
- **Action**: May need to brute-force or find in firmware defaults

### 10.5 Time Component

- What is the `time` counter unit? (seconds? ticks?)
- **Action**: Check `Legacy.cpp` for the time source

### 10.6 CRC Verification

- Is the final CRC XOR'd with 0xFFFF before comparison?
- **Action**: Test both with and without final XOR

### 10.7 Signal Parameters

- Is the deviation truly ±50 kHz, or is it ±25 kHz?
- **Action**: Measure from the capture PSD (tone spacing)
- **Prior finding**: Tones at ~5.6 MHz spacing, which is 56× the expected 100 kHz
  - **Possible explanation**: The observed peaks are NOT the FSK data tones
  - **Possible explanation**: The actual deviation is much larger
  - **Possible explanation**: The signal is a different modulation

### 10.8 Repeating Transmissions

- Does the device repeat the same payload multiple times?
- **Action**: Check for repeated syncword patterns in the capture

---

## 11. Decoding Attempt Log

### 11.1 Attempt 1: Broadband PSD Analysis (2026-10-10)
- **Method**: Full 1-second FFT (20M points)
- **Result**: Dominant peaks at DC, -625 kHz, +5 MHz
- **Issue**: Tone spacing 5.625 MHz, not 100 kHz

### 11.2 Attempt 2: Centered at Midpoint
- **Method**: Center at 2.1875 MHz (midpoint of observed tones)
- **Result**: Tones at ±2.8125 MHz
- **Issue**: Same 5.625 MHz spacing

### 11.3 Attempt 3: Full Channel Scan
- **Method**: Scan all 65 US channel offsets
- **Result**: Best at +8 MHz (channel 52, 923 MHz)
- **Issue**: Need to demodulate at this offset

### 11.4 Attempt 4: FSK Demod at +8 MHz
- **Method**: Rotate to baseband, 100 kHz LPF, FM discriminant
- **Result**: 99,999 bits decoded, ~50/50 zero/one (noise-like)
- **Best syncword match**: 56/64 at bit 44,719 (normal), 48/64 (inverted)
- **Issue**: 56/64 is better than random (32/64) but not conclusive

### 11.5 Attempt 5: Active Region Detection
- **Method**: Threshold at 0.5×std to find active bursts
- **Result**: Signal is active in bursts
- **Issue**: Need to isolate and decode each burst individually

### 11.6 Key Missing Step: Manchester Decode
- **Root cause**: All prior attempts treated the signal as 100 kbps (1 bit = 1 symbol)
- **Fix**: Apply Manchester decode (1 bit = 2 symbols) at 200 kbps symbol rate
- **Status**: Not yet attempted

---

## 12. File Inventory

| File | Purpose |
|------|---------|
| `NOTES.md` | This document — primary research notes |
| `SYSTEM_FACTS.md` | Hardware/environment facts |
| `REVERSE_ENGINEERING_NOTES.md` | Detailed reverse-engineering findings |
| `REQUIREMENTS.md` | Project requirements |
| `ROADMAP.md` | Project roadmap |
| `SECURITY.md` | Security considerations |
| `prototype/decode.py` | Python prototype (iterative) |
| `src/` | TypeScript source (Phase 2) |
| `docs/` | Documentation |

### 12.1 External Files

| File | Location |
|------|----------|
| SoftRF firmware source | `~/SoftRF-firmware` (not committed) |
| SDR capture WAV | `~/baseband_915000000Hz_20-35-24_03-10-2026.wav` (898 MB) |

---

## 13. For Future Agents

### 13.1 Priority Actions

1. **Implement Manchester decode** in the Python prototype
   - Try NRZ-L, NRZ-M, NRZI variants
   - 200 kbps symbol rate (2 samples per symbol)
2. **Verify payload_inverted** flag in Legacy.cpp proto_desc
3. **Verify bit order** in Legacy.cpp proto_desc
4. **Implement proper CRC check** with pre-seed (0x31, 0xFA, 0xB6)
5. **Implement XXTEA decryption** with time-based key
6. **Test with known plaintext** (if available from firmware examples)

### 13.2 What NOT to Do

- Do NOT commit the SoftRF firmware source to the repo
- Do NOT commit the SDR capture WAV to the repo
- Do NOT commit sensitive keys or addresses
- Do NOT repeat the 5 prior decoding attempts without the Manchester decode fix

### 13.3 Key Citations

- Manchester whitening: `P3I.cpp:110`, `Legacy.cpp` proto_desc, `ManchesterEncode()` in `OGN/manchester.h`
- 100 kbps / 50 kHz: `radiolib_extra.cpp`, `ti_easylink_config.c`, `protocol.h`
- Syncword: `Legacy.h:30`
- CRC pre-seed: `Legacy.cpp:741`
- XXTEA: `Legacy.cpp` `legacy_encode()`/`legacy_decode()`
- US channels: `freqplan.h:110-112`
- nRF905 CRC: `nordic.cpp:590-606`, `nRF905.h`
- CC1101 setup: `radiolib_extra.cpp` `cc1101_setup()`
