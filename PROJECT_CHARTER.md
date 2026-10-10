# softrf-decoder

## Purpose

Build a real-time receiver capable of detecting, demodulating, decoding, and tracking SoftRF Legacy telemetry transmissions.

The system shall support offline analysis using known-good IQ captures and realtime reception using RTL-SDR hardware.

## Project Goal

Convert RF telemetry transmissions into structured location and tracking data consumable by external systems.

## Non-Goals

The following are explicitly out of scope for the initial MVP:

- Browser UI
- Mapping UI
- User authentication
- Database storage
- Cloud deployment
- Mobile applications
- Multi-protocol support
- Protocols other than SoftRF Legacy

## Success Criteria

### Phase 1

Given a known-good IQ sample:

- Detect signal bursts
- Recover frames
- Decode telemetry
- Verify decoded output meets known validation conditions

### MVP

Given a live RTL-SDR:

- Receive SoftRF Legacy telemetry
- Decode telemetry in realtime
- Maintain current track state
- Expose output through adapter interfaces

## License

MIT
