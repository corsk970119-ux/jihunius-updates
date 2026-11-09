# Drive refresh layout stability

Scope: prevent the host window, header controls and file list from moving during
manual refresh, card insertion and transient drive-read errors. Existing palette,
button styles and drive worker/business operations are retained.

## Reproduction and cause

In the previous build, the header's 100-pixel wrapped status expanded while
`check_card_modifier` displayed its preparation message, then contracted when the
previous status returned. A Korean-font Tk reproduction moved the body from y=108
to y=134 and raised a minimum-sized window from height 826 to 852. The drive status
also wrapped a read-error message and moved its list down 15 pixels.

## Changes

- Fixed one-line requested geometry for header and drive status labels. Text is
  fitted with an ellipsis; the complete original message is available on hover.
  Repeated unchanged text uses a cache; no polling loop or dependency was added.
- Directory identity now uses destination, labels and paths, excluding status.
  Status-only refreshes leave the live list intact. Changed lists retain both
  scroll axes and surviving selections.
- No changes to drive discovery, modifier synchronization, file actions, machine
  monitoring or companion process handling.

## Verification

- Regression test failed before the fix: 63 layout/list assertions across two
  DPI settings and window sizes. All four added tests pass after the fix.
- Reproduction with Korean fonts confirms stable body/header/list bounds through
  wait, preparation, connected and error states.
- Tests cover 100%/125% scaling, default/minimum widths, repeated status changes,
  no list rebuild for a status update, scroll/selection retention, full hover
  text, popup cleanup on shutdown, and text fitting inside the styled badge.
- Full regression suite: 364 tests passed in 224.150 seconds. Review then caught
  an 8-pixel status-text inset discrepancy; a boundary regression failed before
  correcting the inset calculation. The final 2026.11.09.8 package passed 40
  targeted tests in 12.582 seconds (drive layout/recognition, host stability,
  window placement, controls and release payload integrity).
- Korean-font minimum-window visual check at 100% and 125% scaling: all 18 quick
  button labels and icons fit. The correction adds no timer or disk I/O.
- Final application size: 1,264,144 bytes. SHA-256:
  `bcc3bbff9c97de7b12d4f373bae64dcb2e49fe0bd31d10c00fa853549aa6ef9d`.

Windows hardware/card insertion cannot be exercised in this Linux test host.
The real Tk rendering and the same UI completion methods are exercised locally.
Release source, distribution copy and immutable version file are byte-identical.
