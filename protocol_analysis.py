#!/usr/bin/env python3
"""
The autocorrelation shows a clear periodicity at lag 26 (1.3 us).
This means the signal has a symbol rate of ~770 ksym/s.

The instantaneous frequency during ON periods is mostly negative
(-1.1 to -0.3 MHz), which means the carrier is BELOW the IF center.

Key insight: The signal is a COHERENT OOK/ASK signal with:
- Symbol rate: ~770 ksym/s
- Carrier offset: ~-0.5 to -1.0 MHz below IF center
- Phase: coherent at -50 to -60 degrees

This is NOT the 2-FSK protocol from the SoftRF legacy firmware.
This is a DIFFERENT protocol entirely.

Let me check: is this a known SoftRF variant? Or is this a
completely different radio protocol?

Actually, let me reconsider the whole approach. The user said
"you're absolutely certain the capture is correlated to TX Power."
This means the signal IS from the transmitter. But it's NOT the
2-FSK protocol I found in the firmware.

Possibilities:
1. The transmitter is using a DIFFERENT protocol than the legacy one.
2. The transmitter is using a SPREAD SPECTRUM protocol (e.g., DSSS, FHSS).
3. The transmitter is using a MODERN SoftRF protocol, not the legacy one.
4. There's a FREQUENCY OFFSET in the capture that's making it look different.

Let me check the SoftRF documentation for other protocol variants.
"""
import numpy as np

# From the analysis:
# - 12 bursts, each 5.14 ms
# - Symbol rate: ~770 ksym/s (from autocorrelation lag 26)
# - Burst spacing: ~200-800 ms (irregular)
# - OOK/ASK modulation
# - Coherent phase at -50 to -60 degrees
# - Carrier offset: ~-0.5 to -1.0 MHz

# Let me check: 770 ksym/s is close to 768 ksym/s = 2^10 / 2.6667
# Or maybe it's 800 ksym/s = 1/1.25 us

# Actually, the autocorrelation peak at lag 26 means:
# Symbol period = 26 samples
# At 20 MS/s: 26/20e6 = 1.3 us
# Symbol rate = 1/1.3us = 769.2 ksym/s

# 769.2 ksym/s is close to:
# - 768 ksym/s = 768 * 1024 bps = 786,432 bps (if 1 bit/symbol)
# - 800 ksym/s (round number)
# - 2/26 = 0.0769... hmm

# Let me check if this is a KNOWN standard:
# - 802.15.4 (Zigbee): 2.5 Msym/s (not this)
# - BLE: 1 Msym/s (not this)
# - 802.15.4-2020: 2.5 Msym/s (not this)
# - LoRa: variable, but not OOK
# - Sigfox: GFSK at 600 bps (not this)

# This doesn't match any standard I know. Let me check if it's
# a PROPRIETARY protocol.

# Actually, wait. Let me reconsider the symbol rate measurement.
# The autocorrelation peak at lag 26 could be:
# 1. The actual symbol period (770 ksym/s)
# 2. A HARMONIC of a lower symbol rate
# 3. An ARTIFACT of the sampling rate (20 MS/s / 26 ≈ 769 kHz)

# Let me check: 20 MS/s / 26 = 769.23 kHz
# And 20 MS/s / 25 = 800 kHz
# And 20 MS/s / 27 = 740.74 kHz

# 770 ksym/s is a very specific number. Let me see if it matches
# any common bit rates:
# - 768 kbps = 768 * 1024 = 786,432 bps
# - 800 kbps = 800,000 bps
# - 750 kbps = 750,000 bps

# None of these match exactly. Let me check if the symbol rate is
# actually 2x or 4x the data rate (e.g., Manchester coding).

# If the symbol rate is 770 ksym/s and it's Manchester coded:
# Data rate = 770 / 2 = 385 kbps
# That's close to 384 kbps = 384 * 1024 = 393,216 bps

# Or if it's NOT Manchester coded:
# Data rate = 770 kbps
# That's close to 768 kbps = 768 * 1024 = 786,432 bps

# Let me check: is 769.23 ksym/s = 1/1.3us?
# 1.3 us is a very specific time. Let me see if it matches
# any common clock frequencies:
# - 1.3 us = 1/769230 Hz
# - 769230 Hz is close to 768 kHz = 768 * 1024 Hz = 786,432 Hz
# - Or 769230 Hz is close to 20 MHz / 26 = 769,230.77 Hz

# Actually, 20 MHz / 26 is EXACTLY the sample rate divided by the
# autocorrelation lag. This might be a COINCIDENCE, or it might
# mean the symbol rate is locked to the sampling clock.

# Let me try a different approach: look at the RAW bitstream.
# If I can extract the ON/OFF pattern and see if it matches
# a known code (e.g., a pseudo-random sequence, a CRC, a preamble),
# that will tell me the protocol.

print("=== Signal Characterization Summary ===")
print(f"Sample rate: 20 MS/s")
print(f"Number of bursts: 12")
print(f"Burst duration: 5.14 ms")
print(f"Symbol period: 26 samples (1.3 us)")
print(f"Symbol rate: 769.2 ksym/s")
print(f"Modulation: OOK/ASK (coherent)")
print(f"Phase: -50 to -60 degrees")
print(f"Carrier offset: -0.5 to -1.0 MHz")
print()
print("=== Possible Protocols ===")
print(f"1. Proprietary OOK/ASK at 769 ksym/s")
print(f"2. Manchester-coded data at 384.6 kbps")
print(f"3. Unknown spread spectrum (DSSS/FHSS)")
print()
print("=== Next Steps ===")
print(f"1. Extract the ON/OFF bitstream from a burst")
print(f"2. Look for a preamble/sync pattern")
print(f"3. Check for CRC or other structure")
print(f"4. Compare with known SoftRF protocol variants")
