# Architecture

## High-Level Architecture

RTL-SDR / IQ File
        |
        v
    GNU Radio
        |
        v
 Frame Recovery
        |
        v
 Legacy Decoder
        |
        v
 Track Manager
        |
        v
 Output Adapters

---

## Development Phases

### Phase 0

Planning

Deliverables:

- Documentation
- Specifications
- Architecture

### Phase 1

Offline Decode

Input:

Known-good IQ sample

Output:

Decoded telemetry

### Phase 2

Decoder Library

Refactor prototype into maintainable components.

### Phase 3

Realtime Receiver

Replace file input with RTL-SDR.

### Phase 4

Track Management

Convert packets into track state.

### Phase 5

Output Adapters

Implement:

- JSON
- GeoJSON
- KML

### Phase 6

NestJS Integration

Wrap proven services into a long-running application.

---

## Architectural Principles

- GNU Radio is a permanent dependency.
- DSP stays in GNU Radio.
- Business logic remains separate from DSP.
- Output formats are adapters.
- Protocol decoding remains independent of output formats.
