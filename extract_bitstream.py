#!/usr/bin/env python3
"""
Extract the ON/OFF bitstream from a burst and look for structure.
"""
import numpy as np
from scipy.ndimage import uniform_filter1d
from collections import Counter

fpath = '/home/ubuntu/.openclaw/workspace/baseband_915000000Hz_20-35-24_03-10-2026.wav'
with open(fpath, 'rb') as f:
    f.read(44)
    buf = np.fromfile(f, dtype=np.float32)
iq = buf.reshape(-1, 2)

# Find the first real burst
amp_full = np.sqrt(iq[:,0].astype(np.float64)**2 + iq[:,1].astype(np.float64)**2)
env = uniform_filter1d(amp_full, size=100)
active = env > 0.05
transitions = np.diff(active.astype(int))
starts = np.where(transitions == 1)[0]
ends = np.where(transitions == -1)[0]
real_bursts = [(s, e) for s, e in zip(starts, ends) if e - s > 1000]

s, e = real_bursts[0]
I = iq[s:e, 0].astype(np.float64)
Q = iq[s:e, 1].astype(np.float64)
amp = np.sqrt(I**2 + Q**2)

# Extract the ON/OFF bitstream
# Use a threshold at the 50th percentile
on_threshold = np.percentile(amp, 50)
on_mask = (amp > on_threshold).astype(int)

print(f"Burst: {len(I)} samples")
print(f"ON threshold: {on_threshold:.4f}")
print(f"ON samples: {on_mask.sum()} ({100*on_mask.sum()/len(on_mask):.1f}%)")
print(f"OFF samples: {(1-on_mask).sum()} ({100*(1-on_mask).sum()/len(on_mask):.1f}%)")

# Print the first 100 bits
print(f"\nFirst 100 bits: {''.join(map(str, on_mask[:100]))}")

# Find the symbol rate by looking at the run lengths
runs = []
current_run = 1
for i in range(1, len(on_mask)):
    if on_mask[i] == on_mask[i-1]:
        current_run += 1
    else:
        runs.append((on_mask[i-1], current_run))
        current_run = 1
runs.append((on_mask[-1], current_run))

# Count the run lengths
run_lengths = [r[1] for r in runs]
run_length_counts = Counter(run_lengths)
print(f"\nRun length distribution (top 10):")
for length, count in sorted(run_length_counts.items())[:10]:
    print(f"  {length} samples ({length/20e6*1e6:.1f} us): {count} runs")

# The most common run length is likely the symbol duration
most_common_length = max(run_length_counts, key=run_length_counts.get)
print(f"\nMost common run length: {most_common_length} samples ({most_common_length/20e6*1e6:.2f} us)")
print(f"Implied symbol rate: {1/(most_common_length/20e6)/1000:.1f} ksym/s")

# Now let me look at the PHASE during ON periods to see if there's
# phase information (DPSK or QPSK)
on_indices = np.where(on_mask == 1)[0]
if len(on_indices) > 10:
    on_phase = np.arctan2(Q[on_indices], I[on_indices])
    print(f"\nPhase during ON periods:")
    print(f"  Mean: {np.degrees(on_phase.mean()):.1f} deg")
    print(f"  Std: {np.degrees(on_phase.std()):.1f} deg")
    print(f"  Min: {np.degrees(on_phase.min()):.1f} deg")
    print(f"  Max: {np.degrees(on_phase.max()):.1f} deg")
    
    # Check if there are distinct phase clusters (QPSK?)
    hist, bins = np.histogram(on_phase, bins=16, range=(-np.pi, np.pi))
    print(f"  Phase histogram:")
    for i in range(len(hist)):
        if hist[i] > 0:
            print(f"    {np.degrees(bins[i]):.0f} to {np.degrees(bins[i+1]):.0f} deg: {hist[i]}")

# Check the AMPLITUDE distribution during ON periods
on_amp = amp[on_mask]
print(f"\nAmplitude during ON periods:")
print(f"  Mean: {on_amp.mean():.4f}")
print(f"  Std: {on_amp.std():.4f}")
print(f"  Min: {on_amp.min():.4f}")
print(f"  Max: {on_amp.max():.4f}")

# Check if there are distinct amplitude levels (ASK?)
hist, bins = np.histogram(on_amp, bins=10)
print(f"  Amplitude histogram:")
for i in range(len(hist)):
    if hist[i] > 0:
        print(f"    {bins[i]:.4f} to {bins[i+1]:.4f}: {hist[i]}")
