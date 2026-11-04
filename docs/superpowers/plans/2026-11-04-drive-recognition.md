# Drive recognition latency implementation plan

> Execution: implement in this session using systematic debugging and focused regression tests; preserve the existing Windows file-operation checks.

**Goal:** show a usable drive listing without waiting for unrelated card-modifier metadata and avoid filesystem probes for ineligible F/G volumes.

**Architecture:** keep one read worker and the existing generation invalidation. Emit a read-only listing event before modifier metadata, then the existing complete event. Only the complete event can start automatic modifier synchronization. User file actions retain fresh write-time validation.

**Spec:** User reports slow recognition after the responsive-drive change in 2026.11.04.1. Preserve all features, F/G removable-only policy, no UI I/O, no accumulating logs, MES/POP unchanged.

## Tasks
- [x] Add failing tests in tests/test_drive_recognition.py: a slow modifier probe must not hide an already-read listing; an ineligible F candidate must not require directory resolution before recognizing G; invalidated/busy/closed previews must not appear.
- [x] Reproduce against .1 and record the failing result.
- [x] Update select_destination() in apps/jihunius/app.pyw: inspect drive type first, then resolve/verify only removable candidates, preserving F-before-G and current path return semantics.
- [x] Add optional on_listing callback to read_drive_snapshot(), sending an immutable snapshot copy before the modifier signature read. Route drive_listing through generation/busy/shutdown guards and the existing content renderer; resolve a waiting user action once the listing is visible. Finish the worker only on drive_refreshed.
- [x] Keep automatic card synchronization pending until the read completes. Extend existing event test helpers to consume listing progress without weakening end-state assertions.
- [x] Run focused tests, full Tk suite, and delayed-signature timing reproduction. Compare untouched automation and companion payloads against .1.
- [x] Prepare an incremented self-contained version and verify distribution; report native Windows/USB timing as unverified.

## Review focus
Stale refresh results must not replace a newer card; preview must not re-enable writes while another job runs; deferred destructive actions must execute only once and obey cancellation; background code must not call Tk; slow metadata must not create extra worker threads or skip any write validation.
