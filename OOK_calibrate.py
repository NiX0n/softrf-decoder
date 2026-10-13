#!/usr/bin/env python3
"""
Calibrate the OOK threshold properly using the bimodal distribution.
"""
import numpy as np

WAV_FILE = "/home/ubuntu/.openclaw/workspace/baseband_915000000Hz_20-35-24_03-10-2026.wav"
SR = 20_000_000

with open(WAV_FILE, 'rb') as f:
    header = f.read(44)
    data = np.frombuffer(f.read(), dtype=np.float32)
iq = data.reshape(-1, 2)
I = iq[:, 0].astype(np.float32)
Q = iq[:, 1].astype(np.float32)

# Rotate
PHASE_OFFSET = 0.94
I_rot = I * np.cos(PHASE_OFFSET) + Q * np.sin(PHASE_OFFSET)

# Find the two peaks using KMeans-like approach
# Simply: split at the median of the two most common values
# Use histogram to find peaks
hist, edges = np.histogram(I_rot, bins=200)
peak1_idx = np.argmax(hist)
peak1_center = (edges[peak1_idx] + edges[peak1_idx+1]) / 2

# Find second peak (exclude first peak region)
mask = (np.abs(I_rot - peak1_center) > (edges[1] - edges[0]))
hist2, _ = np.histogram(I_rot[mask], bins=200)
peak2_idx = np.argmax(hist2)
# Need to map back to original edges... this is getting complicated.

# Simpler: use Otsu's threshold
def otsu_threshold(x, bins=256):
    hist, edges = np.histogram(x, bins=bins)
    centers = (edges[:-1] + edges[1:]) / 2
    total = hist.sum()
    sum_total = (hist * centers).sum()
    w0 = 0; s0 = 0; best = 0; best_thresh = 0
    for i in range(1, bins):
        w0 += hist[i-1]
        if w0 == 0: continue
        w1 = total - w0
        if w1 == 0: break
        s0 += (i-1) * hist[i-1]
        m0 = s0 / w0
        m1 = (sum_total - s0) / w1
        var = w0 * w1 * (m0 - m1)**2
        if var > best:
            best = var
            best_thresh = centers[i-1]
    return best_thresh

thresh = otsu_threshold(I_rot)
print(f"Otsu threshold: {thresh:.6f}")
symbols = (I_rot > thresh).astype(np.uint8)
print(f"ON fraction: {symbols.mean()*100:.2f}%")

# Try different thresholds and see which gives ~10%
print("\nThreshold sweep:")
for t in np.linspace(-0.03, 0.03, 13):
    frac = (I_rot > t).mean()
    print(f"  thresh={t:+.4f}: ON={frac*100:.1f}%")

# The 10% duty cycle means the threshold should give 10% ON
# Find the 90th percentile of I_rot
p90 = np.percentile(I_rot, 90)
print(f"\n90th percentile: {p90:.6f}")
symbols_10 = (I_rot > p90).astype(np.uint8)
print(f"ON fraction at 90th pct: {symbols_10.mean()*100:.2f}%")

# Check: is the distribution actually bimodal?
# A bimodal distribution would have two distinct peaks
# Let's look at the top 10 most common values
print("\nTop 10 value ranges (by count):")
hist, edges = np.histogram(I_rot, bins=50)
sorted_idx = np.argsort(hist)[::-1][:10]
for i in sorted_idx:
    center = (edges[i] + edges[i+1]) / 2
    print(f"  {center:+.4f}: {hist[i]} samples ({hist[i]/len(I_rot)*100:.2f}%)")
