# Feature Decomposition

Turn broad capabilities into atomic observable contracts. “Supports X” is not atomic.

## Decomposition axes
For every feature ask all applicable questions.

### Entry and visibility
Exposure point; role/mode/flag/platform/resource-state prerequisites.

### Inputs
Required/optional fields, defaults, limits, formats, normalization, validation timing, duplicates.

### State machine
Initial/valid/invalid/terminal states, restart/recovery, concurrency semantics.

### Core behavior
Calculation/routing/selection, ordering, filtering, batching, dedupe, cache, fallback, provider choice.

### Side effects
Database/filesystem/network effects, events, notifications, spawned work, audit records.

### Outputs
Return/API payload, CLI output/exit code, UI state, progress, logs, export/download artifacts.

### Failure behavior
Errors/status codes, retry/backoff, timeout, partial success, rollback/cleanup, cancellation, dependency failure, user recovery.

### Lifecycle
Create/read/update/delete plus enable/disable, pause/resume, cancel/retry, archive/restore, import/export when meaningful.

### Operational/config behavior
Config defaults, env vars, reload semantics, feature flags, health/startup validation, migrations/upgrades.

## Atomic leaf test
A final leaf is atomic only when all are true:
- one concise behavior statement describes it;
- one acceptance test can decide it;
- its status can change independently of siblings;
- evidence can point specifically to it.

If not, split further.

`Partial` semantics are defined in `03-parity-matrix.md`. A leaf must be split until each remaining unmet behavior is independently testable. `Partial` is transitional and must not remain at completion; resolve it to another status defined there before any completion claim.

## Stable IDs
Use hierarchical IDs when useful:
- `F-001` major capability
- `F-001.1` subfeature
- `F-001.1a` atomic behavior

Avoid renumbering established IDs; append IDs for newly discovered behaviors.

## Hidden-feature prompts
For each visible button/endpoint/command ask: what hides/disables it, what happens on repeat/concurrent invocation, what persists or survives restart, what is cleaned up, where permission boundaries apply, what happens when dependencies fail, and whether empty/large/legacy data changes behavior.
