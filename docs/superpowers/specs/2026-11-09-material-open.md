# Sub-PC material window startup recovery

User reports raw Errno 13 Permission denied only when opening the material popup on a sub-PC and explicitly requests a fix. Existing update publication authorization applies.

Evidence: material_ui.boot uses core.InstanceLock(sync-ui.lock). InstanceLock reads byte 0 before acquiring Windows byte lock and outside its catch; Windows mandatory locking can reject that read with bare EACCES. Existing hidden material client survives in a separate process. Each CompanionManager currently knows only processes it spawned, so a second main process or restarted parent tries a second material process instead of reusing the active one. Shared discovery errors are routed to footer events, not this startup dialog. The screenshot alone does not prove the user's exact process state.

Fix the verified lock ordering defect; reuse a live local material process/control session when opening from a new parent. Validate process lifetime to avoid PID reuse, preserve existing quick inputs and two-phase update/exit protocol, handle simultaneous launches. Recover a unique live legacy material session under the existing local companion folder. Do not kill processes, delete lock/database/settings/pending records, change collection ownership, or alter UI/design/timers/network behavior. Genuine access failures retain stage/path diagnostics instead of being mislabeled as duplicate execution.

Verify mandatory-lock reproduction, singleton exclusion and release, live/stale/ambiguous session reuse, concurrent boot race, quick channel/update exit handshakes, startup error details; run full suite, fresh review, prepare .7 and verify deployment.

Reviewed update constraint: recovered/shared sessions require graceful complete exit and restart before updating. Native owned-session update protocol remains unchanged; .6 parents cannot be assumed to preserve a shared acknowledgment after exit.
