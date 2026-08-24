## Context

The skill has one concise entry and three detailed references, but command duplication has already produced divergent quoting, runtime files are project-local without effective ignore protection, and the workflow treats provisioning as universal. The user requires existing skill files to remain, IPv6 to be fallback-only, and architecture discovery to use only technologies actually present in the target project.

## Goals / Non-Goals

**Goals:**

- Make every executable command block valid Shell after loading validated variables.
- Make operation mode, project identity, architecture evidence, VM plan, and mutation authorization explicit.
- Keep one canonical remote-command form and use the discovered libvirt URI consistently.
- Treat 20 GiB and 2 vCPU/1 GiB as overridable defaults, and avoid no-op guest mutations.
- Preserve current local VM entries while migrating their schema.

**Non-Goals:**

- Add helper scripts or new skill files.
- Execute real KVM operations during this documentation hardening change.
- Support production VM management, OpenStack-managed instances, generic libvirt incident diagnosis, arbitrary multi-disk cloning, or automatic template sysprep without separate authorization.

## Decisions

1. **Mode first.** Select inspect/reuse, provision, resize/reconfigure, or verify-only before reading mutation references. Cleanup remains an explicit external authorization path.

2. **Architecture before state reuse.** Resolve the user-selected project root, inspect a bounded set of existing entry files, compute a project/revision/fingerprint identity, then validate local environment and inventory against that identity. Stable connection metadata can be reused; VM state, IP, free space, template state, and disk capacity are always refreshed before mutation.

3. **No assumed technology list.** Enumerate candidate top-level and known project entry files, then inspect only what exists. Do not search broad terms such as `service`, `test`, `hub`, `agent`, or name technologies that are absent.

4. **Canonical variable contract.** Executable blocks use valid `KVM_*` variables with `${VAR:?}` gates, never angle-bracket placeholders. Remote `virsh` uses the discovered URI consistently. Shell snippets are syntax-checked and argv-tested with an SSH stub.

5. **Plan-driven state assertions.** Mutation commands assert template/domain power state, destination absence, storage and host memory, disk format/target count, NVRAM/multi-disk boundaries, guest tool availability, and filesystem layout. Unsupported states stop with evidence.

6. **IPv4 primary, IPv6 fallback.** Poll QGA and IPv4 until a bounded deadline. A validated global IPv6 or scoped link-local IPv6 is used only when IPv4 remains unavailable according to policy. Inventory records family, reason, and readiness timestamps.

7. **Project-local security.** Real state stays in project-root local files with mode `0600`, project identity, and Git-ignore verification. The shared discovery document contains schema and freshness guidance only. Password authentication and key authentication have separate commands; secrets never enter argv.

## Risks / Trade-offs

- [No helper script under the existing file constraint] -> Keep one canonical command form and validate every block with an ad hoc extraction/stub harness.
- [Project root can be ambiguous in a monorepo] -> Require the target project root to be explicit when the current working tree has multiple plausible projects.
- [Template identity hygiene varies] -> Inspect clone identity and stop for un-generalized templates; do not run sysprep without separate authorization.
- [Live memory hotplug often fails] -> Separate live and persistent operations and fall back to controlled reboot only when authorized.

## Migration Plan

1. Rewrite existing entry/reference documents and generic environment schema in place.
2. Migrate current project-local state with project identity and precise timestamps while preserving VM records.
3. Add local exclude entries for the current repository and document ignore verification for future projects.
4. Validate OpenSpec, skill structure, headings, YAML, links, command syntax/argv, and trigger boundary examples.
5. Archive the change and reconcile the main specification.

## Open Questions

None. IPv6 is fallback-only, no specific deployment technology is assumed, and no live KVM mutation is authorized for this change.
