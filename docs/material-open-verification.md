# 2026.11.09.7 material startup verification

User report: sub-PC material popup shows bare [Errno 13] Permission denied. The specific field PC was not available; the verified code defect is a read of the locked sentinel before Windows byte-lock acquisition and outside the lock-conflict handler.

Changes:
- Acquire singleton byte lock before any read/write; keep genuine file-open failures distinct from lock contention.
- Recover a live local material window/control session, preserve native show/toggle and quick-input nonce/queue routing. Windows process handles bind to creation time; wrong/recycled PID, stale/ambiguous legacy sessions are rejected.
- Preserve original two-phase update protocol for owned sessions. Recovered/shared sessions require a graceful complete restart before updating, because a .6 original parent can otherwise delete the close acknowledgment. Complete exit remains graceful; no force-kill or record/settings deletion.
- Concurrent duplicate child exits with a dedicated signal; parent reattaches; stale crash registries cannot bypass startup grace. Other startup failures display stage/path and are captured in diagnostics.

Validation:
- 361 tests passed in 223.748 s against the final .7 package (Python 3.12/Tk 9, Xvfb).
- 20 added regression tests cover mandatory-lock read failure, contention/open permission distinction, hidden/live/legacy/stale/ambiguous process reuse, native Windows handle mocks, PID lifetime, quick command routing, duplicate startup, two-parent update preflight, registry cleanup and startup diagnostics.
- Original mandatory-lock model reproduced Errno 13 before the fix. Independent review found the two-parent cleanup race and stale-registry grace issue; both new reproductions failed before their fixes and passed afterward. No re-review substituted for these tests.
- AST comparison confirms all material-counter business/UI definitions except InstanceLock/new InstanceAlreadyRunning, and all material_ui definitions except boot, match .6. Existing engine/payload and companion-source/hash tests passed.
- No new polling timer, network query, runtime dependency, database migration, collection owner change or design change. Registry lookup runs at startup/recovery; ongoing native observation uses a nonblocking process handle.

Limit: actual Windows GUI, permissions on the reported sub-PC, and company telemetry/MES/POP were not exercised here. This fixes the reproducible startup paths; genuine ACL/security software failures retain specific diagnostics rather than being hidden.

Artifact: 1260719 bytes, SHA-256 a800b80041611254b13ea98d299957c99be11934540fc48b5252a70501514485.
Reference for mandatory byte-lock behavior and locking past EOF: https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/locking?view=msvc-170
