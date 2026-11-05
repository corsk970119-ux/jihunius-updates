# Material integration / approved requirements
Baseline: production 2026.11.05.1, uploaded MaterialCounter 0.4.1.
Owner: one local SQLite writer/collector; clients submit authenticated commands. No shared SQLite or automatic ownership takeover.
Collection switch persists per PC, defaults OFF. Owner collector resumes on host launch, popup hide does not stop collection. Sub PC OFF can enter defects and rotate through owner.
Preserve original counting, exclusions, stock, undo, periods, CSV, backups, diagnostic and reset behavior. Reject stale material/undo/stock/reset operations; requests and receipts commit atomically.
No publication until user asks. No Drive work records requested.

Tasks:
1. Store transaction and durable idempotency / conflicts / reset tests.
2. Authority service, discovery, client pending journal and async synchronization, two-client / restart / OFF tests.
3. Original popup UI integration, async mutations/read reports, shutdown/update/window state, host tab. Private packaging.
4. Full regression and native Tk visual checks; fresh final review and required fixes; deliver candidate file.

Review focus: lost acknowledgements, original state machine correctness, old queued commands after reset/rotate, stopped collection, shared-folder delays, active/hide/full-exit/update lifecycle, incomplete report display, private-build updater isolation. No claims of Windows/company-network verification.
