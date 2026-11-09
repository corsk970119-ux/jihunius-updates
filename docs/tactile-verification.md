# 2026.11.09.6 verification

Selected concept 2: original navy palette, shallow raised native controls, visible outlines; defect warning and replacement arrows on all 9 existing quick pairs. Full green/red/yellow machine surfaces restored. Unknown is gray; stale markers, PRM text, alerts and bindings unchanged.

- Full regression: 341 tests passed in 151.261 s (Xvfb, Python 3.12 / Tk 9).
- Final versioned package: 4 release-package tests passed in 0.992 s. The final preparation changed only SUITE_APP_VERSION and the manifest; runtime source matched the reviewed/tested implementation.
- Regression evidence: baseline .5 fails the two new missing-icon/full-fill assertions; current implementation passes. Native disabled/invoke behavior and machine selection/state/image-cache stability verified.
- Korean-font minimum layout: all 18 icon+label pairs fit within 1000px at 96 and 120 DPI; height remains governed by existing minimum-content calculation (830 / 876px).
- Main CNC/STL/wash tabs, wash-log/protrusion/special-table/material companion windows rendered without callback errors. Linux preview uses NanumBarunGothic in place of Windows Malgun Gothic.
- Five-run sequential baseline/current median (ms): startup 360.115 / 374.197; machine update 0.239 / 0.257; tab switch 1.399 / 1.205. No new timers, runtime Pillow, animations, network calls or per-poll image allocation. These are local measurements, not a guarantee of identical performance on Windows.
- Independent read-only whole-change review of 282b8a0..b5b5240: no Critical/Important/Minor findings; embedded theme/quick/companions independently matched their sources and hashes.
- Native Windows DPI/font rendering and real company device/MES/POP paths remain field verification; no external production automation was run during testing.

Release: 1243719 bytes; SHA-256 21ec85f0de8883f65789c8fb7cbbb51b8add0b347af7001e3e791b4a4a86fb1e.
