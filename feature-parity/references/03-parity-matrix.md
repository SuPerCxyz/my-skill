# Parity Matrix Rules

The matrix is the control plane. Maintain one authoritative copy.

## Required columns
- ID
- Feature / observable behavior
- Scope
- Reference evidence
- Target evidence
- Status
- Verification
- Notes / divergence

## Status semantics

### Missing
No target implementation for the behavior.

### Partial
Temporary unfinished state: some required behavior matches and some does not. State the exact gap. It never counts as done and cannot satisfy a completion gate. Before verification completion, split further when the remaining gap is independently testable.

### Implemented
Target behavior exists and concrete target evidence is recorded. This does not imply verified parity; verification must also pass.

### Blocked
In scope and desired, but a constraint prevents completion. Record blocker, consequence, and required resolution. `Blocked` is incomplete, never automatically accepted, and prevents a full-parity claim.

### Out-of-scope
Discovered behavior excluded by the declared task scope. Record the scope reason.

### Intentional divergence
Target deliberately differs from an in-scope reference behavior. Record target behavior/rationale and obtain user acceptance when material. A blocked behavior accepted as a permanent difference must be explicitly reclassified here.

## Matrix invariants
1. Every in-scope atomic leaf appears exactly once.
2. Parent rows never hide child gaps.
3. `Implemented` requires target evidence.
4. Final parity requires verification, not only implementation.
5. Every in-scope row has reference evidence.
6. New discoveries get rows immediately.
7. Never delete rows to improve completion; change scope/status with rationale.

## Coverage
Report raw counts plus:
`strict completion = verified implemented leaves / all in-scope non-divergence leaves`.

Exclude `Partial`, `Missing`, `Blocked`, and unverified `Implemented` from the numerator.

## Parent summaries
A parent is complete only when every in-scope descendant is verified `Implemented` or an accepted `Intentional divergence`. Prefer leaf counts over hand-maintained percentages.
