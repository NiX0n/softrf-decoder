# softrf-decoder

Decoder for SoftRF 915 MHz radio protocol (EasyLink-compatible).

## Documentation

- **`NOTES.md`** — full protocol research with verified firmware citations and GitHub links
- **`SYSTEM_FACTS.md`** — verified protocol constants with file/line citations and GitHub links
- **`REVERSE_ENGINEERING_NOTES.md`** — decode path, hypotheses, open questions, GitHub links
- **`prototype/decode.py`** — Python reference implementation

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
| `software/firmware/source/SoftRF/src/driver/radio/nordic.cpp` | nRF905 driver |
| `software/firmware/source/SoftRF/src/driver/radio/nordic.h` | nRF905 register definitions |
| `software/firmware/source/libraries/nRF905/nRF905.h` | nRF905 CRC enum |
| `software/firmware/source/libraries/EasyLink/src/syscfg/ti_easylink_config.c` | CC1101 PHY profiles |
| `software/firmware/source/libraries/EasyLink/src/syscfg/ti_easylink_freqplan.h` | US frequency plan |
| `software/firmware/source/libraries/CRC/lib_crc.cpp` | CRC-16 implementation |

To clone for local analysis:

```bash
git clone https://github.com/lyusupov/SoftRF.git SoftRF-firmware
cd SoftRF-firmware && git checkout 973a8d73
```

## Quick Start (Python prototype)

```bash
cd prototype
pip install numpy scipy
python decode.py --wav /path/to/capture.wav
```

## Status

Research in progress. See `NOTES.md` and `REVERSE_ENGINEERING_NOTES.md` for details.
