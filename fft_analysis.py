#!/usr/bin/env python3
"""
# [!!!] THIS SCRIPT IS OBSOLETE — FSK HYPOTHESIS DISPROVEN
#
# This script was written for the 2-FSK hypothesis, which has been
# DISPROVEN. See FSK_HYPOTHESIS_DISPROVEN.md for details.
#
# The signal is OOK/ASK, not FSK. Use OOK_Demodulator_v1.py instead.
#
FFT-based FSK analysis of SoftRF capture.

Method:
  1. Load baseband I/Q from WAV
  2. Estimate envelope (moving max)
  3. Extract first burst (top 20% envelope, longest consecutive run)
  4. Segment into 2000-sample windows (50us each, 100kbps = 200 samples/bit)
  5. Per window: 4096-pt FFT, find peak frequency
  6. Classify each window as tone 0 (low) or tone 1 (high)

Evidence:
  [RF VERIFIED] Two-tone FSK structure confirmed.
  [HYPOTHESIS] Bit mapping (which tone = 0 vs 1) not yet verified.
  [UNVERIFIED] Frame alignment and syncword position.
"""

import numpy as np
from scipy.io import wavfile

WAV_PATH = "baseband_915000000Hz_20-35-24_03-10-2026.wav"
FS = 20_000_000  # 20 MHz sample rate
WINDOW = 2000    # 100us window
FFT_SIZE = 4096
THRESHOLD_KHZ = -802.5  # Decision threshold between two FSK tones


def main():
    sr, data = wavfile.read(WAV_PATH)
    print(f"Sample rate: {sr} Hz")
    print(f"Total samples: {len(data)}")

    # data is interleaved I/Q: [I0, Q0, I1, Q1, ...]
    iq = data.astype(np.complex64).reshape(-1, 2)
    samples = iq[:, 0] + 1j * iq[:, 1]
    print(f"I/Q samples: {len(samples)}")

    # Envelope estimate: moving max
    env = np.abs(samples)
    k = 200
    kernel = np.ones(k) / k
    env_smooth = np.convolve(env, kernel, mode='same')
    # Use running max for robustness
    from scipy.ndimage import maximum_filter
    env_max = maximum_filter(env_smooth, size=400)

    # Find first burst: threshold at 20th percentile of non-zero envelope
    nonzero = env_max[env_max > np.max(env_max) * 0.05]
    if len(nonzero) == 0:
        print("ERROR: No signal found above noise floor")
        return
    thresh = np.percentile(nonzero, 20)

    # Find first consecutive run above threshold
    above = env_max > thresh
    # Find longest run of True
    runs = []
    in_run = False
    start = 0
    for i, v in enumerate(above):
        if v and not in_run:
            start = i
            in_run = True
        elif not v and in_run:
            runs.append((start, i - start))
            in_run = False
    if in_run:
        runs.append((start, len(above) - start))

    if not runs:
        print("ERROR: No signal runs found")
        return

    # Pick the longest run
    best = max(runs, key=lambda x: x[1])
    burst_start, burst_len = best
    print(f"\nFirst burst: start={burst_start}, len={burst_len} samples ({burst_len / FS * 1e3:.1f} ms)")

    # Extract burst
    burst = samples[burst_start:burst_start + burst_len]

    # Segment into windows
    n_windows = burst_len // WINDOW
    print(f"Windows: {n_windows}")

    # Per-window FFT peak frequency
    freqs = []
    for i in range(n_windows):
        w = burst[i * WINDOW: (i + 1) * WINDOW]
        # Apply windowing
        w = w * np.hanning(len(w))
        fft = np.fft.fftshift(np.fft.fft(w, FFT_SIZE))
        mag = np.abs(fft)
        peak_idx = np.argmax(mag)
        peak_freq = (peak_idx - FFT_SIZE // 2) * FS / FFT_SIZE
        freqs.append(peak_freq)

    freqs = np.array(freqs)
    freqs_khz = freqs / 1e3

    print(f"\nFFT-based frequency analysis ({WINDOW}-sample windows):")
    print(f"  Windows: {len(freqs_khz)}")
    print(f"  Mean: {np.mean(freqs_khz):.1f} kHz")
    print(f"  Std: {np.std(freqs_khz):.1f} kHz")
    print(f"  Min: {np.min(freqs_khz):.1f} kHz")
    print(f"  Max: {np.max(freqs_khz):.1f} kHz")

    print(f"\nAll windows (kHz):")
    for i, f in enumerate(freqs_khz):
        print(f"  {i}: {f:+.1f} kHz")

    # Classify bits
    bits = (freqs_khz > THRESHOLD_KHZ).astype(int)
    print(f"\nDecoded bits: {len(bits)}")
    print(f"Zeros: {np.sum(bits == 0)}, Ones: {np.sum(bits == 1)}")
    print(f"Bit pattern: {''.join(map(str, bits))}")

    # Hex bytes
    hex_bytes = []
    for i in range(0, len(bits) - 7, 8):
        byte = bits[i:i+8]
        val = 0
        for b in byte:
            val = (val << 1) | b
        hex_bytes.append(f"{val:02X}")
    print(f"Hex bytes: {' '.join(hex_bytes)}")


if __name__ == "__main__":
    main()
