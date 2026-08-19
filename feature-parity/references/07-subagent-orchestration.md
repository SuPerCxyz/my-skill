# Sub-agent Orchestration

Use parallel agents only when they reduce discovery blind spots or context pressure.

## Roles
- **Locator:** where behavior is registered/exposed.
- **Analyzer:** end-to-end trace of a feature.
- **Pattern finder:** analogous flows, edge cases, tests, conventions.
- **Surface auditor:** independent UI/API/CLI/config/job/integration enumeration.
- **Verifier:** checks target behavior against defined feature IDs.

## Rules
1. Main agent owns scope, stable IDs, authoritative matrix, synthesis, and final decisions.
2. Discovery agents are read-only unless explicitly assigned an implementation slice.
3. Give agents disjoint focus areas; avoid redundant summaries.
4. Require concrete path/line/test/runtime evidence.
5. Reject evidence-free “looks complete” conclusions.
6. Reconcile the matrix only after all results in the current discovery wave are available.
7. Reuse existing agent/session context when supported rather than restarting equivalent research.
8. Respect host/user concurrency limits.

## Useful partitions
UI/routes; backend/API/domain; persistence/schema/migrations; jobs/events/recovery; integrations/config; tests/fixtures/edge cases.

## Independent omission audit
At least one final audit pass must search the reference without relying on existing matrix categories, otherwise it tends to reproduce the same blind spots.
