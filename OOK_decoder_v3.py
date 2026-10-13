#!/usr/bin/env python3
"""OOK/ASK decoder v3 — burst extraction + OOK demodulation."""

import numpy as np
from scipy.io import wavfile

rate, data = wavfile.read('../baseband_915000000Hz_20-35-24_03-10-2026.wav')
SR = rate
print(f"Loaded: {len(data)} samples @ {SR} Hz")

env = np.abs(data)
print(f"Env: max={env.max():.4f}, mean={env.mean():.4f}")

# Find contiguous regions above a meaningful threshold
# The 10% duty cycle means signal is present ~10% of the time
# Use a threshold well above the noise floor
threshold = 0.05  # ~1.8x the mean
above = env > threshold

# Find all contiguous regions above threshold
transitions = np.diff(above.astype(int))
starts = np.where(transitions == 1)[0] + 1
ends = np.where(transitions == -1)[0] + 1

# Pair them up
bursts = []
for s, e in zip(starts, ends):
    if e - s > 50000:  # > 2.5 ms = real burst, not noise spike
        bursts.append((s, e))

print(f"Found {len(bursts)} bursts > 2.5ms")
for i, (s, e) in enumerate(bursts[:20]):
    print(f"  {i}: {(e-s)/SR*1e3:.2f} ms, peak={env[s:e].max():.4f}")

# Use the longest burst (best SNR)
if bursts:
    longest = max(bursts, key=lambda x: x[1]-x[0])
    bs, be = longest
    burst_env = env[bs:be].copy()
    print(f"\nUsing longest burst: {(be-bs)/SR*1e3:.2f} ms")
    print(f"  Burst env: min={burst_env.min():.4f}, max={burst_env.max():.4f}")
    
    # Remove DC offset
    burst_env = burst_env - np.mean(burst_env)
    
    # Symbol rate: 769 ksym/s => 26.01 samples/symbol
    sym_rate = 769e3
    sps = SR / sym_rate
    n_sym = int(len(burst_env) / sps)
    print(f"  Symbols: {n_sym} at {sym_rate/1e3:.0f} ksym/s")
    
    # OOK: sample at symbol centers (max in window)
    # Vectorized version
    n_sym = int(len(burst_env) / sps)
    idx = np.arange(n_sym) * int(sps)
    symbols = np.array([burst_env[idx+np.arange(int(sps))].max() for idx in idx])
    
    # Threshold: midpoint of two modes
    thr = (symbols.max() + symbols.min()) / 2
    bits = (symbols > thr).astype(np.uint8)
    print(f"  Symbols: {n_sym}, range [{symbols.min():.4f}, {symbols.max():.4f}]")
    print(f"  Bits: {len(bits)}, 1s={bits.sum()}")
    print(f"  bits[:48]: {bits[:48].tolist()}")
    
    # Manchester decode
    man = []
    for i in range(0, len(bits)-1, 2):
        if bits[i]==1 and bits[i+1]==0: man.append(1)
        elif bits[i]==0 and bits[i+1]==1: man.append(0)
    
    print(f"  Manchester: {len(man)} bits")
    print(f"  man[:48]: {man[:48]}")
    
    # Bytes
    mb = []
    for i in range(0, len(man)-7, 8):
        b = 0
        for j in range(8):
            b = (b<<1) | man[i+j]
        mb.append(b)
    print(f"  First 24 bytes: {mb[:24]}")
    
    # Try to find sync pattern
    sync = [0x55,0x99,0xA5,0xA9,0x55,0x66,0x65,0x96]
    for i in range(len(mb)-7):
        if mb[i:i+8]==sync:
            print(f"  SYNC found at byte {i}!")
            break
    else:
        print("  No sync pattern found")
        
    # Also try: maybe the 769 ksym/s rate is wrong
    # Try 115.2 kbps (173.6 symbols/s)
    sym_rate2 = 115.2e3
    sps2 = SR / sym_rate2
    n_sym2 = int(len(burst_env) / sps2)
    print(f"\n  Trying {sym_rate2/1e3:.1f} ksym/s: {n_sym2} symbols")
    
    # Try 57.6 kbps
    sym_rate3 = 57.6e3
    sps3 = SR / sym_rate3
    n_sym3 = int(len(burst_env) / sps3)
    print(f"  Trying {sym_rate3/1e3:.1f} ksym/s: {n_sym3} symbols")
