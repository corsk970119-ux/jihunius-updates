# Shared error history

Approved: error-only collection, combined three-PC view, clear all in one action, deploy. Existing business behavior and performance stay intact.

1. Local SQLite store, 100 records per PC / 30 days; bounded strings and dedup within 60 seconds for same feature, stage and work. Event capture queues to a local worker; no normal-operation logs. PC-local ON/OFF. Tests: retention, concurrent writers, toggle, persistence, detail, dedup.
2. Shared error-only subfolder of existing handover folder. One snapshot per PC; lock serializes snapshot and deletion-generation updates. Bounded helper process handles SMB; no network I/O on UI/capture thread. Tests: three-PC merge, offline/reconnect, clear retry, late writer, killed I/O.
3. Clear-all increments a shared generation, removes old snapshots, and propagates to local stores on reconnect. Offline records in the prior generation are cleared on reconnect, including records made before that PC receives the clear command. This deliberately avoids wall-clock-dependent resurrection. A failed network clear is shown as pending and retried; never falsely reported complete. Concurrent clear requests supersede each other without repeated clearing.
4. Popup defaults to all PCs, newest 100 rows, filter, details, copy/export, one all-PC clear action with confirmation. Distinct PC name/id, version, stage and error context. New-error amber button. UI reads worker snapshots only. Sync at startup, new errors, manual refresh, and while popup open; no machine-data diagnostic polling.
5. Capture existing error dialogs, callback/thread exceptions, explicit background failures and MES/POP terminal errors without changing control flow. Embedded companion hook injection preserves standalone source and business payloads. Verify popup and 1000px header, existing suite, independent review, release 2026.11.05.1, public payload and old-client update notice, Drive records.

Review focus: clear with offline PC and stale in-flight snapshot; clear response lost; local error added during sync; disk/network failure must not block UI or recurse; unchanged MES/POP loops and companion save behavior.

Limit: silent hangs and native process crashes without Python exceptions are not detected. Actual company SMB / Windows MES/POP require field verification.
