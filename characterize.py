"""Thorough signal characterization.

The user confirms the signal IS present and correlated to TX power.
So this IS the signal. Let me figure out what modulation/format it actually is.

Key questions:
1. What's the actual signal bandwidth?
2. Is it FSK, ASK, PSK, or something else?
3. What's the symbol rate?
4. What's the structure (bursts, continuous, etc.)?
"""
import numpy as np
import os

fpath = '/home/ubuntu/.openclaw/workspace/baseband_915000000Hz_20-35-24_03-10-2026.wav'
size = os.path.getsize(fpath)
print(f"File size: {size/1e6:.1f} MB")

with open(fpath, 'rb') as f:
    f.read(44)
    buf = np.fromfile(f, dtype=np.float32)

print(f"Total samples: {len(buf)/2:.0f} I/Q pairs")
print(f"Duration at 20 MS/s: {len(buf)/2/20e6:.2f}s")

iq = buf.reshape(-1, 2)
N = len(iq)

# Analyze in chunks to find where the signal is
print(f"\n=== Chunk-by-chunk analysis (1M samples each) ===")
print(f"{'Chunk':>6} {'I_mean':>10} {'I_std':>10} {'Q_mean':>10} {'Q_std':>10} {'Amp_mean':>10} {'Amp_std':>10} {'Phase_std':>10}")

for chunk in range(min(N // 1_000_000, 20)):
    start = chunk * 1_000_000
    end = start + 1_000_000
    I = iq[start:end, 0].astype(np.float64)
    Q = iq[start:end, 1].astype(np.float64)
    amp = np.sqrt(I**2 + Q**2)
    phase = np.arctan2(Q, I)
    print(f"{chunk:>6} {I.mean():>10.4f} {I.std():>10.4f} {Q.mean():>10.4f} {Q.std():>10.4f} {amp.mean():>10.4f} {amp.std():>10.4f} {np.degrees(phase.std()):>10.1f}")

# Check: is there a signal BURST in there?
# Look at the amplitude envelope
print(f"\n=== Amplitude envelope ===")
amp_full = np.sqrt(iq[:, 0]**2 + iq[:, 1]**2)

# Smooth with moving average
window = 100_000
amp_smooth = np.convolve(amp_full, np.ones(window)/window, mode='valid')
print(f"Envelope (smoothed, {window} samples):")
print(f"  min={amp_smooth.min():.4f} max={amp_smooth.max():.4f} mean={amp_smooth.mean():.4f}")

# Find where amplitude is high (signal present)
threshold = amp_smooth.mean() + 2 * amp_smooth.std()
signal_regions = np.where(amp_smooth > threshold)[0]
if len(signal_regions) > 0:
    print(f"  Signal regions: {len(signal_regions)} chunks")
    # Find contiguous regions
    diffs = np.diff(signal_regions)
    breaks = np.where(diffs > 1)[0]
    regions = []
    start = signal_regions[0]
    for b in breaks:
        regions.append((start, signal_regions[b]))
        start = signal_regions[b+1]
    regions.append((start, signal_regions[-1]))
    for i, (s, e) in enumerate(regions[:10]):
        print(f"  Region {i}: samples {s*window} to {(e+1)*window} = {(e-s+1)*window/20e6:.3f}s")
else:
    print(f"  No clear signal regions found above threshold {threshold:.4f}")

# Check the frequency content
print(f"\n=== Frequency content (FFT of first 1M samples) ===")
I = iq[:1_000_000, 0].astype(np.float64)
Q = iq[:1_000_000, 1].astype(np.float64)
analytic = I + 1j*Q
fft = np.fft.fftshift(np.fft.fft(analytic))
freqs = np.fft.fftshift(np.fft.fftfreq(1_000_000, d=1/20e6))
mag = np.abs(fft)

# Find top peaks
top_idx = np.argsort(mag)[::-1][:10]
print("Top 10 frequency peaks:")
for idx in sorted(top_idx):
    print(f"  {freqs[idx]/1000:>10.1f} kHz: {mag[idx]:>10.1f}")

# Check if the signal is at DC or offset
dc_mag = mag[len(mag)//2]
print(f"\n  DC: {dc_mag:.1f}")

# Check the spectrum shape
# Is it a wideband signal or narrowband?
bandwidth = np.sum(mag > 0.1 * mag.max())
print(f"  Effective bandwidth (10% of max): {bandwidth * 20e6/1_000_000 / 1000:.1f} kHz")

# Check: is the signal AM (amplitude modulated) or FM (frequency modulated)?
# If AM: amplitude varies with data
# If FM: phase varies with data, amplitude is constant
print(f"\n=== AM vs FM check ===")
amp_var = amp_full.std() / amp_full.mean()
print(f"  Amplitude variation: {amp_var*100:.1f}% (high = AM, low = FM)")

phase = np.arctan2(iq[:, 1].astype(np.float64), iq[:, 0].astype(np.float64))
phase_diff = np.diff(phase)
# Unwrap
phase_diff_wrapped = (phase_diff + np.pi) % (2*np.pi) - np.pi
phase_var = phase_diff_wrapped.std()
print(f"  Phase variation: {np.degrees(phase_var):.1f} deg/sample")

# Check the Q/I ratio
iq_ratio = np.abs(Q.astype(np.float64)) / (np.abs(I.astype(np.float64)) + 1e-10)
print(f"  |Q/I| ratio: mean={iq_ratio.mean():.3f} median={np.median(iq_ratio):.3f}")

# Check: is the signal real (Q=0) or complex?
q_zero_frac = np.sum(np.abs(Q.astype(np.float64)) < 0.001) / len(Q)
print(f"  Q≈0 fraction: {q_zero_frac*100:.1f}%")
