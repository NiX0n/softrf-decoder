#!/usr/bin/env python3
"""Phase 1 offline decode prototype for SoftRF Legacy telemetry.
Firmware-verified protocol: 2-FSK 100kbps 50kHz dev, Manchester whitening,
syncword 55 99 A5 A9 55 66 65 96, 24-byte payload, CRC16 CCITT-FFFF (seed 31 FA B6),
XXTEA with 5-key XOR + v6key (time XOR address), base 40N/40W, delta/1e7 degrees.
"""
import struct, sys, math, time
import numpy as np

WAV = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/.openclaw/workspace/baseband_915000000Hz_20-35-24_03-10-2026.wav"
FS = 30_000_000  # sample rate
BITRATE = 100_000  # 100 kbps

# --- CRC-CCITT (firmware: P_CCITT=0x1021, seed FFFF, pre-seed 31 FA B6)
def make_crc_table():
    table = np.zeros(256, dtype=np.uint16)
    for i in range(256):
        crc = np.uint16(i << 8)
        for _ in range(8):
            if (crc >> 8) & 1:
                crc = (crc << 1) ^ np.uint16(0x1021)
            else:
                crc = crc << 1
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

# --- XXTEA decode (firmware: 31-bit delta, 4-byte key)
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

# --- Read WAV (stereo float32: odd=I, even=Q)
def read_wav(path):
    t0 = time.time()
    with open(path, 'rb') as f:
        riff = f.read(12)
        assert riff[:4] == b'RIFF', f"Not RIFF: {riff[:4]}"
        assert riff[8:12] == b'WAVE', f"Not WAVE"
        while True:
            hdr = f.read(8)
            if len(hdr) < 8:
                break
            cid = hdr[:4]
            csize = struct.unpack('<I', hdr[4:])[0]
            if cid == b'data':
                n = csize // 8  # complex samples (2ch x 4 bytes)
                raw = f.read(n * 8)
                # Interleaved: [I0, Q0, I1, Q1, ...]
                data = np.frombuffer(raw, dtype=np.float32)
                iq = data.reshape(-1, 2)
                i_ch = iq[:, 0]
                q_ch = iq[:, 1]
                return i_ch, q_ch
            else:
                f.seek(csize, 1)
    raise RuntimeError("No data chunk")

# --- FM demodulation via quadrature (angle differentiation)
def fm_demod(i_ch, q_ch):
    """Quadrature FM demod: out[n] = atan2(q[n],i[n]) - atan2(q[n-1],i[n-1]).
    Unwrap to remove 2π discontinuities.
    """
    phase = np.arctan2(q_ch, i_ch)
    phase_diff = np.diff(phase)
    # Unwrap: add 2π where the jump is > π
    phase_diff = np.where(phase_diff < -np.pi, phase_diff + 2*np.pi, phase_diff)
    phase_diff = np.where(phase_diff >  np.pi, phase_diff - 2*np.pi, phase_diff)
    return phase_diff

# --- Syncword
SYNC_BYTES = [0x55, 0x99, 0xA5, 0xA9, 0x55, 0x66, 0x65, 0x96]
SYNC_BITS = []
for byte in SYNC_BYTES:
    for bit in range(7, -1, -1):
        SYNC_BITS.append((byte >> bit) & 1)
SYNC_BITS = np.array(SYNC_BITS, dtype=np.uint8)
INV_SYNC = 1 - SYNC_BITS

# --- Find syncword in bit array
def find_syncword(bits, sw, max_pos=None):
    if max_pos is None:
        max_pos = len(bits) - len(sw)
    # Use numpy for efficient pattern search
    # Build a rolling comparison: compare each window to sw
    for i in range(0, max_pos, 1):
        if np.array_equal(bits[i:i+len(sw)], sw):
            return i
    return -1

# --- Decode payload after syncword
def decode_payload(bits, sync_pos):
    start = sync_pos + len(SYNC_BITS)
    payload_bits = bits[start:start + 272]
    if len(payload_bits) < 272:
        return None, None
    # Convert to bytes (MSB first)
    data = np.zeros(34, dtype=np.uint8)
    for i in range(34):
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

    # v6key = (time & 0x0fffffff) ^ address
    v6key = (time_val & 0x0FFFFFFF) ^ address

    # KEY values from Legacy.h
    KEY1 = [0xe43276df, 0xdca83759, 0x9802b8ac, 0x4675a56b,
            0xfc78ea65, 0x804b90ea, 0xb76542cd, 0x329dfa32]
    KEY2 = 0x045d9f3b
    KEY3 = 0x87b562f4
    KEY4 = 0x956F6C77
    KEY5 = 0xA5F9B21C
    key = (KEY1[0] ^ KEY1[1] ^ KEY1[2] ^ KEY1[3] ^ KEY1[4] ^ KEY1[5] ^ KEY1[6] ^ KEY1[7]
           ^ KEY2 ^ KEY3 ^ KEY4 ^ KEY5 ^ v6key) & 0xFFFFFFFF

    # Relative coordinates (XXTEA encoded)
    lon_bytes = payload[6:14]
    lat_bytes = payload[14:22]

    lon_words = [int.from_bytes(lon_bytes[0:4], 'little'), int.from_bytes(lon_bytes[4:8], 'little')]
    lat_words = [int.from_bytes(lat_bytes[0:4], 'little'), int.from_bytes(lat_bytes[4:8], 'little')]

    lon_dec = xxtea_decode(lon_words, 2, key)
    lat_dec = xxtea_decode(lat_words, 2, key)

    lon_delta = int.from_bytes(struct.pack('<II', *lon_dec), 'little')
    lat_delta = int.from_bytes(struct.pack('<II', *lat_dec), 'little')

    if lon_delta > 2**31: lon_delta -= 2**32
    if lat_delta > 2**31: lat_delta -= 2**32

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
    print(f"Loaded {n} samples ({n*2} complex), {n/FS:.2f}s")
    print(f"  I: min={i_ch.min():.4f}, max={i_ch.max():.4f}, mean={i_ch.mean():.4f}")
    print(f"  Q: min={q_ch.min():.4f}, max={q_ch.max():.4f}, mean={q_ch.mean():.4f}")
    print(f"  Read time: {time.time()-t0:.1f}s")

    # FM demodulate using quadrature
    t0 = time.time()
    print("FM demodulating (quadrature)...")
    sig = fm_demod(i_ch, q_ch)
    print(f"  Signal range: [{sig.min():.4f}, {sig.max():.4f}], mean={sig.mean():.4f}")
    print(f"  Demod time: {time.time()-t0:.1f}s")

    # Downsample to ~200 samples per bit (20MHz effective)
    # FS=30MHz, bitrate=100kbps → 300 samples/bit
    # For 2FSK: one bit = one tone (not two). Use 300 samples per bit.
    samples_per_bit = int(FS / BITRATE)  # 300
    print(f"Sampling at {samples_per_bit} samples/bit (100 kbps)")

    # Threshold
    thresh = 0.0  # For 2FSK, center of the two tones
    sig_norm = (sig - sig.mean()) / (sig.std() + 1e-10)
    bits = (sig_norm > 0).astype(np.uint8)
    print(f"  Bits: {len(bits)}, ones={bits.sum()}")

    # Find syncword
    t0 = time.time()
    print("Searching for syncword...")
    sync_pos = find_syncword(bits, SYNC_BITS)
    if sync_pos < 0:
        print("  Normal syncword NOT found, trying inverted...")
        sync_pos = find_syncword(bits, INV_SYNC)
    print(f"  Search time: {time.time()-t0:.1f}s")
    print(f"  Syncword found at bit {sync_pos}" if sync_pos >= 0 else "  Syncword NOT found")

    if sync_pos >= 0:
        # Check if we need to invert
        is_inverted = np.array_equal(bits[sync_pos:sync_pos+len(SYNC_BITS)], INV_SYNC)
        if is_inverted:
            print("  (inverted pattern detected — inverting all bits)")
            bits = 1 - bits
            sync_pos = find_syncword(bits, SYNC_BITS)

        payload, crc_bytes = decode_payload(bits, sync_pos)
        if payload:
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

    # Diagnostic: print some sample bits
    print("\n--- Diagnostic: bit stream samples ---")
    for offset in [1000, 10000, 100000, 1000000, 10000000]:
        if offset + 10 < len(bits):
            print(f"  bit[{offset}] = {''.join(str(b) for b in bits[offset:offset+10])}")

    print(f"\nTotal time: {time.time()-t0:.1f}s")

if __name__ == '__main__':
    main()
