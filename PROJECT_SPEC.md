# Project Specification

## Overview

softrf-decoder shall decode SoftRF Legacy telemetry from both:

1. Offline IQ recordings
2. Live RTL-SDR receivers

## Functional Requirements

### FR-1

The system shall accept IQ samples as input.

### FR-2

The system shall recover SoftRF Legacy frames from IQ data.

### FR-3

The system shall validate recovered frames.

### FR-4

The system shall decode telemetry payloads.

### FR-5

The system shall maintain current track state.

### FR-6

The system shall expose decoded information through output adapters.

### FR-7

The system shall operate continuously for live decoding.

---

## Output Requirements

The output system shall be adapter-based.

Initial candidate adapters:

- JSON
- GeoJSON
- KML

Implementation order shall follow project phases.

---

## Performance Requirements

Realtime decoding shall be supported when using RTL-SDR hardware.

---

## Platform Requirements

Linux only.

---

## Testing Requirements

Every practical component shall include unit tests.

Regression tests shall be maintained.

Known-good control samples shall be used whenever practical.

Any bug fixed shall receive a corresponding test.

---

## Security Requirements

Sensitive captures shall not be committed.

Location-bearing recordings shall remain outside source control.
