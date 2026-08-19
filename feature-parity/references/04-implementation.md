# Implementation Discipline

## Preserve target-native design
Parity is behavioral, not structural. Use target conventions for routing, state, persistence, services, errors, tests, and UI unless they cannot express required behavior.

## Slice vertically
Prefer small end-to-end slices covering related feature IDs over disconnected layer-by-layer changes. Each slice should leave the target testable.

## Per-slice loop
1. Select IDs and acceptance criteria.
2. Re-read reference evidence.
3. Inspect analogous target patterns.
4. Implement the smallest coherent target-native change.
5. Add/adjust tests.
6. Run affected and appropriate regression tests.
7. Exercise runtime behavior when feasible.
8. Update target evidence/status.
9. Inspect sibling/reference behavior for newly exposed dependencies.

## Avoid false parity
None of these proves parity:
- same function/component name;
- same button without equivalent state behavior;
- endpoint existence without payload/error semantics;
- happy-path-only tests when failure/recovery exists;
- mocks where the reference has durable side effects;
- TODO/stub/placeholder paths.

## Data/integrations
For schema/state changes include migration, upgrade/backward compatibility, and cleanup. For integrations capture provider selection, auth, retries, timeout, idempotency, limits, callbacks/events, degraded mode, and secret/config handling.

## Legal/provenance boundary
Default to independent implementation from behavioral/spec evidence. Do not paste distinctive reference implementation code merely to accelerate parity. If licensed code reuse is explicitly requested, handle license, notices, attribution, compatibility, and project policy as a separate provenance-aware decision.
