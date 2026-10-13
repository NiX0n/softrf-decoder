#!/usr/bin/env python3
"""
OOK Demodulator v2 - Robust decoder using:
1. Burst-level aggregation (not sample-level)
2. Adaptive threshold (midway between noise floor and signal level)
3. Symbol timing search via autocorrelation
4. Sync word search with bit-slip correction

Key insight from v1: SNR is low (~1.7) so sample-level thresholding is unreliable.
Instead, aggregate over sub-burst durations (30-32 ms) which should contain
many symbols. This gives effective SNR improvement via integration.
"""
import numpy as np
import struct

WAV_FILE = "/home/ubuntu/.openclaw/workspace/baseband_915000000Hz_20-35-24_03-10-2026.wav"
SR = 20_000_000
SYNC = [0x55, 0x99, 0xA5, 0xA9, 0x55, 0x66, 0x65, 0x96]
SYNC_BITS = []
for b in SYNC:
    for i in range(7, -1, -1):
        SYNC_BITS.append(1 if (b >> i) & 1 else 0)
SYNC_BITS = np.array(SYNC_BITS, dtype=np.uint8)
SYNC_LEN = 64

print("=== OOK Demodulator v2 (Robust) ===")
print(f"SYNC pattern: {len(SYNC_BITS)} bits ({SYNC_LEN/2:.0f} bytes)")

# Load signal
with open(WAV_FILE, 'rb') as f:
    header = f.read(44)
    data = np.frombuffer(f.read(), dtype=np.float32)
iq = data.reshape(-1, 2)
envelope = np.sqrt(iq[:, 0]**2 + iq[:, 1]**2)

# Adaptive threshold: noise floor = median, signal = 20th percentile above
noise_floor = np.median(envelope)
signal_level = np.percentile(envelope, 99.5)  # strong signal level
threshold = (noise_floor + signal_level) / 2
print(f"Noise floor: {noise_floor:.4f}")
print(f"Signal level (99.5th pct): {signal_level:.4f}")
print(f"Threshold: {threshold:.4f}")

# Find active windows where signal is present
active = envelope > threshold
# Find runs of active
runs = []
i = 0
while i < len(active):
    if active[i]:
        j = i
        while j < len(active) and active[j]:
            j += 1
        if j - i > 2 * SR:  # > 2 ms
            runs.append((i, j))
        i = j
    else:
        i += 1
print(f"\nActive windows (>2ms): {len(runs)}")
for idx, (s, e) in enumerate(runs[:10]):
    t = s / SR * 1000
    d = (e - s) / SR * 1000
    print(f"  Window {idx}: t={t:.1f} ms, duration={d:.1f} ms, peak={envelope[s:e].max():.4f}")

# For each active window, try to decode
# Strategy: Within a window, the signal is modulated.
# Use a lower threshold (just above noise) to detect symbol-level activity
# and then count ON/OFF per symbol period.

# Try multiple symbol rates based on the 30-32 ms sub-burst structure
# If each sub-burst is 30-32 ms and contains many symbols:
# At 769 ksym/s: 30ms * 769k = 23,070 symbols
# At 384.5 ksym/s: 30ms * 384.5k = 11,535 symbols
# At 234 ksym/s: 30ms * 234k = 7,020 symbols
# At 117 ksym/s: 30ms * 117k = 3,510 symbols
# At 58.5 ksym/s: 30ms * 58.5k = 1,755 symbols
# At 30 ksym/s: 30ms * 30k = 900 symbols

symbol_rates = [769000, 384500, 234000, 117000, 58500, 30000]

def try_decode(window_start, window_end, sym_rate, thresh):
    """Decode a window at a given symbol rate and threshold.
    Returns (score, bits) where score is sync match count."""
    n_samples = window_end - window_start
    seg = envelope[window_start:window_end]
    
    # Determine symbols
    n_symbols = int(n_samples / (SR / sym_rate))
    if n_symbols < SYNC_LEN:
        return 0, None
    
    sym_samples = SR / sym_rate
    symbols = np.zeros(n_symbols, dtype=np.uint8)
    for s in range(n_symbols):
        start = int(s * sym_samples)
        end = min(int((s+1) * sym_samples), n_samples)
        if end > start:
            symbols[s] = 1 if np.mean(seg[start:end]) > thresh else 0
    
    # Search for sync pattern
    best_score = 0
    best_pos = -1
    for pos in range(n_symbols - SYNC_LEN + 1):
        match = np.sum(symbols[pos:pos+SYNC_LEN] == SYNC_BITS)
        if match > best_score:
            best_score = match
            best_pos = pos
    
    return best_score, (symbols, best_pos)

# Try the best window with multiple rates
if runs:
    # Use the longest window
    best_window = max(runs, key=lambda r: r[1] - r[0])
    ws, we = best_window
    print(f"\nDecoding window: t={ws/SR*1000:.1f} ms, duration={(we-ws)/SR*1000:.1f} ms")
    
    results = []
    for rate in symbol_rates:
        score, result = try_decode(ws, we, rate, threshold)
        results.append((score, rate, result))
        print(f"  Rate {rate:>7}: best sync match = {score}/{SYNC_LEN}")
    
    # Try also with lower threshold
    print(f"\n  With lower threshold ({noise_floor*1.5:.4f}):")
    for rate in symbol_rates:
        score, result = try_decode(ws, we, rate, noise_floor*1.5)
        if score > 30:
            print(f"  Rate {rate:>7}: best sync match = {score}/{SYNC_LEN}")

# Also try: the 30-32 ms sub-bursts themselves might BE the symbols
# (i.e., on/off keying where each key-on is one bit)
# At ~30 ms per bit: 33 bps
# This is very slow but possible for remote controls

# Or the sub-bursts could be frames with a fixed internal structure
print("\n=== Sub-burst structure analysis ===")
# Extract all sub-bursts from the best window
seg = envelope[ws:we]
sub_active = seg > threshold
sub_runs = []
i = 0
while i < len(sub_active):
    if sub_active[i]:
        j = i
        while j < len(sub_active) and sub_active[j]:
            j += 1
        if j - i > SR:  # > 1 ms
            sub_runs.append((i, j))
        i = j
    else:
        i += 1

durations = [(e-s)/SR*1000 for s,e in sub_runs]
gaps = []
for k in range(len(sub_runs)-1):
    gap = (sub_runs[k+1][0] - sub_runs[k][1]) / SR * 1000
    gaps.append(gap)

print(f"Sub-bursts: {len(sub_runs)}")
print(f"Durations: min={min(durations):.2f} ms, max={max(durations):.2f} ms, mean={np.mean(durations):.2f} ms")
print(f"Std dev: {np.std(durations):.2f} ms")
if gaps:
    print(f"Gaps: min={min(gaps):.2f} ms, max={max(gaps):.2f} ms, mean={np.mean(gaps):.2f} ms")

# Check if durations cluster into 2-3 groups (binary/ternary encoding)
if durations:
    hist, edges = np.histogram(durations, bins=30)
    print("\nDuration histogram:")
    for i in range(len(hist)):
        if hist[i] > 0:
            center = (edges[i] + edges[i+1])/2
            print(f"  {center:.1f} ms: {'*' * min(hist[i], 50)} ({hist[i]})")
