# SoftRF Legacy Decoding - Status

## What I've Tried

1. **Direct tone correlation** at -730 kHz and -830 kHz
   - Result: 50% 1s and 0s, but only 20% valid Manchester pairs

2. **FM demodulation with phase derivative**
   - Result: Phase differences are very noisy, not clearly separating into two tones

3. **AM demodulation**
   - Result: Amplitude is varying with a period of 50 samples, not clearly separating into two tones

4. **Phase-locked loop (PLL)**
   - Result: Phase is rotating too fast to track reliably

## Key Observations

1. The signal is definitely FSK with two tones at -730 kHz and -830 kHz (approximately)
2. The symbol rate is 200 ksym/s (100 samples per symbol)
3. The Manchester decoding is not producing valid pairs with any of the approaches I've tried
4. The amplitude is varying with a period of 50 samples (half the symbol duration)

## Possible Issues

1. **Modulation scheme**: The signal might be using GFSK (Gaussian FSK) instead of simple FSK
2. **Alignment**: My symbol boundaries might not be aligned with the actual symbol boundaries
3. **Signal quality**: The signal might be too noisy to reliably detect the tones
4. **Frequency offset**: The exact frequencies of the two tones might be slightly different from what I've assumed

## Recommendation

The signal appears to be a valid FSK transmission, but my current demodulation approaches are not able to reliably decode it. I recommend:

1. **Try a different demodulation approach**: Use a more sophisticated PLL or a matched filter bank
2. **Check the exact frequencies**: Use a spectrum analyzer to determine the exact frequencies of the two tones
3. **Improve the alignment**: Use a better algorithm to find the symbol boundaries
4. **Improve the signal quality**: Use a better antenna or a closer receiver

## Conclusion

The signal is definitely an FSK transmission, but my current approaches are not able to reliably decode it. Further investigation is needed to determine the exact modulation scheme and to improve the demodulation algorithm.
