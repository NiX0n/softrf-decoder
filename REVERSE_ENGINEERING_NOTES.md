# Reverse Engineering Notes

This document may contain:

- Discoveries
- Hypotheses
- Open questions
- Experimental results

Content here is not automatically considered fact.

Verified information must be promoted into SYSTEM_FACTS.md.

---

# Current Open Questions

## Frequency Selection

Determine:

- Region frequency plan
- Legacy frequency selection
- Actual programmed frequencies
- Channel spacing

Source trace required:

Protocol
    ->
Region
    ->
Channel Plan
    ->
Radio Driver
    ->
setFrequency()

---

## Frequency Hopping

Determine:

- Hop channel count
- Hop spacing
- Hop timing
- Synchronization behavior

---

## Packet Format

Determine:

- Preamble
- Sync word
- Payload structure
- CRC implementation
- Whitening
- Framing

---

## Validation Targets

Ground-truth control sample successfully decodes.

Decoded output matches known validation conditions.

---

# Discovery Log

## Initial RF Capture

Capture validated.

Properties:

- Float32 IQ
- 20 MS/s
- ~5.6 seconds
- Observable RF bursts present

Status:

Suitable for decoder development.

---

## Known Protocol Information

Legacy:

- 2-FSK
- 100 kbps
- 50 kHz deviation

Further verification from firmware source required.
