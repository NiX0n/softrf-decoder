# Architecture

## Guiding Principle

GNU Radio performs DSP.

TypeScript performs everything else.

---

# High-Level Architecture

                 IQ Samples
                       |
                       v
                GNU Radio DSP
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

# Architectural Layers

## Layer 1 - DSP

Responsibilities:

- SDR integration
- filtering
- synchronization
- demodulation
- symbol recovery
- frame extraction

Technology:

- GNU Radio

Outputs:

- recovered frames

---

## Layer 2 - Protocol Decoding

Responsibilities:

- frame validation
- CRC validation
- payload decoding

Technology:

- TypeScript

Outputs:

- telemetry objects

---

## Layer 3 - Tracking

Responsibilities:

- track state
- track updates
- object lifecycle

Technology:

- TypeScript

Outputs:

- track objects

---

## Layer 4 - Adapters

Responsibilities:

- JSON
- GeoJSON
- KML

Technology:

- TypeScript

Outputs:

- external representations

---

## Layer 5 - Service Host

Responsibilities:

- configuration
- lifecycle
- dependency injection
- endpoint exposure

Technology:

- NestJS

---

# Development Lifecycle

## Phase 0

Planning

Deliverables:

- specifications
- architecture
- documentation

Acceptance:

documentation approved

---

## Phase 1

Offline Decode Prototype

Input:

control IQ capture

Output:

decoded telemetry

Acceptance:

known validation condition is satisfied

---

## Phase 2

Decoder Library

Goal:

refactor prototype into maintainable libraries

Acceptance:

automated tests pass

---

## Phase 3

Realtime Receiver

Goal:

replace file input with RTL-SDR

Acceptance:

live telemetry received

---

## Phase 4

Track Manager

Goal:

produce realtime track state

Acceptance:

track updates observable

---

## Phase 5

Output Adapters

Goal:

produce external representations

Acceptance:

at least one adapter validated

---

## Phase 6

NestJS Host

Goal:

assemble proven components into long-running application

Acceptance:

end-to-end operation
