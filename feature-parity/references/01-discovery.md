# Reference Discovery

Optimize for recall: discover feature surfaces before assuming how the system works.

## Pass 1 — Repository map
Identify languages/frameworks, apps/packages, frontend/backend boundaries, build/deploy files, generated/vendor code, tests, docs, examples, plugins/extensions.

## Pass 2 — Registration surfaces
Locate:
- routes/pages/navigation/menu definitions;
- API routers/controllers/handlers/OpenAPI;
- CLI registration;
- dependency/provider registries;
- events/topics/queues/jobs/schedulers;
- configuration and feature flags;
- plugin/extension hooks;
- migrations and model registries.

Registration points often reveal features omitted from README files.

## Pass 3 — Trace representative flows
For each major capability trace:
`entry → validation → orchestration → domain logic → persistence/external call → result/event → user feedback`.

Apply the failure/recovery decomposition axes from `02-feature-decomposition.md` rather than stopping at the happy path.

## Pass 4 — Tests as behavior index
Search tests/fixtures for ordering, dedupe, limits, fallback, malformed input, races, lifecycle cleanup, permissions, compatibility, retries, and recovery. Tests often expose hidden subfeatures.

## Pass 5 — Public/historical clues
Use README, docs, examples, changelog, screenshots, and issues to discover candidates, then verify them against the pinned revision.

## Search heuristics
Search feature nouns/verbs plus:
`create update delete retry timeout cancel recover restore import export sync refresh enable disable archive duplicate conflict permission validation default limit sort filter search pagination webhook event job migration`.

For UI-heavy systems also search labels, route names, dialog titles, action IDs, keyboard shortcuts, and empty/error/loading strings.

## Discovery output
For each candidate record its name, surfaces, likely entrypoint, relevant files/tests, and whether verified or suspected. Suspected behavior cannot become a parity claim until verified.
