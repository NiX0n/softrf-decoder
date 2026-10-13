#!/usr/bin/env python3
"""OOK/ASK decoder v2 — vectorized burst extraction + symbol decoding."""

import numpy as np
from scipy.io import wavfile
from scipy.ndimage import uniform_filter1d, maximum_filter1d

rate, data = wavfile.read('../baseband_915000000Hz_20-35-24_03-10-2026.wav')
SR = rate

# --- Burst detection (vectorized) ---
env = np.abs(data)
env_smooth = uniform_filter1d(env, size=1000)
noise_floor = np.median(env_smooth)
threshold = noise_floor * 2

# Find peaks (local maxima above threshold)
peaks = maximum_filter1d(env_smooth, size=5000)
peak_idx = np.where((env_smooth == peaks) & (env_smooth > threshold))[0]

# Merge nearby peaks into bursts
bursts = []
if len(peak_idx) > 0:
    # Group peaks within 10ms of each other
    groups = []
    current_group = [peak_idx[0]]
    for p in peak_idx[1:]:
        if p - current_group[-1] < SR // 100:  # 10 ms
            current_group.append(p)
        else:
            if len(current_group) > 0:
                groups.append(current_group)
            current_group = [p]
    if len(current_group) > 0:
        groups.append(current_group)
    
    for g in groups:
        start = min(g) - SR // 200  # 5 ms before first peak
        end = max(g) + SR // 200    # 5 ms after last peak
        start = max(0, start)
        end = min(len(env), end)
        bursts.append((start, end))

print(f"Found {len(bursts)} burst groups")
for i, (s, e) in enumerate(bursts):
    duration = (e - s) / SR
    peak = np.max(env[s:e])
    avg = np.mean(env[s:e])
    print(f"  {i+1}: {duration:.3f} ms, peak={peak:.4f}, avg={avg:.4f}")

# --- Demodulate the best burst ---
if len(bursts) == 0:
    print("No bursts found, using full signal")
    burst = data
    env_b = env
else:
    best = max(range(len(bursts)), key=lambda i: np.max(env[bursts[i][0]:bursts[i][1]]))
    bs, be = bursts[best]
    burst = data[bs:be]
    env_b = env[bs:be]
    print(f"\n=== Demodulating burst {best+1} ===")
    print(f"Length: {len(env_b)} samples = {len(env_b)/SR*1e3:.2f} ms")

# Remove DC
env_b = env_b - np.mean(env_b)

# --- Try symbol rates ---
for sym_khz in [769]:
    sps = SR / (sym_khz * 1000)
    n_sym = int(len(env_b) / sps)
    
    # Vectorized: sample at symbol rate using max in each window
    indices = np.arange(n_sym) * int(sps)
    symbols = np.array([np.max(env_b[idx:idx+int(sps)]) for idx in indices])
    
    thr = (symbols.max() + symbols.min()) / 2
    bits = (symbols > thr).astype(int)
    
    print(f"\n{sym_khz} ksym/s: {n_sym} symbols")
    print(f"  sym range: [{symbols.min():.6f}, {symbols.max():.6f}]")
    print(f"  threshold: {thr:.6f}")
    print(f"  bits[:64]: {bits[:64].tolist()}")
    print(f"  bit ratio (1s): {bits.mean():.3f}")
    
    # Run-length
    changes = np.where(np.diff(bits) != 0)[0]
    run_lengths = np.diff(np.concatenate([[-1], changes, [len(bits)]]))
    print(f"  run-lengths: min={run_lengths.min()}, max={run_lengths.max()}, mean={run_lengths.mean():.2f}")
    
    # Manchester decode
    man = []
    for i in range(0, len(bits)-1, 2):
        if bits[i] == 1 and bits[i+1] == 0:
            man.append(1)
        elif bits[i] == 0 and bits[i+1] == 1:
            man.append(0)
    
    man = np.array(man)
    print(f"  Manchester: {len(man)} bits")
    print(f"  man[:64]: {man[:64].tolist()}")
    
    # To bytes
    man_bytes = []
    for i in range(0, len(man)-7, 8):
        b = 0
        for j in range(8):
            b = (b << 1) | man[i+j]
        man_bytes.append(b)
    
    print(f"  First 32 bytes: {man_bytes[:32]}")
    
    # Syncword search
    sync = [0x55, 0x99, 0xA5, 0xA9, 0x55, 0x66, 0x65, 0x96]
    found = False
    for i in range(len(man_bytes)-7):
        if man_bytes[i:i+8] == sync:
            print(f"\n  >>> SOFT RF SYNCWORD at byte {i}!")
            found = True
            break
    if not found:
        print(f"\n  No SoftRF syncword found.")
