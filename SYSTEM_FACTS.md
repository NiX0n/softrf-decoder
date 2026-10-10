# System Facts

This document contains verified facts only.

Speculation belongs in REVERSE_ENGINEERING_NOTES.md.

---

# Sources of Truth

Priority order:

1. SoftRF firmware source
2. Ground-truth RF captures
3. This document
4. Specifications
5. Architecture documents

If conflicts occur:

Firmware source wins.

Observed RF evidence wins over assumptions.

---

# Firmware

Repository:

https://github.com/lyusupov/SoftRF

Purpose:

Authoritative source for:

- Protocol behavior
- Packet formats
- Modulation settings
- CRC implementation
- Frequency selection
- Hopping implementation

---

# Ground Truth Capture

File:

baseband_915000000Hz_20-35-24_03-10-2026.wav

Properties:

- Float32 IQ
- Complex I/Q
- 20 MS/s
- Approximately 5.6 seconds duration
- Contains observable RF bursts

Notes:

Capture contains sensitive location data.

Must never be committed to source control.

---

# Verified Protocol Facts

Current verified facts:

- SoftRF Legacy uses 2-FSK
- Bitrate: 100 kbps
- Frequency deviation: 50 kHz

Additional facts must include source references before being added.
