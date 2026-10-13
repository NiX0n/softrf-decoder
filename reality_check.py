#!/usr/bin/env python3
"""
REALITY CHECK: Let me re-read the task description carefully.

"10% duty cycle signal" - this is a KEY constraint I've been ignoring!

If the signal has 10% duty cycle, then 10% of the time the carrier is ON,
and 90% of the time it's OFF. This is NOT low SNR - this is a NORMAL
modulation scheme where the signal alternates between ON and OFF states.

The problem is: I've been treating the envelope as if it should be clearly
bimodal (ON vs OFF), but with 10% duty cycle, the OFF periods are 90%
of the time. So the "noise floor" I measured IS the OFF state, and the
"signal peaks" are the ON state.

But wait - the 75th percentile is 0.044, and the 99th is 0.164.
If 90% of the time is OFF and 10% is ON, then:
- 90th percentile should be in the OFF range
- But 90th percentile is 0.046, which is close to the 75th (0.044)
- This means 90% of samples are at ~0.044 level

That's NOT consistent with 10% duty cycle OOK!

Unless... the "10% duty cycle" refers to something else?
Or the signal is not simple OOK?

Let me reconsider: maybe the 915 MHz carrier is ALWAYS present,
and the "10% duty cycle" refers to the DATA modulation on top of it?
Like, the carrier is always there (hence the elevated "noise floor"),
and the data is modulated as small variations on top?

This would make sense if:
- The receiver is not perfectly centered on 915 MHz
- There's a DC offset or I/Q imbalance
- The "carrier" is actually a mixing artifact

Let me check the raw I and Q separately:
"""
import numpy as np

WAV_FILE = "/home/ubuntu/.openclaw/workspace/baseband_915000000Hz_20-35-24_03-10-2026.wav"
SR = 20_000_000

with open(WAV_FILE, 'rb') as f:
    header = f.read(44)
    data = np.frombuffer(f.read(), dtype=np.float32)
iq = data.reshape(-1, 2)
I = iq[:, 0]
Q = iq[:, 1]

print("=== I/Q Analysis ===")
print(f"I: mean={I.mean():.6f}, std={I.std():.6f}, min={I.min():.6f}, max={I.max():.6f}")
print(f"Q: mean={Q.mean():.6f}, std={Q.std():.6f}, min={Q.min():.6f}, max={Q.max():.6f}")

# If this is a carrier at 915 MHz, I and Q should be correlated
# (both oscillating at the carrier frequency)
# But if the receiver is perfectly centered, I and Q should be 90° out of phase

# Let's check the phase:
phase = np.arctan2(Q, I)
print(f"\nPhase: mean={phase.mean():.4f} rad, std={phase.std():.4f} rad")
print(f"Phase histogram (10 bins):")
hist, edges = np.histogram(phase, bins=10, range=(-np.pi, np.pi))
for i in range(len(hist)):
    center = (edges[i] + edges[i+1]) / 2
    print(f"  {center:.2f} rad: {'*' * min(hist[i]//100000, 50)} ({hist[i]//100000}k)")

# If phase is uniform, the signal is noise
# If phase is concentrated, there's a carrier

# Also: what's the power spectrum of I and Q?
print("\n=== I/Q Power Spectrum (100 ms chunk) ===")
chunk_I = I[1_000_000:3_000_000]
chunk_Q = Q[1_000_000:3_000_000]
n = len(chunk_I)
window = np.hanning(n)
fft_I = np.fft.rfft(chunk_I * window)
fft_Q = np.fft.rfft(chunk_Q * window)
freqs = np.fft.rfftfreq(n, 1/SR)
psd_I = np.abs(fft_I)**2
psd_Q = np.abs(fft_Q)**2
psd_total = psd_I + psd_Q

# Find the 5 strongest peaks
peaks = np.argsort(psd_total)[::-1][:5]
for i in peaks:
    if freqs[i] > 1000:
        print(f"  {freqs[i]/1000:.0f} kHz: PSD_I={psd_I[i]:.2f}, PSD_Q={psd_Q[i]:.2f}")

# The key question: is there a carrier?
# If I and Q both have strong peaks at the same frequency, there's a carrier
# If they're uncorrelated, it's noise

print("\n=== KEY INSIGHT ===")
print("If the '10% duty cycle' is correct, then 10% of the time")
print("the signal should be at a DIFFERENT level than the other 90%.")
print("\nBut I measured:")
print("  50th pct: 0.039 (median)")
print("  75th pct: 0.044")
print("  90th pct: 0.046")
print("  95th pct: 0.050")
print("  99th pct: 0.164")
print("\nThis is NOT a bimodal distribution! It's a continuous distribution")
print("with a long tail. This is consistent with NOISE, not OOK.")
print("\nUNLESS: the '10% duty cycle' refers to something I'm not seeing,")
print("like a very short preamble or a different modulation scheme entirely.")
