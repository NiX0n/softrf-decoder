"""Fix the sync word detection.

Firmware decode order:
  1. Manchester decode 2 symbols -> 1 bit
  2. Group bits into bytes (8 bits/byte, MSB first)
  3. Look for preamble 0x55 then sync word 55 99 A5 A9 55 66 65 96

So I need to check the MANCHESTER-DECODED bytes for the sync word pattern.
My earlier analysis found 0x55 at 80% of positions in the RAW stream,
which is the PREAMBLE byte, not the sync word.

Let me:
1. Use the 8-bit threshold to get bits
2. Manchester-decode pairs of bits into nibbles
3. Build bytes and look for sync word
"""
import numpy as np
from scipy.signal import find_peaks
import struct
import os

# Load file
fpath = '/home/ubuntu/.openclaw/workspace/baseband_915000000Hz_20-35-24_03-10-2026.wav'
size = os.path.getsize(fpath)
with open(fpath, 'rb') as f:
    f.read(44)
    buf = np.fromfile(f, dtype=np.float32)
iq = buf.reshape(-1, 2)
n = min(len(iq), 50_000_000)
I = iq[:n, 0].astype(np.float64)

# Get bits
I_c = I - I.mean()
thr = (I_c.max() + I_c.min()) / 2
bits = (I_c > thr).astype(np.uint8)

# Manchester decode: 2 bits -> 1 bit
# 00 -> 0, 01 -> 0, 10 -> 0, 11 -> 1
bits_m = ((bits[::2] & bits[1::2])).astype(np.uint8)
print(f"Manchester decoded bits: {len(bits_m)}")

# Build bytes (MSB first)
byte_count = len(bits_m) // 8
bytes_out = np.zeros(byte_count, dtype=np.uint8)
for i in range(byte_count):
    b = 0
    for j in range(8):
        b = (b << 1) | bits_m[i*8+j]
    bytes_out[i] = b

# Find sync word
sync = np.array([0x55, 0x99, 0xA5, 0xA9, 0x55, 0x66, 0x65, 0x96], dtype=np.uint8)
positions = []
for i in range(len(bytes_out)-8):
    if np.array_equal(bytes_out[i:i+8], sync):
        positions.append(i)
print(f"Sync word found at positions: {positions[:20]}")
print(f"Total: {len(positions)}")

# Also look for preamble 0x55 before sync
for pos in positions[:5]:
    if pos > 0:
        print(f"  Byte before sync @ {pos}: {bytes_out[pos-1]:02x} (expect 55)")
    # Show 32 bytes around
    start = max(0, pos-16)
    end = min(len(bytes_out), pos+32)
    print(f"  Context: {bytes_out[start:end].hex(' ').upper()}")

# Also check: what if the bits are LSB first?
bytes_out_lsb = np.zeros(byte_count, dtype=np.uint8)
for i in range(byte_count):
    b = 0
    for j in range(8):
        b |= bits_m[i*8+j] << j
    bytes_out_lsb[i] = b

positions_lsb = []
for i in range(len(bytes_out_lsb)-8):
    if np.array_equal(bytes_out_lsb[i:i+8], sync):
        positions_lsb.append(i)
print(f"\nLSB-first: sync word found at {len(positions_lsb)} positions")
for pos in positions_lsb[:5]:
    start = max(0, pos-16)
    end = min(len(bytes_out_lsb), pos+32)
    print(f"  Context @ {pos}: {bytes_out_lsb[start:end].hex(' ').upper()}")
