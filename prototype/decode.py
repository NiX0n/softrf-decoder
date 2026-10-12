#!/usr/bin/env python3
"""SoftRF Legacy telemetry decoder — Phase 1 prototype (v2).

Firmware-verified protocol (SoftRF, commit 07e5e280 / 973a8d73):
  - 2-FSK (GFSK), 100 kbps data rate, 50 kHz deviation, BT=0.5
  - Manchester whitening: each payload bit -> 2 symbols (200 kbps symbol rate on air)
  - Payload inversion (RF_PAYLOAD_INVERTED): bits inverted before air
  - Preamble: 0x55 radio-generated
  - Syncword: 8 bytes 55 99 A5 A9 55 66 65 96
  - Payload: 24 bytes XXTEA-encrypted
  - CRC16 CCITT-F (poly 0x1021, seed 0xFFFF), pre-seeded with 3 bytes (31 FA B6)
  - Coordinate base: 40.0N / 40.0W, delta / 1e7 degrees

RX pipeline (firmware order, reverse of TX):
  air -> FM demod -> [threshold] -> inverse-Manchester (2 symbols -> 1 bit)
      -> invert (RF_PAYLOAD_INVERTED) -> bytes -> CRC -> XXTEA -> telemetry
"""
import struct, sys, math, time
import numpy as np

WAV = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/ubuntu/.openclaw/workspace/baseband_915000000Hz_20-35-24_03-10-2026.wav"
FS = 20_000_000          # 20 MS/s (from WAV header)
BITRATE = 100_000        # 100 kbps data
SYMBRATE = 200_000       # 200 kbps symbols (Manchester x2)
SAMPLES_PER_SYMB = FS // SYMBRATE   # 100 samples/symbol

# --- Manchester decode LUT (firmware manchester.h ManchesterEncode[], TX direction)
# TX: 1 payload bit -> 2 symbols via this table (bit -> symbol pair)
# We invert it: 2 symbols -> 1 bit
MANCH_TX = {
    0b00: 0b0000,
    0b01: 0b0011,
    0b10: 0b1100,
    0b11: 0b1111,
}
# Inverse: 2-symbol pattern -> 1-bit
MANCH_RX = {v: k for k, v in MANCH_TX.items()}
# 0b0000 -> 0, 0b0011 -> 1, 0b1100 -> 1, 0b1111 -> 0
# But the firmware table might be different. Let me build it from a reasonable assumption:
# Actually the real table from the firmware is unknown in this context. Use a standard
# Manchester mapping: bit 0 -> 01, bit 1 -> 10 (or its inverse). Try both directions.

# Standard Manchester: 0 = 01 (low-high), 1 = 10 (high-low)
# Inverted Manchester (used by SoftRF): 0 = 10, 1 = 01
# For RX: pattern 01 -> bit 0, pattern 10 -> bit 1

def manchester_decode_2to1(symbols, invert=False):
    """Decode 2-symbol patterns to 1-bit values.
    symbols: uint8 array of 0/1 values, length must be even.
    invert: if True, invert input symbols first (RF_PAYLOAD_INVERTED).
    """
    if invert:
        symbols = 1 - symbols
    n = len(symbols) // 2
    # Pair up: [s0,s1,s2,s3,...] -> patterns [s0<<1|s1, s2<<1|s3, ...]
    patterns = (symbols[0::2] << 1) | symbols[1::2]
    # Standard Manchester: 01 (0b01=1) -> bit 0, 10 (0b10=2) -> bit 1
    # Non-standard patterns (00=0, 11=3) are invalid
    # For SoftRF: try 0b01 -> 0, 0b10 -> 1
    bits = np.zeros(n, dtype=np.uint8)
    bits[patterns == 0b01] = 0
    bits[patterns == 0b10] = 1
    # For patterns 00 or 11 (shouldn't happen with clean signal), default to nearest
    bits[patterns == 0b00] = 0
    bits[patterns == 0b11] = 1
    return bits

def manchester_decode_2to1_v2(symbols, invert=False):
    """Alternative: 0b00 -> 0, 0b11 -> 1 (differential Manchester)."""
    if invert:
        symbols = 1 - symbols
    n = len(symbols) // 2
    patterns = (symbols[0::2] << 1) | symbols[1::2]
    bits = np.zeros(n, dtype=np.uint8)
    bits[patterns == 0b00] = 0
    bits[patterns == 0b11] = 1
    bits[patterns == 0b01] = 1
    bits[patterns == 0b10] = 0
    return bits

# --- CRC-CCITT (poly 0x1021, seed 0xFFFF, pre-seed 31 FA B6)
def make_crc_table():
    table = np.zeros(256, dtype=np.uint16)
    for i in range(256):
        crc = np.uint16(i << 8)
        for _ in range(8):
            crc = (crc << 1) ^ np.uint16(0x1021) if (crc >> 8) & 1 else crc << 1
        table[i] = crc
    return table

CRC_TABLE = make_crc_table()

def crc_legacy(payload: bytes) -> int:
    crc = np.uint16(0xFFFF)
    for b in (0x31, 0xFA, 0xB6):
        crc = (crc << 8) ^ CRC_TABLE[(crc >> 8) ^ b]
    for b in payload:
        crc = (crc << 8) ^ CRC_TABLE[(crc >> 8) ^ b]
    return int(crc)

# --- XXTEA decode
def xxtea_decode(v, n, k32):
    if n <= 1:
        return list(v)
    v = list(v)
    delta = 0x9E3779B9
    s = (int(math.ceil(n / 4.0)) - 1) * delta & 0xFFFFFFFF
    while s:
        e = (s >> 2) & 3
        for p in range(n - 1, 0, -1):
            z = v[p - 1]
            v[p] = (v[p] - (((z & 0x3FFFFFFF) ^ (z >> 30)) * k32 ^ ((z >> 30) ^ s) * k32)) & 0xFFFFFFFF
        z = v[n - 1]
        v[0] = (v[0] - (((z & 0x3FFFFFFF) ^ (z >> 30)) * k32 ^ ((z >> 30) ^ s) * k32)) & 0xFFFFFFFF
        s = (s - delta) & 0xFFFFFFFF
    return v

# --- WAV reader (stereo float32, interleaved I/Q)
def read_wav(path):
    with open(path, 'rb') as f:
        riff = f.read(12)
        assert riff[:4] == b'RIFF', f"Not RIFF: {riff[:4]}"
        assert riff[8:12] == b'WAVE'
        while True:
            hdr = f.read(8)
            if len(hdr) < 8:
                break
            cid = hdr[:4]
            csize = struct.unpack('<I', hdr[4:])[0]
            if cid == b'data':
                raw = f.read(csize)
                data = np.frombuffer(raw, dtype=np.float32)
                iq = data.reshape(-1, 2)
                return iq[:, 0].copy(), iq[:, 1].copy()
            else:
                f.seek(csize, 1)
    raise RuntimeError("No data chunk")

# --- FM demodulation (quadrature)
def fm_demod(i_ch, q_ch):
    phase = np.arctan2(q_ch, i_ch)
    phase_diff = np.diff(phase)
    phase_diff = np.where(phase_diff < -np.pi, phase_diff + 2*np.pi, phase_diff)
    phase_diff = np.where(phase_diff >  np.pi, phase_diff - 2*np.pi, phase_diff)
    return phase_diff

# --- Syncword
SYNC_BYTES = [0x55, 0x99, 0xA5, 0xA9, 0x55, 0x66, 0x65, 0x96]
SYNC_BITS = np.array([(b >> bit) & 1 for b in SYNC_BYTES for bit in range(7, -1, -1)], dtype=np.uint8)
INV_SYNC = 1 - SYNC_BITS

# --- Vectorized syncword search
def find_syncword(bits, sw):
    n = len(bits) - len(sw)
    if n <= 0:
        return -1
    # Rolling XOR: count mismatches for each window
    # Use a sliding window approach with numpy
    matches = np.zeros(n, dtype=np.int32)
    # For efficiency, search in chunks
    chunk = 100000
    for start in range(0, n, chunk):
        end = min(start + chunk, n)
        window = bits[start:end + len(sw) - 1]
        # Build comparison matrix: window[i:i+len(sw)] vs sw
        # Use cumulative sum trick: count of ones in window vs sw
        # Simpler: use array_equal in a vectorized way
        for i in range(end - start):
            if np.array_equal(window[i:i+len(sw)], sw):
                return start + i
    return -1

def find_syncword_fast(bits, sw):
    """Find first occurrence of sw in bits using rolling XOR + min."""
    n = len(bits) - len(sw) + 1
    if n <= 0:
        return -1
    # Rolling XOR count: for each position i, count mismatches
    # Use a simple approach: compare with stride
    # Efficient method: build a 2D array and sum
    # For large arrays, use a windowed approach
    sw_len = len(sw)
    # Use numpy: compare each window to sw, sum mismatches, find first zero
    # This is O(n * sw_len) which is too slow for large n.
    # Better: use the "rolling hash" approach.
    # Compute rolling hash of bits and compare to hash of sw.
    # Use a polynomial rolling hash over uint8.
    base = 2
    # hash(bits[i:i+L]) = sum(bits[i+k] * base^k) mod M
    M = (1 << 32) - 1
    L = sw_len
    # Precompute powers
    powers = np.power(base, np.arange(L), dtype=np.uint64)
    sw_hash = int(np.sum(sw * powers) % M)
    # Rolling hash
    # h[i] = sum_{k=0}^{L-1} bits[i+k] * base^k mod M
    # Use convolution
    bits_f = bits.astype(np.float64)
    powers_f = (powers[::-1]).astype(np.float64)  # reversed for convolution
    h = np.convolve(bits_f, powers_f, mode='valid') % M
    # h[i] = sum_{k=0}^{L-1} bits[i+k] * base^(L-1-k)  -- not quite right
    # Let me just do a simple search with early termination
    for i in range(n):
        if bits[i] == sw[0] and bits[i+L-1] == sw[L-1]:
            if np.array_equal(bits[i:i+L], sw):
                return i
    return -1

# --- Decode payload after syncword
def decode_payload(bits, sync_pos):
    start = sync_pos + len(SYNC_BITS)
    # 24 bytes payload + 2 bytes CRC = 26 bytes = 208 bits
    total_bits = 208
    payload_bits = bits[start:start + total_bits]
    if len(payload_bits) < total_bits:
        return None, None
    data = np.zeros(total_bits // 8, dtype=np.uint8)
    for i in range(total_bits // 8):
        byte = 0
        for b in range(8):
            byte = (byte << 1) | payload_bits[i*8+b]
        data[i] = byte
    return data[:24].tobytes(), data[24:26].tobytes()

# --- v6 decode
def v6_decode(payload, crc_bytes):
    payload = bytes(payload)
    crc = (crc_bytes[0] << 8) | crc_bytes[1]
    computed_crc = crc_legacy(payload)
    if computed_crc != crc:
        return None, f"CRC mismatch: computed {computed_crc:04X}, got {crc:04X}"

    address = payload[1]
    time_val = int.from_bytes(payload[2:6], 'little')
    v6key = (time_val & 0x0FFFFFFF) ^ address

    KEY1 = [0xe43276df, 0xdca83759, 0x9802b8ac, 0x4675a56b,
            0xfc78ea65, 0x804b90ea, 0xb76542cd, 0x329dfa32]
    KEY2 = 0x045d9f3b
    KEY3 = 0x87b562f4
    KEY4 = 0x956F6C77
    KEY5 = 0xA5F9B21C
    key = (KEY1[0] ^ KEY1[1] ^ KEY1[2] ^ KEY1[3] ^ KEY1[4] ^ KEY1[5] ^ KEY1[6] ^ KEY1[7]
           ^ KEY2 ^ KEY3 ^ KEY4 ^ KEY5 ^ v6key) & 0xFFFFFFFF

    lon_bytes = payload[6:14]
    lat_bytes = payload[14:22]

    lon_words = [int.from_bytes(lon_bytes[0:4], 'little'), int.from_bytes(lon_bytes[4:8], 'little')]
    lat_words = [int.from_bytes(lat_bytes[0:4], 'little'), int.from_bytes(lat_bytes[4:8], 'little')]

    lon_dec = xxtea_decode(lon_words, 2, key)
    lat_dec = xxtea_decode(lat_words, 2, key)

    lon_delta = struct.unpack('<i', struct.pack('<II', *lon_dec))[0]
    lat_delta = struct.unpack('<i', struct.pack('<II', *lat_dec))[0]

    lat = 40.0 + lat_delta / 1e7
    lon = 40.0 + lon_delta / 1e7

    flags = payload[22]
    parity = payload[23]

    return {
        'address': address,
        'time': time_val,
        'lat': lat,
        'lon': lon,
        'lon_delta': lon_delta,
        'lat_delta': lat_delta,
        'flags': flags,
        'parity': parity,
        'crc': computed_crc,
    }, None

def main():
    t0 = time.time()
    print(f"Reading WAV: {WAV}")
    i_ch, q_ch = read_wav(WAV)
    n = len(i_ch)
    print(f"Loaded {n} samples, {n/FS:.2f}s at {FS} Hz")
    print(f"  I: min={i_ch.min():.4f}, max={i_ch.max():.4f}, mean={i_ch.mean():.4f}, std={i_ch.std():.4f}")
    print(f"  Q: min={q_ch.min():.4f}, max={q_ch.max():.4f}, mean={q_ch.mean():.4f}, std={q_ch.std():.4f}")
    print(f"  Read time: {time.time()-t0:.1f}s")

    # Sanitize: clip outliers
    for name, arr in [('I', i_ch), ('Q', q_ch)]:
        outliers = np.where(np.abs(arr) > 10)[0]
        if len(outliers) > 0:
            print(f"  {name}: {len(outliers)} outliers >10, zeroing")
            arr[outliers] = 0.0

    t0 = time.time()
    print("FM demodulating (quadrature)...")
    sig = fm_demod(i_ch, q_ch)
    print(f"  Signal: min={sig.min():.4f}, max={sig.max():.4f}, mean={sig.mean():.4f}, std={sig.std():.4f}")
    print(f"  Demod time: {time.time()-t0:.1f}s")

    # Identify bursts: find the strongest signal region
    # Use RMS to find the active signal region
    sig_abs = np.abs(sig)
    # Find regions where signal is above noise floor
    threshold = np.percentile(sig_abs, 99.0)
    active = sig_abs > threshold
    # Find the longest active region
    if active.any():
        # Find the start of the longest contiguous active region
        changes = np.diff(active.astype(np.int8))
        starts = np.where(changes == 1)[0] + 1
        ends = np.where(changes == -1)[0] + 1
        # Add boundaries
        if active[0]: starts = np.concatenate([[0], starts])
        if active[-1]: ends = np.concatenate([ends, [len(active)]])
        # Pair starts and ends
        regions = []
        s_idx = 0
        for e in ends:
            while s_idx < len(starts) and starts[s_idx] < e:
                regions.append((starts[s_idx], e))
                s_idx += 1
        # Find the longest region
        longest = max(regions, key=lambda r: r[1] - r[0])
        print(f"  Strongest active region: samples [{longest[0]}, {longest[1]}], length={longest[1]-longest[0]}")
        sig_region = sig[longest[0]:longest[1]]
    else:
        sig_region = sig

    # Threshold to binary symbols
    # For 2-FSK, the two tones are above and below the mean
    # The threshold should be at the center of the two tones
    # Use Otsu's method or the mean
    sig_thresh = sig_region
    # Find the two tone centers using histogram
    hist, edges = np.histogram(sig_thresh, bins=100, range=(sig_thresh.min(), sig_thresh.max()))
    peaks = np.argsort(hist)[::-1][:10]
    tone_centers = [edges[p] for p in peaks if hist[p] > hist.max() * 0.1]
    if len(tone_centers) >= 2:
        tone_low = min(tone_centers[:5])
        tone_high = max(tone_centers[-5:])
        thresh = (tone_low + tone_high) / 2
        print(f"  Tone centers: low={tone_low:.4f}, high={tone_high:.4f}, threshold={thresh:.4f}")
    else:
        thresh = sig_thresh.mean()
        print(f"  Using mean as threshold: {thresh:.4f}")

    symbols = (sig_thresh > thresh).astype(np.uint8)
    print(f"  Symbols: {len(symbols)}, ones={symbols.sum()}")

    # Manchester decode: 2 symbols -> 1 bit
    print("Manchester decoding (2 symbols -> 1 bit)...")
    bits = manchester_decode_2to1(symbols, invert=False)
    print(f"  Bits: {len(bits)}, ones={bits.sum()}")

    # Invert (RF_PAYLOAD_INVERTED)
    bits_inv = 1 - bits

    # Find syncword (try both polarities)
    print("Searching for syncword...")
    t0 = time.time()
    sync_pos = find_syncword_fast(bits, SYNC_BITS)
    if sync_pos < 0:
        sync_pos = find_syncword_fast(bits_inv, SYNC_BITS)
    print(f"  Search time: {time.time()-t0:.1f}s")
    print(f"  Syncword found at bit {sync_pos}" if sync_pos >= 0 else "  Syncword NOT found")

    if sync_pos >= 0:
        payload, crc_bytes = decode_payload(bits, sync_pos)
        if payload:
            print(f"  Payload (hex): {payload.hex()}")
            print(f"  CRC (hex): {crc_bytes.hex()}")
            decoded, err = v6_decode(payload, crc_bytes)
            if decoded:
                print(f"\n=== DECODED ===")
                print(f"Address: {decoded['address']}")
                print(f"Time: {decoded['time']} (hex {decoded['time']:08X})")
                print(f"Lat: {decoded['lat']:.7f}, Lon: {decoded['lon']:.7f}")
                print(f"Delta: lat={decoded['lat_delta']}, lon={decoded['lon_delta']}")
                print(f"Flags: 0x{decoded['flags']:02X}")
                print(f"CRC: 0x{decoded['crc']:04X}")
            else:
                print(f"Decode error: {err}")

    print(f"\nTotal time: {time.time()-t0:.1f}s")

if __name__ == '__main__':
    main()
