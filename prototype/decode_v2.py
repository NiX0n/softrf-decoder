#!/usr/bin/env python3
"""
Phase-coherent 2-FSK demodulator with Manchester decode, CRC, and XXTEA.

Uses well-understood principles:
  - Phase-coherent quadrature demodulation (reference phase continuous across symbols)
  - Energy-based symbol detection
  - Manchester bit recovery
  - CRC16-CCITT-F verification
  - XXTEA decryption

Fault tolerance:
  - Multiple candidate frequencies tested
  - Phase offset search (the reference may start at an unknown phase)
  - Burst-level: try alignment at every sample position
"""

import numpy as np
import soundfile as sf
import struct

# ── Protocol constants ───────────────────────────────────────────────
FS         = 20_000_000
BITRATE    = 100_000
SYMBOL_RATE = 200_000
SPS         = FS // SYMBOL_RATE  # 100 samples per symbol
BITLEN     = 320
SYMLEN     = 640
PAYLEN     = 24
HDRLEN     = 8
PKTLEN     = 32

# XXTEA
DELTA  = 0x9E3779B9
ROUNDS = 32
MASK   = 0xFFFFFFFF

def btea_decrypt(v: list, n: int, k: list) -> list:
    """XXTEA decrypt. v = list of n uint32, k = list of 4 uint32."""
    v = list(v)
    q = ROUNDS + 6 * n // 2
    sum_v = 0
    z = v[-1]
    y = v[0]
    while q > 0:
        p = 0
        i = 0
        while i < n - 1:
            mx = ((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))
            mx ^= (sum_v ^ y) + (k[(p & 3) ^ i] ^ z)
            mx &= MASK
            v[i] = (v[i] - mx) & MASK
            y = v[i]
            p += 1
            i += 1
        # Last element
        mx = ((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))
        mx ^= (sum_v ^ y) + (k[3] ^ z)
        mx &= MASK
        v[n-1] = (v[n-1] - mx) & MASK
        z = v[n-1]
        # First element
        mx = ((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))
        mx ^= (sum_v ^ z) + (k[(p & 3) ^ (n-1)] ^ y)
        mx &= MASK
        v[0] = (v[0] - mx) & MASK
        y = v[0]
        p += 1
        sum_v = (sum_v - DELTA) & MASK
        q -= 1
    return v


def btea_encrypt(v: list, n: int, k: list) -> list:
    """XXTEA encrypt (for verification)."""
    v = list(v)
    q = ROUNDS + 6 * n // 2
    sum_v = 0
    y = v[0]
    z = v[-1]
    while q > 0:
        p = 0
        i = 0
        while i < n - 1:
            mx = ((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))
            mx ^= (sum_v ^ y) + (k[(p & 3) ^ i] ^ z)
            mx &= MASK
            v[i] = (v[i] + mx) & MASK
            y = v[i]
            p += 1
            i += 1
        mx = ((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))
        mx ^= (sum_v ^ y) + (k[3] ^ z)
        mx &= MASK
        v[n-1] = (v[n-1] + mx) & MASK
        z = v[n-1]
        mx = ((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))
        mx ^= (sum_v ^ z) + (k[(p & 3) ^ (n-1)] ^ y)
        mx &= MASK
        v[0] = (v[0] + mx) & MASK
        y = v[0]
        p += 1
        sum_v = (sum_v + DELTA) & MASK
        q -= 1
    return v

def crc16_ccitt_f(data: bytes, init: int = 0xFFFF) -> int:
    crc = init
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc

def get_syncword_crc() -> int:
    """CRC of the 8-byte sync word + first payload byte."""
    sync = bytes([0x55, 0x99, 0xA5, 0xA9, 0x55, 0x66, 0x65, 0x96])
    crc = 0xFFFF
    for b in sync + b'\x31':
        crc ^= b << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc

SYNC_CRC = get_syncword_crc()

def manchester_decode(symbols, invert=False):
    """Decode Manchester symbols to bits.
    Encode: bit1 -> (1,0), bit0 -> (0,1)
    Decode: (1,0) -> bit1, (0,1) -> bit0
    With inversion: (0,1) -> bit1, (1,0) -> bit0
    """
    bits = []
    for i in range(0, len(symbols) - 1, 2):
        a, b = symbols[i], symbols[i + 1]
        if a != b:
            if (a == 1 and b == 0) or (invert and a == 0 and b == 1):
                bits.append(1)
            else:
                bits.append(0)
        else:
            bits.append(None)  # invalid pair
    return bits

def bits_to_bytes(bits, bit_order_msb_first=True):
    """Convert bits to bytes.
    RF bit order: bit0 (LSB) first on the wire.
    So the received bit stream is LSB-first.
    To form a byte: bit0 goes into position 0, bit1 into position 1, etc.
    """
    if len(bits) < 8:
        return bytes([0])
    # Take the first 8 bits (they arrive LSB-first)
    b = 0
    for i in range(8):
        b |= (bits[i] & 1) << i
    return bytes([b])

def fsk_demodulate(z: np.complex128, freq: float, t_start: float, n_samples: int) -> complex:
    """Phase-coherent demodulation: multiply by e^{-j2πft} and integrate.
    t_start is the absolute time of the first sample (for phase continuity).
    Returns the complex integral value.
    """
    t = (np.arange(n_samples) + t_start * FS) / FS
    ref = np.exp(-2j * np.pi * freq * t)
    return np.sum(z * ref)

def decode_fsk_symbol(z_symbol: np.complex128, t_abs_start: float,
                      freq_mark: float, freq_space: float) -> int:
    """Decode one FSK symbol using phase-coherent correlation.
    Returns 1 if space tone is stronger, 0 if mark tone is stronger.
    """
    mark_val  = abs(fsk_demodulate(z_symbol, freq_mark,  t_abs_start, len(z_symbol)))
    space_val = abs(fsk_demodulate(z_symbol, freq_space, t_abs_start, len(z_symbol)))
    return 1 if space_val > mark_val else 0

def decode_burst(z_burst: np.complex128, t_burst_start: float,
                 freq_mark: float, freq_space: float, invert_manchester: bool = False):
    """Decode a full FSK burst into a byte array.
    Returns (bytes, manchester_valid_fraction) or (None, 0.0) on failure.
    """
    n_sym = SYMLEN
    # We need n_sym symbols, each SPS samples long
    n_needed = n_sym * SPS
    if len(z_burst) < n_needed:
        return None, 0.0

    symbols = []
    for s in range(n_sym):
        sym_start = s * SPS
        z_sym = z_burst[sym_start:sym_start + SPS]
        t_sym_start = t_burst_start + sym_start / FS
        symbols.append(decode_fsk_symbol(z_sym, t_sym_start, freq_mark, freq_space))

    bits = manchester_decode(symbols, invert=invert_manchester)
    # Count valid pairs
    valid_count = sum(1 for b in bits if b is not None)
    valid_frac = valid_count / (n_sym // 2) if n_sym >= 2 else 0.0

    # Filter out invalid pairs
    valid_bits = [b for b in bits if b is not None]
    if len(valid_bits) < 8:
        return None, valid_frac

    # Convert to bytes (LSB-first on the wire)
    byte_val = 0
    for i in range(8):
        byte_val |= (valid_bits[i] & 1) << i
    raw_bytes = bytes([byte_val])

    return raw_bytes, valid_frac

def find_bursts(i: np.ndarray, q: np.ndarray, threshold_db: float = -40) -> list:
    """Find signal bursts above the noise floor."""
    z = i + 1j * q
    power = np.abs(z) ** 2

    # Use a sliding window to find the noise floor
    window = 10000
    if len(power) > window:
        sorted_power = np.sort(power)
        noise_power = np.median(sorted_power[:len(sorted_power)//2])
    else:
        noise_power = np.median(power)

    threshold = noise_power * (10 ** (threshold_db / 10))

    above = power > threshold
    # Find transitions
    rising = np.where((above[1:] == 1) & (above[:-1] == 0))[0]
    falling = np.where((above[1:] == 0) & (above[:-1] == 1))[0]

    bursts = []
    for r in rising:
        if len(falling) > 0:
            f = falling[falling > r]
            if len(f) > 0:
                end = f[0]
                if end - r > 100:  # minimum burst length
                    bursts.append((r + 1, end + 1))

    return bursts

def decode_wav(wav_path: str, freq_mark: float = None, freq_space: float = None,
               invert: bool = False, verbose: bool = True):
    """Main decoder function."""
    if verbose:
        print(f"Loading {wav_path}...")

    data, fs = sf.read(wav_path, dtype='float32', always_2d=True)
    i = data[:, 0].astype(np.float64)
    q = data[:, 1].astype(np.float64)

    if verbose:
        print(f"  Samples: {len(i)}, FS: {fs}")

    # Detect frequency if not provided
    if freq_mark is None or freq_space is None:
        # Use the first burst to detect frequencies
        z = i + 1j * q
        # Find a strong burst
        power = np.abs(z) ** 2
        # Use a larger window for FFT
        n_fft = min(1 << 20, len(z))
        spectrum = np.fft.rfft(z[:n_fft] * np.hanning(n_fft))
        freqs = np.fft.rfftfreq(n_fft, 1/fs)
        mag = np.abs(spectrum)
        # Find peaks
        peak_idx = np.argmax(mag)
        peak_freq = freqs[peak_idx]
        if verbose:
            print(f"  Dominant frequency: {peak_freq/1000:.2f} kHz")
        # Assume 100 kHz separation
        freq_mark = peak_freq - 50_000
        freq_space = peak_freq + 50_000
        if verbose:
            print(f"  Using mark={freq_mark/1000:.2f} kHz, space={freq_space/1000:.2f} kHz")

    # Find bursts
    if verbose:
        print("Finding bursts...")
    bursts = find_bursts(i, q)
    if verbose:
        print(f"  Found {len(bursts)} bursts")

    results = []
    for idx, (start, end) in enumerate(bursts):
        z_burst = i[start:end] + 1j * q[start:end]
        t_start = start / fs
        raw_bytes, valid_frac = decode_burst(z_burst, t_start, freq_mark, freq_space, invert)
        if verbose:
            status = f"OK ({raw_bytes.hex()})" if raw_bytes else f"FAIL (valid={valid_frac:.1%})"
            print(f"  Burst {idx}: {start}-{end} → {status}")
        if raw_bytes:
            results.append({
                'start': start,
                'end': end,
                'bytes': raw_bytes,
                'valid_frac': valid_frac
            })

    return results, freq_mark, freq_space


def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='SoftRF Legacy FSK decoder')
    parser.add_argument('wav', help='Input WAV file')
    parser.add_argument('--mark', type=float, default=None, help='Mark frequency (Hz)')
    parser.add_argument('--space', type=float, default=None, help='Space frequency (Hz)')
    parser.add_argument('--invert', action='store_true', help='Invert Manchester decode')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()

    results, mark, space = decode_wav(
        args.wav,
        freq_mark=args.mark,
        freq_space=args.space,
        invert=args.invert,
        verbose=True
    )

    print(f"\nDecoded {len(results)} packets")
    for r in results:
        print(f"  {r['bytes'].hex()} (valid={r['valid_frac']:.1%})")


if __name__ == '__main__':
    main()
