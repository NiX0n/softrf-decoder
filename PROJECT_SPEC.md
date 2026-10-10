# Project Specification

## Project Name

softrf-decoder

## Purpose

Decode SoftRF Legacy telemetry transmissions from:

- Offline IQ captures
- Live RTL-SDR receivers

and expose decoded telemetry through reusable output adapters.

---

# Technology Decisions

The following decisions are considered resolved.

Future implementations shall not revisit these choices without written justification.

## Primary Language

TypeScript

All application logic shall be written in TypeScript unless there is a documented reason not to.

Examples:

- protocol decoding
- track management
- adapters
- services
- APIs
- orchestration

## DSP Platform

GNU Radio

GNU Radio is considered a permanent dependency.

DSP implementation shall occur within GNU Radio whenever practical.

Custom DSP implementations require written justification.

## Service Framework

NestJS

NestJS is the target application framework.

However:

NestJS shall not be introduced until the relevant functionality has been proven in isolated libraries.

Business logic shall not depend directly on NestJS.

## Python Usage

Python is permitted for:

- GNU Radio integration
- DSP experimentation
- Analysis tools
- Development utilities

Python shall not become the primary application language.

---

# Functional Requirements

## FR-1

The system shall accept IQ sample streams.

## FR-2

The system shall recover SoftRF Legacy frames.

## FR-3

The system shall validate recovered frames.

## FR-4

The system shall decode telemetry payloads.

## FR-5

The system shall maintain current track state.

## FR-6

The system shall expose telemetry through adapter interfaces.

## FR-7

The system shall support realtime operation using RTL-SDR hardware.

---

# Output Requirements

Output implementations shall be adapters.

Planned adapters:

- JSON
- GeoJSON
- KML

The decoder shall not depend on any specific output format.

---

# Platform Requirements

Linux only.

---

# Licensing

MIT

---

# Security Requirements

Sensitive location-bearing captures shall not be committed.

Control captures must remain outside source control.

Synthetic fixtures should be preferred whenever practical.

---

# Testing Requirements

Unit testing is mandatory.

Regression testing is mandatory.

The control capture shall act as a validation corpus.

Bug fixes shall include tests where practical.
