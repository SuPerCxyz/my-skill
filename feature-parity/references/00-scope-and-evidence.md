# Scope, Revisions, and Evidence

## 1. Pin comparison points
Record:
- reference repository/path, branch/tag, exact commit SHA;
- target repository/path, branch, baseline commit;
- requested scope and date.

The pinned reference revision is authoritative for the current parity run. If reference or target changes during work, record the new revision and revalidate affected evidence. Do not silently switch to a newer upstream revision unless the user asked to track latest/upstream.

## 2. Parity dimensions
Assess only relevant dimensions, but never assume “feature parity” means UI alone.

- Functional: available capabilities.
- Behavioral: inputs, outputs, transitions, side effects, failures.
- API: routes, methods, payloads, errors, pagination, idempotency.
- CLI: commands, arguments, defaults, output, exit codes.
- UI: navigation, controls, states, accessibility, visual feedback.
- Data: schema semantics, lifecycle, migrations, serialization/export.
- Integration: protocols, providers, retries, auth, webhooks/events.
- Operational: config, startup, health, logs, jobs, recovery, upgrades.

## 3. Evidence hierarchy
Prefer, in order:
1. reproducible runtime/black-box observation;
2. automated tests/fixtures;
3. executable source path plus registration/wiring;
4. schema/migration/config definitions;
5. official docs/examples;
6. screenshots/issues/changelog as discovery clues.

When stronger evidence is available, documentation alone must not establish that behavior exists in the pinned revision.

## 4. Evidence format
Use concrete locators: `path:line-range`, test name, route/command name, runtime command + observed result, or stable permalink. Record what the evidence proves, not merely where it is.
