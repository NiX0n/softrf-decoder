# SoftRF Legacy Decoding - Final Status

## Summary

After extensive investigation, I have been unable to successfully decode the
SoftRF Legacy protocol from the baseband WAV capture. The signal is definitely
FSK, but my demodulation approaches have not been able to reliably extract
the bits.

## What I've Tried

### 1. Direct Tone Correlation
- Assumed tones at -730 kHz and -830 kHz (±50 kHz around -780 kHz center)
- Cross-correlated I and Q channels with sine/cosine at these frequencies
- Result: 50% 1s and 0s, but only 20% valid Manchester pairs
- **Failed**: The frequencies were incorrect

### 2. FFT Spectrum Analysis
- Analyzed the frequency spectrum of the signal
- Result: The signal is NOT at ±50 kHz around a center frequency
- The signal has a large DC component (peak at 0 Hz)
- After DC removal, the signal is mostly at 2 kHz, with small amounts at ±98 kHz
- **Surprising**: The signal is not at the expected FSK frequencies

### 3. Frequency Histogram
- Computed the instantaneous frequency of the signal using `np.angle(z[1:]*np.conj(z[:-1]))`
- Result: The signal is mostly at 2 kHz (23.4 million samples)
- Small amounts at ±98 kHz (609,942 and 837,616 samples)
- **Surprising**: The signal is not at ±50 kHz

### 4. Standard FSK Demodulation
- Multiplied the signal by mark and space reference tones (±50 kHz)
- Lowpass filtered the result
- Compared the two outputs to determine the bit
- Result: The bits were switching between 0 and 1, but the pattern was not clear
- **Failed**: The approach did not produce a usable bit stream

### 5. Signal Analysis
- The I channel is consistently around 0.022, and the Q channel is consistently around -0.032
- This means the signal is at a fixed point in the complex plane (approximately I=0.022, Q=-0.032)
- The signal is quantized to 5 levels (multiples of 0.0078125)
- **Surprising**: The signal is not switching between different frequencies

## Key Observations

1. The signal is definitely FSK (it's switching between 0 and 1)
2. The signal is NOT at the expected FSK frequencies (±50 kHz)
3. The signal is at 2 kHz (mostly) and ±98 kHz (small amounts)
4. The signal is quantized to 5 levels
5. The I and Q channels are not behaving like a standard I/Q signal

## Possible Explanations

1. **Wrong center frequency**: The signal might be at a different center frequency than I assumed
2. **Wrong deviation**: The signal might have a different deviation than 50 kHz
3. **Different modulation scheme**: The signal might not be 2-FSK
4. **Signal processing issue**: The signal might have been processed in a way that I'm not accounting for
5. **WAV file format issue**: The WAV file might not contain I/Q data as expected

## What I've Learned

1. The skill file says the signal is 2-FSK at 100 kbps with 50 kHz deviation
2. The signal is definitely FSK (it's switching between 0 and 1)
3. The signal is not at the expected FSK frequencies (±50 kHz)
4. The signal is quantized to 5 levels
5. The I and Q channels are not behaving like a standard I/Q signal

## Recommendations

1. **Verify the WAV file format**: Confirm that the WAV file contains I/Q data
2. **Check the center frequency**: The signal might be at a different center frequency
3. **Check the deviation**: The signal might have a different deviation
4. **Try a different demodulation approach**: Use a more sophisticated PLL or matched filter bank
5. **Look for a reference implementation**: Find a standard FSK demodulator that works with this type of signal
6. **Consult with an RF expert**: An expert might be able to identify the modulation scheme and provide guidance

## Conclusion

The signal is definitely an FSK transmission, but my current approaches are not
able to reliably decode it. Further investigation is needed to determine the exact
modulation scheme and to improve the demodulation algorithm.

## Next Steps

1. Verify the WAV file format and signal characteristics
2. Determine the correct center frequency and deviation
3. Try a different demodulation approach
4. Look for a reference implementation of FSK demodulation
5. Consult with an RF expert if needed

## Files

- `decode.py` - Initial demodulation attempts
- `decode_v2.py` - Phase-continuous 2-FSK demodulator
- `REVERSE_ENGINEERING_NOTES.md` - Protocol details from firmware
- `SYSTEM_FACTS.md` - System facts and assumptions
