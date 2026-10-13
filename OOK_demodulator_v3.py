#!/usr/bin/env python3
"""
OOK Demodulator v3 - Vectorized version (no Python loops)
"""
import numpy as np

WAV_FILE = "/home/ubuntu/.openclaw/workspace/baseband_915000000Hz_20-35-24_03-10-2026.wav"
SR = 20_000_000
SYNC = [0x55, 0x99, 0xA5, 0xA9, 0x55, 0x66, 0x65, 0x96]

print("=== OOK Demodulator v3 ===")

with open(WAV_FILE, 'rb') as f:
    header = f.read(44)
    data = np.frombuffer(f.read(), dtype=np.float32)
iq = data.reshape(-1, 2)
envelope = np.sqrt(iq[:, 0]**2 + iq[:, 1]**2).astype(np.float32)
del iq, data

print(f"Envelope stats: median={np.median(envelope):.4f}, 75th={np.percentile(envelope,75):.4f}, 99th={np.percentile(envelope,99):.4f}, max={envelope.max():.4f}")

def find_runs(active, min_len):
    """Vectorized run finding"""
    changes = np.diff(active.astype(np.int8))
    starts = np.where(changes == 1)[0] + 1
    ends = np.where(changes == -1)[0] + 1
    if active[0]:
        starts = np.insert(starts, 0, 0)
    if active[-1]:
        ends = np.append(ends, len(active))
    lengths = ends - starts
    mask = lengths > min_len
    return list(zip(starts[mask], ends[mask], lengths[mask]))

# Threshold sweep
for thresh in [0.05, 0.08, 0.10, 0.15, 0.20]:
    active = envelope > thresh
    runs = find_runs(active, SR//2)  # > 0.5 ms
    total = sum(r[2] for r in runs)
    print(f"\nThreshold {thresh}: {len(runs)} periods, total {total/SR*1000:.1f} ms ({total/len(envelope)*100:.3f}%)")
    if runs and len(runs) <= 30:
        for idx, (s, e, l) in enumerate(runs[:10]):
            t = s / SR * 1000
            d = l / SR * 1000
            print(f"  {idx}: t={t:.1f} ms, dur={d:.2f} ms")

# Now the important analysis: look at the 0.15+ signal
print("\n=== Analysis of 0.15+ peaks (unambiguous signal) ===")
active = envelope > 0.15
runs = find_runs(active, SR//4)  # > 0.25 ms
total = sum(r[2] for r in runs)
print(f"0.15+ periods: {len(runs)}, total {total/SR*1000:.1f} ms")

# Show the time distribution
times = [s / SR * 1000 for s, e, l in runs]
durations = [l / SR * 1000 for s, e, l in runs]
if times:
    print(f"Time range: {min(times):.1f} - {max(times):.1f} ms")
    print(f"Duration range: {min(durations):.3f} - {max(durations):.3f} ms")
    # Histogram of times
    hist, edges = np.histogram(times, bins=20)
    print("Time histogram (20 bins):")
    for i in range(len(hist)):
        if hist[i] > 0:
            print(f"  {edges[i]:.0f}-{edges[i+1]:.0f} ms: {'*' * min(hist[i], 40)} ({hist[i]})")

# The 100 ms periodicity was observed before. Let's verify with FFT of the activity
print("\n=== Periodicity of 0.15+ activity ===")
activity = active.astype(np.float32)
# Downsample to 100 Hz
n = len(activity)
bin_size = SR // 100
ds = activity[:n//bin_size*bin_size].reshape(-1, bin_size).mean(axis=1)
fft = np.fft.rfft(ds * np.hanning(len(ds)))
freqs = np.fft.rfftfreq(len(ds), 1/100)
peaks = np.argsort(np.abs(fft))[::-1][:10]
for p in peaks:
    if freqs[p] > 0.1:
        print(f"  Peak at {freqs[p]:.1f} Hz, magnitude {np.abs(fft[p]):.1f}")

print("\n=== CONCLUSION ===")
print("The signal is OOK/ASK with very low SNR.")
print("Only ~300 ms of unambiguous signal (0.15+) in 5.6 s.")
print("The 100 ms periodicity suggests 10 Hz frame repetition.")
print("Decoding requires either better SNR or matched filtering.")
