#!/usr/bin/env python3
"""
Sweep thresholds to find the one that gives 10% duty cycle.
The OOK signal should have ON = 10% and OFF = 90% (or vice versa).
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

# Find the threshold that gives exactly 10% ON
# This means the 90th percentile (if ON is the high values)
# or the 10th percentile (if ON is the low values)

p10 = np.percentile(I_rot, 10)
p90 = np.percentile(I_rot, 90)
print(f"10th percentile: {p10:.6f}")
print(f"90th percentile: {p90:.6f}")

# Check: 10% of samples are above p90 (high = ON)
on_high = (I_rot > p90).mean()
print(f"\nON (high, > p90={p90:.6f}): {on_high*100:.1f}%")

# Or: 10% of samples are below p10 (low = ON)
on_low = (I_rot < p10).mean()
print(f"ON (low, < p10={p10:.6f}): {on_low*100:.1f}%")

# The correct threshold should give exactly 10%
# Let's find the exact value
# If ON is high: threshold = p90, and ON = (I > p90).mean() ≈ 10%
# If ON is low: threshold = p10, and ON = (I < p10).mean() ≈ 10%

# Which one makes sense for OOK?
# In OOK, ON = carrier present (high amplitude), OFF = carrier absent (low amplitude)
# So ON should be the HIGH values
# threshold should be p90

threshold = p90
symbols = (I_rot > threshold).astype(np.uint8)
print(f"\nUsing threshold={threshold:.6f} (p90)")
print(f"ON fraction: {symbols.mean()*100:.2f}%")

# Now let's check the symbol rate by looking at the transition rate
transitions = np.sum(np.diff(symbols) != 0)
print(f"Transitions: {transitions}")
print(f"Transition rate: {transitions / len(symbols) * 100:.2f}% of samples")

# The minimum burst duration should be at least 1 sample (50ns)
# Let's find the distribution of burst durations
on_runs = []
off_runs = []
current = symbols[0]
count = 1
for i in range(1, len(symbols)):
    if symbols[i] == current:
        count += 1
    else:
        if current == 1:
            on_runs.append(count)
        else:
            off_runs.append(count)
        current = symbols[i]
        count = 1
if current == 1:
    on_runs.append(count)
else:
    off_runs.append(count)

print(f"\nON runs: {len(on_runs)}")
print(f"  min: {min(on_runs)} samples = {min(on_runs)/SR*1e6:.2f} ms")
print(f"  median: {np.median(on_runs)} samples = {np.median(on_runs)/SR*1e6:.2f} ms")
print(f"  max: {max(on_runs)} samples = {max(on_runs)/SR*1e6:.2f} ms")

print(f"\nOFF runs: {len(off_runs)}")
print(f"  min: {min(off_runs)} samples = {min(off_runs)/SR*1e6:.2f} ms")
print(f"  median: {np.median(off_runs)} samples = {np.median(off_runs)/SR*1e6:.2f} ms")
print(f"  max: {max(off_runs)} samples = {max(on_runs)/SR*1e6:.2f} ms")

# The minimum symbol duration should be consistent
# If OOK is at 769 ksym/s, each symbol = 26 samples
min_symbol = min(min(on_runs), min(off_runs))
print(f"\nMinimum symbol duration: {min_symbol} samples = {min_symbol/SR*1e6:.2f} ms")
if min_symbol > 0:
    print(f"Estimated symbol rate: {SR/min_symbol/1000:.1f} ksym/s")
