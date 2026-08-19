# Behavioral Verification

Verify whether the target behaves like the pinned reference revision, not whether its code looks similar.

## Preferred methods
1. **Differential black-box:** equivalent inputs against reference/target; compare outputs, state, and side effects while normalizing semantically irrelevant IDs/timestamps.
2. **Contract tests:** encode observable requests/responses, CLI results, state transitions, events, persisted records, exports.
3. **Reference-test semantic mapping:** map relevant reference tests to equivalent target tests or explain non-applicability; do not mechanically copy test code.
4. **Runtime scenarios:** exercise happy, failure, recovery, concurrency, and restart behavior.
5. **Inspection fallback:** when execution is impossible, use code-path evidence and label confidence as inspection-only.

## Minimum scenario classes
For non-trivial features consider normal, boundary/empty, invalid input, auth/permission failure, dependency timeout/failure, duplicate/repeated action, restart/recovery, concurrency, and cleanup/delete/cancel.

## Result semantics
Use `Pass`, `Fail`, `Blocked`, `Not run`, or `Not applicable` per leaf. Full-parity requirements are defined in `SKILL.md` Phase 8; its per-leaf verification requirement applies here. Inspection-only evidence must be explicitly identified when it is the strongest available method.
