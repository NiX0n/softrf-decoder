#!/usr/bin/env python3
"""
SoftRF Legacy V6 - Fault-tolerant decoder with proper FSK demodulation.

Uses a phase-coherent quadrature demodulator (textbook FSK approach):
1. For each symbol, correlate signal with e^(-j*2*pi*f_mark*t) and e^(-j*2*pi*f_space*t)
2. Pick the tone with higher energy
3. Manchester decode, invert, find syncword, verify CRC, decrypt XXTEA

Key: the reference phase is continuous across symbols (not reset to 0).
"""

import sys
import struct
import numpy as np

# Protocol Constants
FS = 20_000_000
BITRATE = 100_000
SYMBOL_RATE = 200_000
SYMBOL_SP = SPS = FS // SYMBOL_RATE  # 100 samples per half-symbol

SYNCWORD = bytes([0x55, 0x99, 0xA5, 0xA9, 0x55, 0x66, 0x65, 0x96])
SYNC_BITS = []
for byte in SYNCWORD:
    for i in range(7, -1, -1):
        SYNC_BITS.append((byte >> i) & 1)
SYNC_BITS = np.array(SYNC_BITS, dtype=np.int8)

LEGACY_KEY = bytes.fromhex(
    "04 5d 9f 3b 45 c5 2b f3 6f 2a c6 5c a9 9c 40 3b"
)

CRC_POLY = 0x1021
CRC_INIT = 0xFFFF
CRC_PRE_SEED = [0x55, 0x99, 0xA5]


def load_wav(path):
    with open(path, "rb") as f:
        riff = f.read(12)
        assert riff[:4] == b'RIFF' and riff[8:12] == b'WAVE'
        while True:
            cid = f.read(4)
            if len(cid) < 4:
                break
            csz = struct.unpack('<I', f.read(4))[0]
            if cid == b'data':
                data = f.read(csz)
                break
            f.read(csz)
    samples = np.frombuffer(data, dtype=np.float32).astype(np.complex64)
    print(f"  Loaded {len(samples):,} samples ({len(samples)/FS:.2f}s)")
    return samples


def find_bursts(sig, energy_thresh=0.01):
    win = 20000
    env = np.array([np.mean(np.abs(sig[i:i+win])**2) if i+win < len(sig) else 0 
                    for i in range(0, len(sig)-win, win)])
    thresh = env.mean() * 2
    in_burst = False
    bursts = []
    for i, e in enumerate(env):
        if e > thresh and not in_burst:
            start = i * win
            in_burst = True
        elif e < thresh and in_burst:
            end = i * win
            if end - start > 20000:
                bursts.append((start, end))
            in_burst = False
    if in_burst:
        bursts.append((len(env) * win, len(sig)))
    return bursts


def fsk_demodulate(sig, f_mark, f_space, num_symbols):
    """
    Phase-coherent FSK demodulation.
    
    For each symbol, correlate with continuous phase references.
    The key: reference phase accumulates continuously, not reset per symbol.
    """
    symbols = np.zeros(num_symbols, dtype=np.int8)
    
    for i in range(num_symbols):
        s0 = i * SYMBOL_SP
        s1 = s0 + SYMBOL_SP
        if s1 >= len(sig):
            break
        sym = sig[s0:s1]
        
        # Absolute time for this symbol (continuous across symbols)
        abs_t = (i * SYMBOL_SP + np.arange(SYMBOL_SP)) / FS
        
        # Correlate with mark and space references
        mark_ref = np.exp(-1j * 2 * np.pi * f_mark * abs_t)
        space_ref = np.exp(-1j * 2 * np.pi * f_space * abs_t)
        
        mark_corr = np.abs(np.dot(sym, np.conj(mark_ref)))
        space_corr = np.abs(np.dot(sym, np.conj(space_ref)))
        
        symbols[i] = 1 if mark_corr > space_corr else 0
    
    return symbols


def manchester_decode(symbols):
    """Firmware ManchesterEncode: bit 1 = 0,1  bit 0 = 1,0. Inverse mapping."""
    bits = []
    for i in range(0, len(symbols)-1, 2):
        if symbols[i] == 0 and symbols[i+1] == 1:
            bits.append(1)
        elif symbols[i] == 1 and symbols[i+1] == 0:
            bits.append(0)
    return np.array(bits, dtype=np.int8)


def invert_bits(bits):
    return np.where(bits == 1, 0, 1).astype(np.int8)


def bits_to_bytes(bits):
    byte_count = len(bits) // 8
    result = np.zeros(byte_count, dtype=np.uint8)
    for i in range(byte_count):
        b = 0
        for j in range(8):
            b = (b << 1) | bits[i*8 + j]
        result[i] = b
    return result


def find_syncword(bits):
    if len(bits) < 64:
        return -1
    sw = SYNC_BITS
    matches = []
    for i in range(len(bits) - len(sw) + 1):
        if np.array_equal(bits[i:i+len(sw)], sw):
            matches.append(i)
    return matches[0] if matches else -1


def crc16_ccitt_f(data, pre_seed=None):
    crc = CRC_INIT
    if pre_seed:
        for b in pre_seed:
            crc ^= b << 8
            for _ in range(8):
                crc = ((crc << 1) ^ CRC_POLY) & 0xFFFF if (crc & 0x8000) else (crc << 1) & 0xFFFF
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ CRC_POLY) & 0xFFFF if (crc & 0x8000) else (crc << 1) & 0xFFFF
    return crc


def btea_decrypt(data, key):
    DELTA = 0x9E3779B9
    rounds = 32
    v = list(struct.unpack('<4I', data[:16]))
    k = list(struct.unpack('<4I', key[:16]))
    q = rounds
    s = (DELTA * q) & 0xFFFFFFFF
    while q:
        s = (s - DELTA) & 0xFFFFFFFF
        e = (s >> 2) & 3
        for i in range(3, -1, -1):
            jj = (i + 1) % 4
            kk = i % 4
            v[i] = (v[i] - ((((v[jj] >> 5) ^ ((i + v[jj]) >> 2)) ^ v[i]) + ((v[(i+3)%4] >> 5) ^ (s >> 2)) + k[kk] + (v[kk] >> 5))) & 0xFFFFFFFF
        q = q - 1
    return struct.pack('<4I', *v)


def main():
    wav_path = "/home/ubuntu/.openclaw/workspace/baseband_915000000Hz_20-35-24_03-10-2026.wav"
    print(f"=== SoftRF Legacy V6 Decoder ===")
    print(f"  WAV: {wav_path}")
    print(f"  FS={FS}, BR={BITRATE}, SPS={SYMBOL_SP}")
    print()

    print("Loading I/Q...")
    iq = load_wav(wav_path)

    print("Finding bursts...")
    bursts = find_bursts(iq)
    print(f"  {len(bursts)} bursts")
    for i, (s, e) in enumerate(bursts):
        dur = (e - s) / FS
        print(f"    [{i}] t={s/FS:.3f}s - {e/FS:.3f}s ({dur:.3f}s)")

    # Measure tones for first burst
    s, e = bursts[0]
    sig = iq[s:e]
    fft = np.fft.fft(sig, n=4096)
    freqs = np.fft.fftfreq(4096, 1.0/FS)
    power = np.abs(fft)**2
    top = np.argsort(power)[-5:][::-1]
    print(f"\nTop 5 frequencies (first burst):")
    for idx in top:
        print(f"  {freqs[idx]:+.1f} kHz, power={power[idx]/power.max():.3f}")

    # Use measured tones
    f_mark = -730_000.0
    f_space = -830_000.0

    print(f"\nTrying f_mark={f_mark/1000:.0f} kHz, f_space={f_space/1000:.0f} kHz")
    num_symbols = len(sig) // SYMBOL_SP
    print(f"  {num_symbols} symbols")

    # Phase-coherent demodulation
    symbols = fsk_demodulate(sig, f_mark, f_space, num_symbols)
    ones = np.sum(symbols == 1)
    zeros = np.sum(symbols == 0)
    print(f"  1s: {ones}, 0s: {zeros}")

    bits = manchester_decode(symbols)
    print(f"  Manchester bits: {len(bits)}")
    valid = sum(1 for i in range(0, len(symbols)-1, 2)
                if (symbols[i] == 0 and symbols[i+1] == 1) or
                   (symbols[i] == 1 and symbols[i+1] == 0))
    total = len(symbols)//2
    print(f"  Valid pairs: {valid}/{total}")

    # Try both polarities
    for polarity in [0, 1]:
        bits_try = invert_bits(bits) if polarity else bits
        pos = find_syncword(bits_try)
        if pos >= 0:
            print(f"\n  *** SYNCWORD FOUND at pos {pos} (polarity={polarity}) ***")
            payload = bits_to_bytes(bits_try)
            pkt = payload[pos//8 : pos//8+32]
            print(f"  Packet: {' '.join(f'{b:02x}' for b in pkt[:24])}")
            raw_payload = pkt[8:24]
            crc_stored = (pkt[24] | (pkt[25] << 8)) & 0xFFFF
            crc_calc = crc16_ccitt_f(raw_payload, pre_seed=CRC_PRE_SEED)
            print(f"  CRC: stored={crc_stored:04x}, calc={crc_calc:04x}, match={crc_stored==crc_calc}")
            if crc_stored == crc_calc:
                print("  *** CRC VERIFIED ***")
                decrypted = btea_decrypt(raw_payload, LEGACY_KEY)
                print(f"  Decrypted: {' '.join(f'{b:02x}' for b in decrypted)}")
                text = bytes(b for b in decrypted if 32 <= b < 127).decode('ascii', errors='ignore')
                if len(text) > 3:
                    print(f"  ASCII: {text}")
            return

    print(f"\n  No syncword found.")

    # Try with swapped tones
    print(f"\n  Swapping tones...")
    symbols2 = fsk_demodulate(sig, f_space, f_mark, num_symbols)
    bits2 = manchester_decode(symbols2)
    valid2 = sum(1 for i in range(0, len(symbols)-1, 2)
                 if (symbols2[i] == 0 and symbols2[i+1] == 1) or
                    (symbols2[i] == 1 and symbols2[i+1] == 0))
    print(f"  Valid pairs: {valid2}/{total}")
    for polarity in [0, 1]:
        bits_try = invert_bits(bits2) if polarity else bits2
        pos = find_syncword(bits_try)
        if pos >= 0:
            print(f"\n  *** SYNCWORD FOUND (swapped) at pos {pos} ***")
            return

    print(f"\n  Still no syncword. Need to investigate further.")


if __name__ == "__main__":
    main()
