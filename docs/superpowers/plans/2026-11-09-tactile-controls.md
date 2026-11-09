# Implementation plan and ledger

Baseline: local 282b8a0, published 2026.11.09.5. Spec: ../specs/2026-11-09-tactile-controls.md.

1. Add meaningful UI regression coverage; build static button and icon assets, attach icons to existing native quick buttons, restore full machine fills.
2. Apply shallow depth to companion buttons without changing action handlers, geometry or data paths. Rebuild embedded sources; inspect main and popup renders.
3. Run full checks, fresh independent whole-change review, prepare and atomically publish .6 with expected-head verification. Verify deployed hashes and manifest.

Status: implementation, full checks and independent review complete; atomic deployment pending. Selection/implementation/deployment authorized by user; exact bevel and icon artwork are implementation judgments.


Task 1 complete: static assets/icons and full machine fill; regression tests written first, initial execution blocked by missing Xvfb, then confirmed failing against .5 and passing current. Native 18-button disabled/invoke routing passed.
Task 2 complete: companion bevels retain image-cache bounds, geometry and handlers. Korean minimum layout 1000px at 96/120 DPI passes; all four popup renders have no callback errors.
Task 3 verification complete: 341/341 tests; final package 4/4 tests; independent source review found no findings. Remote base source hashes match local baseline.
Review caveats resolved by rendered Korean-font fit and completed full suite. Native Windows rendering/device integration remain field-only verification, as with the baseline.
