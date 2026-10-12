#!/usr/bin/env python3
"""
OOK/ASK Demodulator Prototype v1.0
==================================

Purpose: Test if the OOK/ASK hypothesis is correct by thresholding the envelope
and looking for patterns in the resulting bitstream.

The signal in the capture appears to be OOK/ASK (amplitude-based) at ~769 ksym/s,
NOT the 2-FSK 100 kbps SoftRF legacy protocol. This script tests the OOK/ASK
hypothesis.

How it works:
1. Read the I/Q samples
2. Compute the envelope (magnitude)
3. Apply a threshold to get ON/OFF bits
4. Look for patterns (sync patterns, run lengths, etc.)

Usage:
    python3 OOK_Demodulator_v1.py [wav_file]
"""

import sys
import numpy as np
import os

# ============================================================================
# Configuration
# ============================================================================

def load_iq(wav_path):
    """Load I/Q samples from WAV file."""
    print(f"Loading {wav_path}...")
    file_size = os.path.getsize(wav_path)
    print(f"  File size: {file_size:,} bytes")

    with open(wav_path, 'rb') as f:
        header = f.read(44)
        print(f"  WAV header: {len(header)} bytes")
        samples = np.frombuffer(f.read(), dtype='<f4')
    print(f"  Total samples: {len(samples):,}")
    print(f"  I/Q pairs: {len(samples)//2:,}")

    if len(samples) % 2 != 0:
        samples = samples[:-1]
        print(f"  (dropped last odd sample)")

    return samples

def analyze_ook(samples, max_samples=1_000_000):
    """
    Analyze the OOK/ASK signal.
    """
    N = min(len(samples)//2, max_samples)
    I = samples[0:2*N:2].copy()
    Q = samples[1:2*N:2].copy()
    mag = np.hypot(I, Q)

    print("\n=== OOK/ASK Analysis ===")
    print(f"Samples analyzed: {N:,}")
    print(f"Mean magnitude: {mag.mean():.6f}")
    print(f"Max magnitude: {mag.max():.6f}")
    print(f"Min magnitude: {mag.min():.6f}")
    print(f"Std/mean: {mag.std()/mag.mean():.4f}")

    # Try different thresholds
    for threshold_factor in [0.5, 1.0, 1.5, 2.0]:
        threshold = mag.mean() * threshold_factor
        on = mag > threshold
        on_fraction = on.mean()

        # Find bursts
        burst_starts = np.where(on & ~np.roll(on, 1))[0]
        burst_ends = np.where(~on & np.roll(on, 1))[0]

        # Calculate burst durations
        if len(burst_starts) > 0 and len(burst_ends) > 0:
            durations = burst_ends[:len(burst_starts)] - burst_starts[:len(burst_ends)]
            mean_duration = durations.mean() if len(durations) > 0 else 0
            min_duration = durations.min() if len(durations) > 0 else 0
            max_duration = durations.max() if len(durations) > 0 else 0

            print(f"\nThreshold {threshold:.4f} (factor {threshold_factor}):")
            print(f"  ON fraction: {on_fraction:.3f}")
            print(f"  Bursts: {len(burst_starts)}")
            print(f"  Mean burst duration: {mean_duration:.1f} samples ({mean_duration/20e6:.4f} ms)")
            print(f"  Min burst duration: {min_duration:.1f} samples ({min_duration/20e6:.4f} ms)")
            print(f"  Max burst duration: {max_duration:.1f} samples ({max_duration/20e6:.4f} ms)")

    # Look for bit patterns at different symbol rates
    print("\n=== Symbol Rate Analysis ===")
    for symbol_rate in [769_000, 1_000_000, 1_500_000, 2_000_000]:
        samples_per_symbol = int(20_000_000 / symbol_rate)
        print(f"\nSymbol rate {symbol_rate//1000} ksym/s ({samples_per_symbol} samples/symbol):")

        # Downsample to symbol rate
        n_symbols = N // samples_per_symbol
        if n_symbols < 10:
            print(f"  (too few symbols: {n_symbols})")
            continue

        # For each symbol, take the mean magnitude
        symbol_values = []
        for i in range(n_symbols):
            start = i * samples_per_symbol
            end = start + samples_per_symbol
            if end <= N:
                symbol_values.append(mag[start:end].mean())
        symbol_values = np.array(symbol_values)

        # Threshold the symbol values
        threshold = symbol_values.mean() * 1.5
        bits = (symbol_values > threshold).astype(int)

        # Analyze the bit pattern
        bit_count = bits.sum()
        total_bits = len(bits)
        print(f"  Symbols: {total_bits}")
        print(f"  ON bits: {bit_count} ({bit_count/total_bits:.3f})")
        print(f"  First 100 bits: {bits[:100].astype(str).join('')}")

def main():
    # Get WAV file path
    if len(sys.argv) > 1:
        wav_path = sys.argv[1]
    else:
        wav_path = "baseband_915000000Hz_203524_03-10-2026.wav"

    if not os.path.exists(wav_path):
        print(f"Error: {wav_path} not found")
        sys.exit(1)

    # Load samples
    samples = load_iq(wav_path)

    # Analyze
    analyze_ook(samples)

    print("\n=== Analysis Complete ===")
    print("Next steps:")
    print("  1. Look for sync patterns in the bitstream")
    print("  2. Try different symbol rates")
    print("  3. Check if the bitstream matches any known protocol")
    print("  4. Verify receiver center frequency (if OOK is actually FSK with wrong tuning)")

if __name__ == "__main__":
    main()
