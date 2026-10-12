#!/usr/bin/env python3
"""Deep signal analysis — what IS this signal actually doing?"""
import numpy as np, scipy.signal

def load_wav(path):
    with open(path, 'rb') as f:
        data = f.read()
    # Parse WAV: skip header until first data chunk
    i = 12
    fmt = None
    data_off = None
    while i < len(data) - 4:
        cid = data[i:i+4].decode('ascii', errors='ignore')
        sz = int.from_bytes(data[i+4:i+8], 'little')
        if cid == 'fmt ':
            fmt = data[i+8:i+8+16]
            i += 8 + sz
        elif cid == 'data':
            data_off = i + 8
            break
        else:
            i += 8 + sz
    if fmt is None or data_off is None:
        raise ValueError("no fmt/data")
    nch = int.from_bytes(fmt[2:4], 'little')
    sr = int.from_bytes(fmt[4:8], 'little')
    bps = int.from_bytes(fmt[14:16], 'little')
    if bps == 32 and nch == 1:
        raw = np.frombuffer(data[data_off:], np.float32).copy()
    else:
        raw = np.frombuffer(data[data_off:], np.int16).astype(np.float32) / 32768
    return raw, sr

raw, FS = load_wav("../baseband_915000000Hz_20-35-24_03-10-2026.wav")
iq = raw[::2] + 1j * raw[1::2]

# Take the first burst
start, end = 177730, 285899
burst = iq[start:end]
n = len(burst)
print(f"Burst 0: {n} samples = {n/FS*1000:.2f} ms")
print(f"Envelope: max={np.abs(burst).max():.4f}, mean={np.abs(burst).mean():.4f}")

# Plot the instantaneous frequency over time
win = 4000
print("\nInstantaneous frequency trace (kHz) over burst:")
print("Sample    Freq(kHz)")
for i in range(0, n - win, 200):
    seg = burst[i:i+win]
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    f = np.fft.rfftfreq(len(seg), 1/FS)[np.argmax(spec)]
    bar = " " * max(0, int((f+10000)/200)) + "#"
    print(f"{i:6d}  {f/1000:+9.1f}  {bar[:120]}")

# Envelope analysis
env = np.abs(burst)
print(f"\nEnvelope statistics:")
print(f"  Mean: {env.mean():.4f}")
print(f"  Median: {np.median(env):.4f}")
print(f"  10th percentile: {np.percentile(env, 10):.4f}")
print(f"  90th percentile: {np.percentile(env, 90):.4f}")
print(f"  Histogram (10 bins):")
hist, edges = np.histogram(env, bins=10)
for i, (count, edge) in enumerate(zip(hist, edges[:-1])):
    print(f"    [{edges[i]:.4f} - {edges[i+1]:.4f}]: {count} ({count/len(env)*100:.1f}%)")

# Phase trace
phase = np.unwrap(np.angle(burst))
print(f"\nPhase statistics:")
print(f"  Range: {phase.max()-phase.min():.1f} rad = {(phase.max()-phase.min())/(2*np.pi):.1f} cycles")
dphase = np.diff(phase)
print(f"  Phase step mean: {np.mean(dphase):.4f} rad/sample = {np.mean(dphase)*FS/(2*np.pi)/1000:.1f} kHz")
print(f"  Phase step std: {np.std(dphase):.4f} rad/sample = {np.std(dphase)*FS/(2*np.pi)/1000:.1f} kHz")
print(f"  Phase step max: {np.max(np.abs(dphase)):.4f} rad/sample")

# Check: is this OOK? Look at the envelope in 200-sample windows
print(f"\nEnvelope per bit-slot (200 samples):")
bits = []
for i in range(0, n - 200, 200):
    bits.append(np.mean(np.abs(burst[i:i+200])))
bits = np.array(bits)
print(f"  Mean envelope per slot: {bits.mean():.4f}")
print(f"  Std envelope per slot: {bits.std():.4f}")
# OOK would show bimodal distribution
bimodal_threshold = (bits.max() + bits.min()) / 2
n_on = np.sum(bits > bimodal_threshold)
n_off = np.sum(bits <= bimodal_threshold)
print(f"  Bimodal check (threshold={bimodal_threshold:.4f}): ON={n_on}, OFF={n_off}")
print(f"  Ratio ON/OFF: {n_on/max(1,n_off):.1f}")
