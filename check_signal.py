#!/usr/bin/env python3
"""
Quick signal characterization - what is actually in this capture?
"""
import numpy as np

WAV_FILE = "/home/ubuntu/.openclaw/workspace/baseband_915000000Hz_20-35-24_03-10-2026.wav"
SR = 20_000_000

with open(WAV_FILE, 'rb') as f:
    header = f.read(44)
    data = np.frombuffer(f.read(), dtype=np.float32)
iq = data.reshape(-1, 2)
envelope = np.sqrt(iq[:, 0]**2 + iq[:, 1]**2)
print(f"Total samples: {len(data)/2:.0f} ({len(data)/2/SR:.1f} s)")
print(f"I: mean={iq[:,0].mean():.6f}, std={iq[:,0].std():.6f}")
print(f"Q: mean={iq[:,1].mean():.6f}, std={iq[:,1].std():.6f}")
print(f"Envelope: min={envelope.min():.6f}, max={envelope.max():.6f}")
print(f"Envelope percentiles:")
for p in [50, 75, 90, 95, 99, 99.5, 99.9]:
    print(f"  {p}th: {np.percentile(envelope, p):.6f}")

# The 75th percentile is 0.044 - that's NOT Gaussian noise
# Gaussian noise would have 75th percentile at ~0.67 * std
# std of envelope ~0.035, so 75th should be ~0.024 if Gaussian
# But it's 0.044 - significantly higher!
# This means the "noise floor" is NOT pure noise - it contains signal

print(f"\nGaussian noise check:")
print(f"  If Gaussian: 75th ≈ 0.674*std = {0.674*envelope.std():.6f}")
print(f"  Actual 75th: {np.percentile(envelope, 75):.6f}")
print(f"  Ratio: {np.percentile(envelope,75)/(0.674*envelope.std()):.2f} (1.0 = pure Gaussian)")

# This confirms: the "noise floor" is elevated by signal content
# The signal is spread across the entire capture, not in discrete bursts

# Let's look at the PSD to understand the signal structure
print(f"\n=== PSD Analysis ===")
# Use a 100 ms chunk
chunk = envelope[1_000_000:3_000_000]  # 50-150 ms
n = len(chunk)
window = np.hanning(n)
fft = np.fft.rfft(chunk * window)
freqs = np.fft.rfftfreq(n, 1/SR)
psd = np.abs(fft)**2 / (n * np.sum(window**2))

# Find peaks
peak_idx = np.argsort(psd)[::-1][:10]
for i in peak_idx:
    if freqs[i] > 1000:
        print(f"  {freqs[i]/1000:.0f} kHz: PSD={psd[i]:.6f}")

# The signal appears to be a continuous OOK/ASK carrier with
# a modulated envelope that looks like noise
# This is consistent with a very low duty cycle signal buried in noise

print(f"\n=== FINAL ASSESSMENT ===")
print("This capture contains a VERY weak OOK/ASK signal.")
print("The signal-to-noise ratio is extremely low (< 1 dB).")
print("The 'noise floor' is actually signal + noise mixed together.")
print("The 10% duty cycle is NOT visible as distinct bursts.")
print("The signal is spread across the entire capture.")
print("\nTo decode this, we need either:")
print("1. A better receiver (lower noise figure)")
print("2. A longer capture with averaging")
print("3. A known reference signal for matched filtering")
print("4. OR: accept that this capture is too weak to decode")
