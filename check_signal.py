"""Check if the signal is actually FSK by looking at phase rotation.

The I channel might be DC-coupled and the actual FSK is in the phase.
Let me try:
1. Look at the full I/Q vector for each sample
2. Check if the signal rotates (phase) vs oscillates (amplitude)
3. Try proper FM demod on I/Q
"""
import numpy as np

fpath = '/home/ubuntu/.openclaw/workspace/baseband_915000000Hz_20-35-24_03-10-2026.wav'
with open(fpath, 'rb') as f:
    f.read(44)
    buf = np.fromfile(f, dtype=np.float32)

iq = buf.reshape(-1, 2)
n = 10_000_000
I = iq[:n, 0].astype(np.float64)
Q = iq[:n, 1].astype(np.float64)

# Check amplitude and phase
amp = np.sqrt(I**2 + Q**2)
phase = np.arctan2(Q, I)
print(f"Amp: min={amp.min():.6f} max={amp.max():.6f} mean={amp.mean():.6f}")
print(f"Phase: min={np.degrees(phase.min()):.1f} max={np.degrees(phase.max()):.1f}")
print(f"Phase std: {np.degrees(phase.std()):.1f} deg")

# The signal is almost purely in I with tiny Q.
# If it's FSK at baseband, the I channel should show:
# - Two distinct amplitude levels for 2-FSK (if amplitude modulated)
# - Or phase rotation for FM

# Check if there's ANY Q component variation
q_diff = np.diff(Q)
print(f"\nQ: mean={Q.mean():.6f} std={Q.std():.6f} min={Q.min():.6f} max={Q.max():.6f}")
print(f"Q diff: std={q_diff.std():.6f} max_abs={np.abs(q_diff).max():.6f}")

# Check the I channel more carefully
# The 5-level distribution we saw earlier (0.0156, 0.0234, 0.0312, 0.0391, 0.0469)
# suggests the signal is actually varying! Let me look at it in a different way.

# The signal levels are quantized to steps of ~0.0078
# This could be 4-level FSK (4-FSK) rather than 2-FSK!
# Or it could be amplitude-modulated with 4 levels.

# Check the distribution more carefully
levels, counts = np.unique(np.round(I, 4), return_counts=True)
print(f"\nI channel levels (top 10):")
for l, c in sorted(zip(levels, counts), key=lambda x: -x[1])[:10]:
    print(f"  {l:.4f}: {c} ({100*c/n:.1f}%)")

# Check if the levels form pairs (suggesting 2-FSK with noise)
# or 4 distinct levels (suggesting 4-FSK)

# Let me try to find the "word" boundaries by looking at level transitions
# Count how many times the level changes
level_ids = np.searchsorted(np.sort(levels)[::-1][::-1], I, side='right')
# This is getting complex. Let me just check: is the signal varying?
print(f"\nI channel: std={I.std():.6f}, range={I.max()-I.min():.6f}")
print(f"Number of unique I values: {len(levels)}")

# Check if there's a periodic pattern
# The signal is at 20 MS/s with 100 samples per bit (100 kbps)
# Look at the autocorrelation at lag 100
ac = np.correlate(I[:1_000_000].astype(np.float32) - I[:1_000_000].mean(), 
                  I[:1_000_000].astype(np.float32) - I[:1_000_000].mean(), mode='valid')[:200]
ac /= ac[0]
peaks = []
for i in range(2, 200):
    if ac[i] > ac[i-1] and ac[i] > ac[i+1] and ac[i] > 0.01:
        peaks.append((i, ac[i]))
print(f"\nAutocorrelation peaks (top 5): {sorted(peaks, key=lambda x:-x[1])[:5]}")
