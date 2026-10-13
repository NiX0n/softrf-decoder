#!/usr/bin/env python3
"""
Coherent Demodulation - The signal is a continuous carrier at ~-54° phase.
The data is in the AMPLITUDE variations (ASK) or PHASE variations (PSK).
Let's check both.
"""
import numpy as np

WAV_FILE = "/home/ubuntu/.openclaw/workspace/baseband_915000000Hz_20-35-24_03-10-2026.wav"
SR = 20_000_000

print("=== Coherent Demodulation ===")

with open(WAV_FILE, 'rb') as f:
    header = f.read(44)
    data = np.frombuffer(f.read(), dtype=np.float32)
iq = data.reshape(-1, 2)
I = iq[:, 0].astype(np.float32)
Q = iq[:, 1].astype(np.float32)

# The carrier is at phase ~ -0.94 rad
# Let's rotate to align it to 0°: multiply by exp(+j*0.94)
PHASE_OFFSET = 0.94
cos_p = np.cos(PHASE_OFFSET)
sin_p = np.sin(PHASE_OFFSET)

# Rotate: I' = I*cos + Q*sin, Q' = -I*sin + Q*cos
I_rot = I * cos_p + Q * sin_p
Q_rot = -I * sin_p + Q * cos_p

print(f"After rotating by +{PHASE_OFFSET} rad:")
print(f"  I_rot: mean={I_rot.mean():.6f}, std={I_rot.std():.6f}")
print(f"  Q_rot: mean={Q_rot.mean():.6f}, std={Q_rot.std():.6f}")

# If the signal is pure AM (ASK), Q_rot should be ~0 and I_rot should vary
# If there's PM, Q_rot will have content

# The real part (I_rot) after alignment should contain the AM signal
# Let's look at its distribution
print(f"\nI_rot percentiles:")
for p in [1, 10, 25, 50, 75, 90, 99]:
    print(f"  {p}th: {np.percentile(I_rot, p):.6f}")

# Now let's look at the envelope of the ROTATED signal
envelope_rot = np.sqrt(I_rot**2 + Q_rot**2)
print(f"\nRotated envelope:")
for p in [1, 10, 25, 50, 75, 90, 99]:
    print(f"  {p}th: {np.percentile(envelope_rot, p):.6f}")

# The key: after rotating, I_rot should be the AM envelope
# If the signal is OOK, I_rot should be bimodal: 0 (OFF) and A (ON)
# Let's check if I_rot is bimodal
print(f"\nI_rot histogram (20 bins):")
hist, edges = np.histogram(I_rot, bins=20)
for i in range(len(hist)):
    center = (edges[i] + edges[i+1]) / 2
    if hist[i] > 1000:
        print(f"  {center:.4f}: {'*' * min(hist[i]//10000, 50)} ({hist[i]//10000}k)")

# Also check: is there a frequency offset?
# If the carrier isn't exactly at 0 Hz after mixing, I_rot will oscillate
# Let's check the mean frequency of I_rot
print(f"\n=== Frequency Offset Check ===")
# Use Goertzel or simple correlation with a reference
# Take 100 ms and compute the dominant frequency
n = 2_000_000  # 100 ms
chunk = I_rot[:n]
fft = np.fft.rfft(chunk * np.hanning(n))
freqs = np.fft.rfftfreq(n, 1/SR)
peak_idx = np.argmax(np.abs(fft))
print(f"Dominant frequency of I_rot: {freqs[peak_idx]:.1f} Hz")
print(f"This is the residual frequency offset after mixing")

# If this is ~0 Hz, the carrier is well-centered
# If it's non-zero, we have a frequency offset to correct
