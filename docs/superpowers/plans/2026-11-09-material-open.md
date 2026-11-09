# Material startup fix plan / ledger

Baseline: local 6cc7233, published 3483accafc1b5a9c97a0cf357cce20a9fc18ea6b (.6).
Spec: ../specs/2026-11-09-material-open.md.
1. Reproduce lock read failure; fix acquire-before-read and classify busy vs access failure.
2. Reattach existing local material session with PID lifetime validation and legacy recovery; handle duplicate startup and preserve quick inputs/update handshake. Add actionable startup diagnostics.
3. Full regression, fresh whole-change review, release .7, atomic publication and exact hash verification.

Status: implementation in progress. Windows production PC is not accessible; explicit emulated mandatory-lock tests plus OS process tests provide reproducible coverage; actual field confirmation remains separate.


Task 1 complete: the Windows mandatory-byte-lock model reproduced bare Errno 13 in old code; acquire-first passes, genuine file-open permission remains distinct.
Task 2 complete: live hidden process reuse, legacy session recovery, lifetime/nonce/path validation, quick request routing and startup diagnostics pass targeted tests.
Final review: independent reviewer found shared-session update cleanup race and stale registry startup grace issue. Both repro tests failed before the fix and pass afterward.
Final ruling: recovered sessions do not acquire update ownership. Require a graceful full restart before an update from the recovering parent; .6 original parents can otherwise delete the only close acknowledgment. This intentionally costs one full restart only in recovered-session update mode; normal owned-session updates retain the original two-phase protocol. No data or pending inputs are deleted.
Stale registry finding elevated to important for the reported startup path; process lifetime is now validated before the duplicate child ends its bounded startup wait.
Full verification complete: 361/361 tests in 223.748 s against final .7 package; atomic publication pending.
