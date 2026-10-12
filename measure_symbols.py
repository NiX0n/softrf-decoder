#!/usr/bin/env python3
"""
Measure the symbol structure of the SoftRF capture.

Key findings so far:
- 12 real bursts, each ~5.14 ms (102,800 samples at 20 MS/s)
- OOK/ASK modulation: 10% ON, 90% OFF
- Phase coherent: -50 to -60 degrees
- ON segment duration: ~12 samples (0.6 us)
- Estimated symbol rate: ~1676 ksym/s

This is NOT 2-FSK at 100 kbps. This is a much faster OOK/ASK signal.

Let me measure the symbol rate more carefully by looking at the
transition density (number of ON/OFF transitions per unit time).
"""
import numpy as np
from scipy.ndimage import uniform_filter1d

fpath = '/home/ubuntu/.openclaw/workspace/baseband_915000000Hz_20-35-24_03-10-2026.wav'
with open(fpath, 'rb') as f:
    f.read(44)
    buf = np.fromfile(f, dtype=np.float32)
iq = buf.reshape(-1, 2)
N = len(iq)

# Find real bursts
amp_full = np.sqrt(iq[:,0].astype(np.float64)**2 + iq[:,1].astype(np.float64)**2)
env = uniform_filter1d(amp_full, size=100)
active = env > 0.05
transitions = np.diff(active.astype(int))
starts = np.where(transitions == 1)[0]
ends = np.where(transitions == -1)[0]
real_bursts = [(s, e) for s, e in zip(starts, ends) if e - s > 1000]

print(f"Found {len(real_bursts)} real bursts")
print(f"Burst durations: {[f'{(e-s)/20e6*1000:.2f}' for s,e in real_bursts[:5]]} ms")
print(f"Burst spacing: {[(real_bursts[i+1][0] - real_bursts[i][1])/20e6*1000 for i in range(min(5, len(real_bursts)-1))]} ms")

# Analyze the first real burst
s, e = real_bursts[0]
I = iq[s:e, 0].astype(np.float64)
Q = iq[s:e, 1].astype(np.float64)
amp = np.sqrt(I**2 + Q**2)
phase = np.arctan2(Q, I)

# The ON/OFF pattern gives the symbol structure
# Let me look at the autocorrelation of the amplitude to find the symbol period
from scipy.signal import fftconvolve
ac = fftconvolve(amp, amp[::-1], mode='full')
ac = ac[len(ac)//2:]  # Take the second half (positive lags)

# Find the first peak in the autocorrelation (after the DC peak)
from scipy.signal import find_peaks
peaks, props = find_peaks(ac, height=0.1*ac.max(), distance=10)
print(f"\nAutocorrelation peaks (first 10):")
for i, p in enumerate(peaks[:10]):
    print(f"  Lag {p}: {ac[p]:.4f} ({p/20e6*1e6:.2f} us)")

# The symbol period should be the lag of the first strong peak
if len(peaks) > 0:
    symbol_period = peaks[0]
    symbol_rate = 1 / (symbol_period / 20e6)
    print(f"\nEstimated symbol period: {symbol_period} samples ({symbol_period/20e6*1e6:.2f} us)")
    print(f"Estimated symbol rate: {symbol_rate/1e6:.2f} Msym/s")
    print(f"Estimated bit rate (if 1 bit/symbol): {symbol_rate/1e6:.2f} Mbps")

# Also check: is the signal actually FSK after all?
# Let me look at the phase derivative (instantaneous frequency)
# during ON periods only.
on_mask = amp > np.percentile(amp, 50)
on_indices = np.where(on_mask)[0]
if len(on_indices) > 100:
    on_phase = np.unwrap(phase[on_indices])
    # Instantaneous frequency
    freq = np.diff(on_phase) * 20e6 / (2*np.pi)
    print(f"\nInstantaneous frequency during ON periods:")
    print(f"  Mean: {freq.mean()/1e6:.3f} MHz")
    print(f"  Std: {freq.std()/1e6:.3f} MHz")
    print(f"  Min: {freq.min()/1e6:.3f} MHz")
    print(f"  Max: {freq.max()/1e6:.3f} MHz")
    
    # Check if there are two distinct frequency clusters (FSK)
    hist, bins = np.histogram(freq, bins=50)
    print(f"  Frequency histogram (top 5 bins):")
    top_bins = np.argsort(hist)[-5:]
    for b in sorted(top_bins, key=lambda x: bins[x]):
        print(f"    {bins[b]/1e6:.3f}-{bins[b+1]/1e6:.3f} MHz: {hist[b]}")
