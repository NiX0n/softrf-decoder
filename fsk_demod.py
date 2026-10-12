#!/usr/bin/env python3
"""
SoftRF FSK demodulator v2 — robust burst detection.

Key fixes:
  1. Burst detection uses peak-based threshold (noise floor is high)
  2. FSK frequency detection uses longer windows for better resolution
  3. Matched filter demodulation at detected tones
  4. Manchester decode with syncword search
"""

import numpy as np
from scipy.io import wavfile
from scipy.ndimage import maximum_filter

WAV_PATH = "../baseband_915000000Hz_20-35-24_03-10-2026.wav"
FS = 20_000_000
SAMPLES_PER_BIT = 200
SYNCWORD = bytes([0x55, 0x99, 0xA5, 0xA9, 0x55, 0x66, 0x65, 0x96])


def find_bursts(samples, min_len_samples=100_000):
    """Find bursts using peak-based threshold."""
    env = np.abs(samples)

    # Use a large window for smoothing
    k = 1000
    kernel = np.ones(k) / k
    env_smooth = np.convolve(env, kernel, mode='same')

    # Find the peak
    peak_val = np.max(env_smooth)
    peak_idx = np.argmax(env_smooth)

    # Threshold: 20% of peak
    thresh = peak_val * 0.20

    above = env_smooth > thresh

    runs = []
    in_run = False
    start = 0
    for i, v in enumerate(above):
        if v and not in_run:
            start = i
            in_run = True
        elif not v and in_run:
            if i - start >= min_len_samples:
                runs.append((start, i - start))
            in_run = False
    if in_run and len(above) - start >= min_len_samples:
        runs.append((start, len(above) - start))

    return runs


def find_fsk_freqs(burst, fs):
    """Find two FSK tones via FFT with longer windows."""
    # Use 4000-sample windows (200us) for better frequency resolution
    window = 4000
    n = min(25, len(burst) // window)
    if n < 4:
        # Fall back to smaller windows
        window = 2000
        n = min(50, len(burst) // window)

    freqs = []
    for i in range(n):
        w = burst[i * window: (i + 1) * window]
        if len(w) < 1000:
            break
        w = w * np.hanning(len(w))
        fft_size = 8192
        fft = np.fft.fftshift(np.fft.fft(w, fft_size))
        mag = np.abs(fft)
        peak_idx = np.argmax(mag)
        peak_freq = (peak_idx - fft_size // 2) * fs / fft_size
        freqs.append(peak_freq)

    freqs = np.array(freqs)
    if len(freqs) < 4:
        return None, None

    # K-means k=2
    f0 = freqs[np.argmin(freqs)]
    f1 = freqs[np.argmax(freqs)]
    for _ in range(30):
        d0 = np.abs(freqs - f0)
        d1 = np.abs(freqs - f1)
        mask0 = d0 < d1
        if np.sum(mask0) == 0 or np.sum(~mask0) == 0:
            break
        f0_new = np.mean(freqs[mask0])
        f1_new = np.mean(freqs[~mask0])
        if abs(f0_new - f0) < 50 and abs(f1_new - f1) < 50:
            break
        f0, f1 = f0_new, f1_new

    return f0, f1


def fsk_demodulate(burst, f0, f1, fs, samples_per_bit):
    """Matched-filter FSK demodulation."""
    n_bits = len(burst) // samples_per_bit
    if n_bits < 10:
        return np.array([]), np.array([])

    t = np.arange(samples_per_bit)
    ref0 = np.exp(1j * 2 * np.pi * f0 * t / fs)
    ref1 = np.exp(1j * 2 * np.pi * f1 * t / fs)

    scores = np.zeros(n_bits)
    for i in range(n_bits):
        seg = burst[i * samples_per_bit: (i + 1) * samples_per_bit]
        score0 = np.abs(np.vdot(seg, ref0))
        score1 = np.abs(np.vdot(seg, ref1))
        scores[i] = score1 / (score0 + score1)

    bits = (scores > 0.5).astype(int)
    return bits, scores


def manchester_decode(bits):
    """Try Manchester decode at various offsets, return best."""
    best = None
    best_score = -1

    for offset in range(0, 200, 20):  # Try every 10 samples
        for invert in [False, True]:
            b = (1 - bits) if invert else bits
            if len(b) < 100:
                continue

            m = []
            for i in range(offset, len(b) - 1, 2):
                if (b[i] == 1 and b[i + 1] == 0):
                    m.append(1)
                elif (b[i] == 0 and b[i + 1] == 1):
                    m.append(0)
                else:
                    m.append(-1)
            m = np.array(m)

            byte_list = []
            for i in range(0, len(m) - 7, 8):
                if np.any(m[i:i + 8] == -1):
                    break
                val = 0
                for bit in m[i:i + 8]:
                    val = (val << 1) | bit
                byte_list.append(val)
            if len(byte_list) < 4:
                continue
            frame = bytes(byte_list)

            sync_count = sum(1 for i in range(len(frame) - 7) if frame[i:i + 8] == SYNCWORD)
            score = sync_count * 10000 + len(frame)
            if score > best_score:
                best_score = score
                best = {
                    'offset': offset,
                    'invert': invert,
                    'sync_count': sync_count,
                    'frame': frame,
                }

    return best


def crc16_nrf905(data):
    """NRF905 CRC-16 (poly=0x1021, init=0xFFFF)."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc


def main():
    print("=== SoftRF FSK Demodulator v2 ===\n")

    sr, data = wavfile.read(WAV_PATH)
    print(f"Loaded: {sr} Hz, {len(data)} samples")

    iq = data.astype(np.complex64).reshape(-1, 2)
    samples = iq[:, 0] + 1j * iq[:, 1]
    print(f"I/Q: {len(samples)} samples\n")

    # Envelope stats
    env = np.abs(samples)
    print(f"Envelope: max={np.max(env):.4f}, mean={np.mean(env):.4f}, "
          f"std={np.std(env):.4f}, min={np.min(env):.4f}")
    print(f"Top 1%: {np.percentile(env, 99):.4f}")
    print(f"Top 0.1%: {np.percentile(env, 99.9):.4f}\n")

    bursts = find_bursts(samples, min_len_samples=100_000)
    print(f"Found {len(bursts)} significant bursts (>5ms):")
    for i, (start, length) in enumerate(bursts):
        print(f"  {i}: start={start}, len={length} ({length / FS * 1e3:.1f} ms)")

    if not bursts:
        print("\nNo significant bursts found. Trying lower threshold...")
        # Try 10% of peak
        def find_bursts_low(samples, min_len_samples=100_000):
            env = np.abs(samples)
            k = 1000
            kernel = np.ones(k) / k
            env_smooth = np.convolve(env, kernel, mode='same')
            peak_val = np.max(env_smooth)
            thresh = peak_val * 0.10
            above = env_smooth > thresh
            runs = []
            in_run = False
            start = 0
            for i, v in enumerate(above):
                if v and not in_run:
                    start = i
                    in_run = True
                elif not v and in_run:
                    if i - start >= min_len_samples:
                        runs.append((start, i - start))
                    in_run = False
            if in_run and len(above) - start >= min_len_samples:
                runs.append((start, len(above) - start))
            return runs

        bursts = find_bursts_low(samples)
        print(f"Found {len(bursts)} bursts with lower threshold:")
        for i, (start, length) in enumerate(bursts):
            print(f"  {i}: start={start}, len={length} ({length / FS * 1e3:.1f} ms)")

    results = []
    for bi, (start, length) in enumerate(bursts):
        print(f"\n--- Burst {bi} ({length / FS * 1e3:.1f} ms) ---")
        burst = samples[start:start + length]

        f0, f1 = find_fsk_freqs(burst, FS)
        if f0 is None:
            print("  SKIPPED: FSK freq detection failed")
            continue
        print(f"  F0: {f0 / 1e3:+.1f} kHz, F1: {f1 / 1e3:+.1f} kHz, sep={abs(f1 - f0) / 1e3:.1f} kHz")

        bits, scores = fsk_demodulate(burst, f0, f1, FS, SAMPLES_PER_BIT)
        if len(bits) < 10:
            print("  SKIPPED: too few bits")
            continue

        ones = np.sum(bits == 1)
        zeros = np.sum(bits == 0)
        print(f"  Bits: {len(bits)} (1s:{ones}, 0s:{zeros})")
        print(f"  Pattern: {''.join(map(str, bits[:64]))}{'...' if len(bits) > 64 else ''}")

        result = manchester_decode(bits)
        if result:
            frame = result['frame']
            print(f"  Manchester: offset={result['offset']}, invert={result['invert']}, syncs={result['sync_count']}")
            print(f"  Frame ({len(frame)} bytes): {' '.join(f'{b:02X}' for b in frame[:48])}{'...' if len(frame) > 48 else ''}")

            if len(frame) >= 4:
                calc = crc16_nrf905(frame[:-2])
                stored = (frame[-2] << 8) | frame[-1]
                ok = calc == stored
                print(f"  CRC16: {'PASS' if ok else 'FAIL'} (calc=0x{calc:04X}, stored=0x{stored:04X})")

            results.append({
                'burst': bi,
                'f0': f0,
                'f1': f1,
                'bits': bits,
                'manchester': result,
            })
        else:
            print("  No valid Manchester decode")

    print(f"\n=== Summary ===")
    print(f"Bursts processed: {len(results)}/{len(bursts)}")
    for r in results:
        m = r['manchester']
        print(f"  Burst {r['burst']}: {m['sync_count']} syncword(s), {len(m['frame'])} bytes")


if __name__ == "__main__":
    main()
