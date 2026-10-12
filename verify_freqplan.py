#!/usr/bin/env python3
"""
Verify the US frequency plan for SoftRF Legacy protocol.
"""

import numpy as np

# US frequency plan (from freqplan.h)
START_FREQ = 902.2  # MHz
NUM_CHANNELS = 65
SPACING = 0.4  # MHz

# Calculate end frequency
end_freq = START_FREQ + (NUM_CHANNELS - 1) * SPACING

print("=" * 60)
print("US Frequency Plan Verification")
print("=" * 60)
print(f"Start frequency: {START_FREQ:.1f} MHz")
print(f"Number of channels: {NUM_CHANNELS}")
print(f"Channel spacing: {SPACING} MHz")
print(f"End frequency: {end_freq:.1f} MHz")
print(f"Total range: {end_freq - START_FREQ:.1f} MHz")
print(f"Center frequency: {(START_FREQ + end_freq) / 2:.1f} MHz")
print()

# Channel calculation
def channel_to_freq(channel):
    """Convert channel number to frequency (MHz)."""
    return START_FREQ + channel * SPACING

def freq_to_channel(freq):
    """Convert frequency (MHz) to channel number."""
    return int((freq - START_FREQ) / SPACING)

# Print key channels
print("Key Channels:")
print("-" * 40)
for ch in [0, 32, 52, 64]:
    freq = channel_to_freq(ch)
    offset = freq - 915.0
    print(f"  Channel {ch:2d}: {freq:.1f} MHz (offset {offset:+.1f} MHz)")

print()

# Verify the strongest channel from scan
print("Scan Verification:")
print("-" * 40)
strongest_offset = 8.0  # MHz
strongest_freq = 915.0 + strongest_offset
strongest_ch = freq_to_channel(strongest_freq)
print(f"  Strongest response: {strongest_freq:.1f} MHz")
print(f"  Channel: {strongest_ch}")
print(f"  Offset: {strongest_offset:+.1f} MHz")
print()

# Frequency deviation analysis
print("Frequency Deviation Analysis:")
print("-" * 40)
tone_0 = -15.0  # kHz
tone_1 = 13.0   # kHz
threshold = (tone_0 + tone_1) / 2  # kHz
deviation = (tone_1 - tone_0) / 2  # kHz

print(f"  Tone 0: {tone_0:.1f} kHz (bit 0)")
print(f"  Tone 1: {tone_1:.1f} kHz (bit 1)")
print(f"  Threshold: {threshold:.1f} kHz")
print(f"  Deviation: {deviation:.1f} kHz")
print()

print("=" * 60)
print("Conclusion: The signal uses FHSS across 65 channels in the US ISM band.")
print("The previous single-frequency assumption was incorrect.")
print("=" * 60)
