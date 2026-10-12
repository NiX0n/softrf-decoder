#!/usr/bin/env python3
"""
SoftRF FHSS-FSK demodulator with per-hop frequency tracking.

Strategy:
1. Detect signal bursts
2. For each burst, track the instantaneous frequency
3. Identify frequency hops (transitions between F0 and F1)
4. Demodulate each hop segment separately
5. Stitch the results together
"""
import numpy as np
from scipy.signal import hilbert
import sys

def detect_bursts(rms, threshold_factor=3.0):
    """Detect signal regions from RMS envelope."""
    baseline = np.median(rms)
    threshold = baseline * threshold_factor
    mask = rms > threshold
    
    # Find contiguous regions
    regions = []
    i = 0
    while i < len(mask):
        if mask[i]:
            start = i
            while i < len(mask) and mask[i]:
                i += 1
            regions.append((start, i))
        else:
            i += 1
    return regions

def estimate_instantaneous_frequency(samples, sr, window_size=1024):
    """
    Estimate instantaneous frequency using Hilbert transform.
    
    Returns:
        freqs: array of instantaneous frequencies (Hz)
        times: array of times (seconds)
    """
    # Apply Hilbert transform to get analytic signal (use real part)
    analytic = hilbert(samples.real)
    
    # Compute instantaneous phase
    phase = np.unwrap(np.angle(analytic))
    
    # Compute instantaneous frequency (derivative of phase)
    freqs = np.gradient(phase) / (2 * np.pi)
    
    # Time array
    times = np.arange(len(freqs)) / sr
    
    return freqs, times

def find_frequency_transitions(freqs, times, threshold_khz=50, min_duration_us=100):
    """
    Identify frequency hops (transitions between F0 and F1).
    
    Returns:
        hops: list of (start_time, end_time, mean_freq) tuples
    """
    # Convert to kHz
    freqs_khz = freqs / 1000
    
    # Find where the frequency changes significantly
    # Use a sliding window to compute the median frequency
    window = int(threshold_khz * 1000 / (freqs[-1] - freqs[0] + 1) * 100) if freqs[-1] != freqs[0] else 100
    window = min(window, len(freqs) // 10)
    
    # Compute rolling median
    if window >= 1:
        med_freqs = np.array([np.median(freqs_khz[i-window//2:i+window//2+1]) for i in range(window//2, len(freqs)-window//2)])
        med_times = times[window//2:len(freqs)-window//2]
    else:
        med_freqs = freqs_khz
        med_times = times
    
    # Find transitions
    hops = []
    i = 0
    while i < len(med_freqs):
        # Find the next significant frequency change
        j = i
        while j < len(med_freqs) and abs(med_freqs[j] - med_freqs[i]) < threshold_khz:
            j += 1
        
        # Add the hop
        if j > i:
            start_time = med_times[i]
            end_time = med_times[min(j, len(med_times)-1)]
            mean_freq = np.mean(med_freqs[i:j])
            hops.append((start_time, end_time, mean_freq))
        
        i = j
    
    return hops

def demodulate_fsk_segment(samples, sr, f0, f1):
    """
    Demodulate a single FSK segment given known F0 and F1 frequencies.
    
    Returns:
        bits: array of bits (0 or 1)
    """
    # Compute the instantaneous frequency
    freqs, times = estimate_instantaneous_frequency(samples, sr)
    
    # Threshold: if freq > (f0+f1)/2, it's a 1; otherwise it's a 0
    threshold = (f0 + f1) / 2
    
    # Convert to bits
    bits = np.where(freqs > threshold, 1, 0)
    
    # Remove consecutive duplicates (runs of same value)
    # This assumes the signal is FSK, not continuous
    bits_unique = []
    prev_bit = None
    for bit in bits:
        if bit != prev_bit:
            bits_unique.append(bit)
            prev_bit = bit
    
    return np.array(bits_unique)

def main():
    print("SoftRF FHSS-FSK Demodulator with Per-Hop Tracking")
    print("=" * 60)
    
    # Read the file
    filename = "../long_baseband_915000000Hz_15-01-19_12-10-2026.wav"
    with open(filename, 'rb') as f:
        header = f.read(44)
        actual_file_size = f.seek(0, 2)
    
    # Use actual file size
    data_size = actual_file_size - 44
    total_samples = data_size // 8
    
    print(f"File size: {actual_file_size} bytes")
    print(f"Total samples: {total_samples}")
    print(f"Duration: {total_samples / 20_000_000:.2f} seconds")
    
    # Detect bursts
    print("\nDetecting bursts...")
    
    # Read in chunks to detect bursts
    chunk_size = 20_000  # 1ms
    n_chunks = total_samples // chunk_size
    
    rms = np.empty(n_chunks)
    for i in range(n_chunks):
        with open(filename, 'rb') as f:
            f.seek(44 + i*chunk_size*8)
            chunk = f.read(chunk_size*8)
        
        payload = np.frombuffer(chunk, dtype=np.float32)
        n = len(payload) // 2
        I = payload[0::2][:n]
        Q = payload[1::2][:n]
        rms[i] = np.sqrt(np.mean(I**2 + Q**2))
    
    regions = detect_bursts(rms, threshold_factor=3.0)
    print(f"Found {len(regions)} signal regions")
    
    # Analyze each burst
    for i, (start, end) in enumerate(regions[:5]):  # First 5 bursts
        sample_offset = start * chunk_size
        n_samples = (end - start) * chunk_size
        
        # Read the burst
        with open(filename, 'rb') as f:
            f.seek(44 + sample_offset * 8)
            chunk = f.read(n_samples * 8)
        
        payload = np.frombuffer(chunk, dtype=np.float32)
        n = len(payload) // 2
        I = payload[0::2][:n]
        Q = payload[1::2][:n]
        samples = I + 1j*Q
        
        # Estimate instantaneous frequency
        freqs, times = estimate_instantaneous_frequency(samples, 20_000_000)
        
        # Find frequency transitions
        hops = find_frequency_transitions(freqs, times, threshold_khz=50)
        
        print(f"\n=== Burst {i} (t={start*chunk_size/20000:.0f}ms) ===")
        print(f"  Samples: {n}")
        print(f"  RMS: {np.sqrt(np.mean(np.abs(samples)**2)):.4f}")
        print(f"  Freq range: {np.min(freqs)/1000:.1f} to {np.max(freqs)/1000:.1f} kHz")
        print(f"  Hops detected: {len(hops)}")
        
        # Show first few hops
        for j, (t_start, t_end, mean_freq) in enumerate(hops[:10]):
            duration_ms = (t_end - t_start) * 1000
            print(f"    Hop {j}: {mean_freq/1000:+.1f} kHz, duration={duration_ms:.2f}ms")
    
    print("\n" + "=" * 60)
    print("Analysis complete.")

if __name__ == "__main__":
    main()
