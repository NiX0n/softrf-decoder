#!/usr/bin/env python3
"""
OOK Decoder - FINAL
The signal is a continuous 915 MHz carrier (phase ~-54°) with AM modulation.
After rotating to 0°, the I channel shows two peaks:
  -0.026 (OFF) and -0.0015 (ON)
Threshold: -0.0135 (midpoint)
"""
import numpy as np

WAV_FILE = "/home/ubuntu/.openclaw/workspace/baseband_915000000Hz_20-35-24_03-10-2026.wav"
SR = 20_000_000
SYNC = [0x55, 0x99, 0xA5, 0xA9, 0x55, 0x66, 0x65, 0x96]

print("=== OOK Decoder (Final) ===")

with open(WAV_FILE, 'rb') as f:
    header = f.read(44)
    data = np.frombuffer(f.read(), dtype=np.float32)
iq = data.reshape(-1, 2)
I = iq[:, 0].astype(np.float32)
Q = iq[:, 1].astype(np.float32)

# Rotate to align carrier to 0°
PHASE_OFFSET = 0.94
I_rot = I * np.cos(PHASE_OFFSET) + Q * np.sin(PHASE_OFFSET)

# Threshold at midpoint of the two peaks
THRESH = -0.0135
symbols = (I_rot > THRESH).astype(np.uint8)

print(f"Threshold: {THRESH}")
print(f"ON fraction: {symbols.mean()*100:.2f}%")

# The 10% duty cycle means ~10% of symbols should be ON
# Let's check
print(f"Expected: ~10% ON")
print(f"Actual: {symbols.mean()*100:.2f}% ON")

# Now search for sync pattern
SYNC_BITS = []
for b in SYNC:
    for i in range(7, -1, -1):
        SYNC_BITS.append(1 if (b >> i) & 1 else 0)
SYNC_BITS = np.array(SYNC_BITS, dtype=np.uint8)
SYNC_LEN = len(SYNC_BITS)
print(f"\nSYNC pattern: {SYNC_LEN} bits")
print(f"  {SYNC_BITS}")

# Search for sync
n = len(symbols)
print(f"\nSearching {n} symbols for sync pattern...")
best_match = 0
best_pos = -1
for pos in range(0, n - SYNC_LEN + 1, 64):  # Step by 64 for speed
    match = np.sum(symbols[pos:pos+SYNC_LEN] == SYNC_BITS)
    if match > best_match:
        best_match = match
        best_pos = pos
    if match == SYNC_LEN:
        break

print(f"Best match: {best_match}/{SYNC_LEN} at position {best_pos}")

if best_match >= SYNC_LEN - 2:  # Allow 2 bit errors
    print("\n*** SYNC FOUND! ***")
    # Extract the payload after sync
    payload_start = best_pos + SYNC_LEN
    payload_len = 256  # Try 256 bits = 32 bytes
    if payload_start + payload_len <= n:
        payload = symbols[payload_start:payload_start+payload_len]
        print(f"Payload ({payload_len} bits = {payload_len//8} bytes):")
        for i in range(0, payload_len, 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | payload[i+j]
            print(f"  {i//8:2d}: 0x{byte:02x}")
else:
    print(f"\nNo sync found. Best match was {best_match}/{SYNC_LEN}")
    print("The signal might be at a different symbol rate or the sync pattern is different.")
    
    # Let's try to estimate the symbol rate by looking at the burst structure
    print("\n=== Symbol Rate Estimation ===")
    # Find runs of ON symbols
    changes = np.diff(symbols.astype(np.int8))
    on_starts = np.where(changes == 1)[0]
    on_ends = np.where(changes == -1)[0]
    on_durations = []
    for s, e in zip(on_starts, on_ends):
        if e > s:
            on_durations.append(e - s)
    
    if on_durations:
        on_durations = np.array(on_durations)
        print(f"ON runs: {len(on_durations)}")
        print(f"  min={on_durations.min()} symbols, max={on_durations.max()} symbols")
        print(f"  mean={on_durations.mean():.1f} symbols")
        # Convert to time assuming 1 symbol = 1 bit at 769 ksym/s
        # At 769 ksym/s: 1 symbol = 1.3 µs
        # At 384.5 ksym/s: 1 symbol = 2.6 µs
        for rate in [769000, 384500, 234000, 117000]:
            sym_time = 1e6 / rate  # µs
            mean_time = on_durations.mean() * sym_time
            print(f"  At {rate} sym/s: mean ON = {mean_time:.1f} µs")
