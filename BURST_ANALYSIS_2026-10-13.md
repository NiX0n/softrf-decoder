# BURST ANALYSIS — 2026-10-13

> **⚠️ NOTE (2026-10-20):** Burst detection results in this document remain valid.
\u003> The OOK/ASK amplitude-based classification was later rejected — see
\u003> `SESSION_REPORT_2026-10-20.md` for the corrected FSK interpretation.

## Critical Discovery: Noise-Subtracted Burst Detection

### Method
Using the silence capture (`silence_baseband_915000000Hz_14-59-57_12-10-2026.wav`) as a noise reference:

1. Extract noise DC offset: I_mean = 0.0222, Q_mean = -0.0320
2. Subtract DC offset from signal I/Q
3. Compute corrected envelope
4. Apply threshold at 2× noise std (0.0111)
5. Detect contiguous above-threshold regions as bursts

### Noise Model (from silence capture)
- **Noise floor (envelope mean)**: 0.0394
- **Noise std (envelope)**: 0.0056
- **Noise I std**: 0.0056
- **Noise Q std**: 0.0056
- **DC offset**: I=0.0222, Q=-0.0320

### Detected Bursts (12 real bursts >1000 samples)

| Burst | Start (samples) | End (samples) | Duration (samples) | Duration (ms) | Start (ms) |
|-------|-----------------|---------------|--------------------|---------------|------------|
| 0 | 3,223,767 | 3,327,164 | 103,397 | 5.170 | 161.188 |
| 1 | 7,143,664 | 7,246,897 | 103,233 | 5.162 | 357.183 |
| 2 | 21,264,644 | 21,368,284 | 103,640 | 5.182 | 1063.232 |
| 3 | 27,203,392 | 27,307,038 | 103,646 | 5.182 | 1360.170 |
| 4 | 43,223,461 | 43,327,096 | 103,635 | 5.182 | 2161.173 |
| 5 | 49,263,496 | 49,366,947 | 103,451 | 5.173 | 2463.175 |
| 6 | 65,104,204 | 65,207,769 | 103,565 | 5.178 | 3255.210 |
| 7 | 70,663,508 | 70,766,945 | 103,437 | 5.172 | 3533.175 |
| 8 | 80,624,715 | 80,728,042 | 103,327 | 5.166 | 4031.236 |
| 9 | 91,943,623 | 92,046,986 | 103,363 | 5.168 | 4597.181 |
| 10 | 101,044,684 | 101,148,071 | 103,387 | 5.169 | 5052.234 |
| 11 | 110,543,563 | 110,647,020 | 103,457 | 5.173 | 5527.178 |

### Key Statistics
- **Count**: 12 bursts
- **Duration range**: 5.162 – 5.182 ms (σ = 0.010 ms, extremely tight)
- **Mean duration**: 5.173 ms (103,462 samples)
- **Spacing range**: 190.8 – 795.8 ms (irregular)
- **Mean spacing**: 482.6 ms
- **Total signal ON time**: 62.1 ms
- **Total capture**: 5.616 s
- **Duty cycle**: 1.105%

### Interpretation

The bursts are:
1. **Extremely consistent in duration** (5.17 ms ± 0.01 ms) — this is a **fixed-length packet**
2. **Irregularly spaced** (190–796 ms) — this suggests **event-driven transmission** (transmit when there's data to send)
3. **12 bursts in 5.6 seconds** — roughly 2.14 bursts/second on average

### Packet Size Estimation

At 20 MS/s sampling, 103,462 samples per burst. If the signal is OOK/ASK:

- **If 1 bit per sample** (1 bit/µs = 1 Msym/s): 103,462 bits = **12,933 bytes**
- **If 1 bit per 2 samples** (500 ksym/s): 51,731 bits = **6,466 bytes**
- **If 1 bit per 10 samples** (100 ksym/s): 10,346 bits = **1,293 bytes**
- **If 1 bit per 100 samples** (10 ksym/s): 1,035 bits = **129 bytes**

Without knowing the symbol rate, we can't determine the packet size. However, the **burst duration of 5.17 ms** is a strong constraint.

### What Changed from Previous Analysis

Previous analysis (without noise subtraction) found:
- 355,665 bursts (mostly 1-sample noise spikes)
- 14 long bursts >100 samples
- Bursts "~100 ms" (this was WRONG — those were noise regions, not signal bursts)

With noise subtraction, the picture is much cleaner:
- **12 real signal bursts** (not 14 — 2 were spurious)
- Each **~5.17 ms** (not 100 ms)
- **Irregular spacing** (event-driven)

### Next Steps

1. **Determine symbol rate** — try multiple symbol periods and check for:
   - Consistent bit transitions
   - Known sync words (e.g., `5599a5a955666596`)
   - Reasonable bit patterns (not all 0s or all 1s)

2. **Look for packet structure** — the fixed 5.17 ms duration suggests:
   - Fixed-length data field
   - Or variable-length with maximum of ~5.17 ms

3. **Correlate with SoftRF firmware** — check the actual SoftRF source code for:
   - Transmission protocol
   - Packet format
   - Symbol rate
   - Modulation type

### Files
- `reality_check.py` — Updated with noise-subtracted burst detection
- `silence_baseband_915000000Hz_14-59-57_12-10-2026.wav` — Noise reference
- `baseband_915000000Hz_20-35-24_03-10-2026.wav` — Signal capture

---
*Analysis performed: 2026-10-13 02:38 UTC*
