#!/usr/bin/env python3
"""Phase 1 offline decode prototype for SoftRF Legacy telemetry.
Firmware-verified protocol: 2-FSK 100kbps 50kHz dev, Manchester whitening,
syncword 55 99 A5 A9 55 66 65 96, 24-byte payload, CRC16 CCITT-FFFF (seed 31 FA B6),
XXTEA with 5-key XOR + v6key (time XOR address), base 40N/40W, delta/1e7 degrees.
"""
import struct, sys, math

WAV = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/.openclaw/workspace/baseband_915000000Hz_20-35-24_03-10-2026.wav"
FS = 30_000_000  # sample rate
BITRATE = 100_000  # 100 kbps
SAMPLES_PER_BIT = FS / BITRATE  # 300

# --- CRC-CCITT (firmware: P_CCITT=0x1021, seed FFFF, delta 31 FA B6)
def make_crc_table():
    table = []
    for i in range(256):
        crc = 0; c = i << 8
        for _ in range(8):
            if (crc ^ c) & 0x8000: crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else: crc = (crc << 1) & 0xFFFF
            c = (c << 1) & 0xFFFF
        table.append(crc)
    return table

CRC_TABLE = make_crc_table()
def update_crc(crc, b): return (crc << 8) ^ CRC_TABLE[(crc >> 8) ^ (b & 0xFF)] & 0xFFFF
def crc_legacy(payload):
    crc = 0xFFFF
    for b in (0x31, 0xFA, 0xB6): crc = update_crc(crc, b)
    for b in payload: crc = update_crc(crc, b)
    return crc

# --- XXTEA decode (firmware: 31-bit delta, 4-byte key)
def xxtea_decode(v, n, k32):
    if n <= 1: return list(v)
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

# --- Read WAV (stereo float32, even channels = signal)
def read_wav(path):
    with open(path, 'rb') as f:
        riff = f.read(12)
        assert riff[:4] == b'RIFF', f"Not RIFF: {riff[:4]}"
        assert riff[8:12] == b'WAVE', f"Not WAVE"
        while True:
            hdr = f.read(8)
            if len(hdr) < 8: break
            cid = hdr[:4]; csize = struct.unpack('<I', hdr[4:])[0]
            if cid == b'data':
                n = csize // 4  # samples (2ch x 4 bytes)
                raw = f.read(n * 4)
                return [struct.unpack('<f', raw[i*4:i*4+4])[0] for i in range(n)]
            else:
                f.seek(csize, 1)
    raise RuntimeError("No data chunk")

# --- FM demodulation: differentiate and use as baseband
def fm_demod(samples):
    out = [0.0] * (len(samples) - 1)
    for i in range(len(samples) - 1):
        out[i] = samples[i+1] - samples[i]
    return out

# --- Threshold to bits
def threshold_bits(sig, thresh=None):
    if thresh is None:
        thresh = max(abs(min(sig)), max(sig)) * 0.1
    return [1 if s > thresh else 0 for s in sig]

# --- Find syncword pattern in bit stream (MSB first, 8 bytes)
SYNC_BYTES = [0x55, 0x99, 0xA5, 0xA9, 0x55, 0x66, 0x65, 0x96]
SYNC_BITS = []
for byte in SYNC_BYTES:
    for bit in range(7, -1, -1):
        SYNC_BITS.append((byte >> bit) & 1)

def find_syncword(bits, sw):
    for i in range(len(bits) - len(sw)):
        if bits[i:i+len(sw)] == sw:
            return i
    return -1

# --- Decode payload after syncword
def decode_payload(bits, sync_pos):
    """Extract 34 bytes (24 payload + 2 CRC) after syncword."""
    start = sync_pos + len(SYNC_BITS)
    # Read 34 bytes = 272 bits
    payload_bits = bits[start:start + 272]
    if len(payload_bits) < 272:
        return None
    # Convert to bytes (MSB first)
    data = []
    for i in range(34):
        byte = 0
        for b in range(8):
            byte = (byte << 1) | payload_bits[i*8+b]
        data.append(byte)
    return data[:24], data[24:26]

# --- v6 decode
def v6_decode(payload, crc_bytes):
    payload = bytes(payload)
    crc = (crc_bytes[0] << 8) | crc_bytes[1]
    computed_crc = crc_legacy(payload)
    if computed_crc != crc:
        return None, f"CRC mismatch: computed {computed_crc:04X}, got {crc:04X}"
    
    # Address
    address = payload[1]
    # Time (4 bytes, little-endian uint32)
    time_val = int.from_bytes(payload[2:6], 'little')
    
    # v6key = (time & 0x0fffffff) ^ address
    v6key = (time_val & 0x0FFFFFFF) ^ address
    # key = KEY1 XOR KEY2 XOR KEY3 XOR KEY4 XOR KEY5 + v6key
    # Need to find the actual KEY values from Legacy.h
    # For now, assume they're all 0 (will need to find actual values)
    # Actually, let's search for them in the firmware source
    key1 = 0xe43276df ^ 0xdca83759 ^ 0x9802b8ac ^ 0x4675a56b ^ 0xfc78ea65 ^ 0x804b90ea ^ 0xb76542cd ^ 0x329dfa32
    key2 = 0x045d9f3b; key3 = 0x87b562f4; key4 = 0x956F6C77
    key5 = 0xA5F9B21C ^ 0xAB3F9D12 ^ 0xC6F34E34 ^ 0xD72FA378
    key = (key1 ^ key2 ^ key3 ^ key4 ^ key5 ^ v6key) & 0xFFFFFFFF
    
    # Relative coordinates (XXTEA encoded)
    # lon: bytes 6..13 (8 bytes)
    # lat: bytes 14..21 (8 bytes)
    lon_bytes = payload[6:14]
    lat_bytes = payload[14:22]
    
    # XXTEA expects 4-byte words. For 8 bytes, that's 2 words.
    lon_words = [int.from_bytes(lon_bytes[0:4], 'little'), int.from_bytes(lon_bytes[4:8], 'little')]
    lat_words = [int.from_bytes(lat_bytes[0:4], 'little'), int.from_bytes(lat_bytes[4:8], 'little')]
    
    lon_dec = xxtea_decode(lon_words, 2, key)
    lat_dec = xxtea_decode(lat_words, 2, key)
    
    lon_delta = int.from_bytes(struct.pack('<II', *lon_dec), 'little')
    lat_delta = int.from_bytes(struct.pack('<II', *lat_dec), 'little')
    
    # Handle negative values (two's complement)
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
    print(f"Reading WAV: {WAV}")
    samples = read_wav(WAV)
    print(f"Loaded {len(samples)} samples, {len(samples)/FS:.2f}s")
    print(f"Min: {min(samples):.4f}, Max: {max(samples):.4f}, Mean: {sum(samples)/len(samples):.4f}")
    
    # Downsample to 10 MHz for easier FM demod
    ds = samples[::3]
    print(f"Downsampled to 10 MHz: {len(ds)} samples")
    
    # FM demod
    print("FM demodulating...")
    sig = fm_demod(ds)
    print(f"Signal range: [{min(sig):.4f}, {max(sig):.4f}]")
    
    # Threshold
    print("Thresholding...")
    bits = threshold_bits(sig)
    print(f"Total bits: {len(bits)}")
    print(f"Ones: {sum(bits)}")
    
    # Find syncword
    print("Searching for syncword...")
    sync_pos = find_syncword(bits, SYNC_BITS)
    print(f"Syncword found at bit {sync_pos}" if sync_pos >= 0 else "Syncword NOT found")
    
    if sync_pos < 0:
        # Try the inverted pattern
        inv_sync = [1 - b for b in SYNC_BITS]
        sync_pos = find_syncword(bits, inv_sync)
        print(f"Inv syncword at bit {sync_pos}" if sync_pos >= 0 else "Still not found")
        if sync_pos >= 0:
            bits = [1 - b for b in bits]  # invert all
    
    if sync_pos >= 0:
        result, payload, crc = decode_payload(bits, sync_pos)
        if result:
            decoded, err = v6_decode(payload, crc)
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
        else:
            print("Payload decode failed")
    
    # Diagnostic: print some sample bits around expected sync position
    print("\n--- Diagnostic: bit stream samples ---")
    for offset in [1000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000]:
        if offset + 10 < len(bits):
            print(f"  bit[{offset}] = {''.join(str(b) for b in bits[offset:offset+10])}")

if __name__ == '__main__':
    main()
