## Context

See `proposal.md` for motivation and `specs/kvm-test-vm-operations/spec.md` for observable behavior. The current test node exposes libvirt through SSH and provides `virsh`, `virt-clone`, `qemu-img`, a bridge-backed test network, QGA channels, and templates with different guest operating systems and disk sizes.

## Goals / Non-Goals

**Goals:**

- Keep the workflow portable across KVM node aliases, template names, storage paths, bridge names, and guest filesystem layouts.
- Make host-side disk growth and guest-side capacity growth separate, observable, and reversible at the VM level.
- Use QGA for readiness and address discovery, then use SSH for guest inspection and filesystem expansion.
- Keep stable environment facts easy to refresh while keeping credentials outside tracked files.

**Non-Goals:**

- Reconfigure libvirt, DHCP, bridges, templates, or host services.
- Build a general VM provisioning system or automate application deployment inside hub/agent VMs.
- Delete failed VMs automatically or manage production resources.

## Decisions

1. **SSH plus native libvirt tooling.** Use the authorized SSH entry point and run `virsh`, `virt-clone`, and `qemu-img` on the target node. This matches the available environment and avoids introducing a dependency on a particular libvirt API client. The skill may use a libvirt API or MCP only when the current environment explicitly provides and authorizes it.

2. **Discovery before mutation.** Resolve the node, connection, templates, source disk, storage pool, bridge, QGA channel, and available capacity before creating a domain. This prevents current names such as `kvm2` or one observed template from becoming hidden contract values.

3. **`virt-clone` for domain identity and `qemu-img resize` for capacity.** `virt-clone` creates an independent disk and regenerates domain identity. Host capacity growth happens only after the destination disk is identified and the guest is off. The target is virtual size 20 GiB; sparse allocation is documented and checked rather than assumed to consume zero storage.

4. **Default resources and bounded escalation.** Override the cloned domain to 2 vCPUs and 1 GiB memory before boot. Treat 512 MiB as the only automatic increment and 4 GiB as the default ceiling. Apply live and persistent memory changes when supported; otherwise apply them while shut off before the next boot. Do not scale on generic slowness.

5. **QGA for discovery, SSH for guest mutation.** QGA is the least invasive way to wait for a booted guest and obtain interface information. Guest expansion uses SSH because QGA command availability differs between templates and may not expose `guest-exec` consistently.

6. **Layout-driven guest expansion.** Inspect `findmnt`, `lsblk`, filesystem type, and LVM metadata. Handle common direct-partition XFS/ext4 and LVM paths explicitly. Stop with a diagnostic for an unmapped layout instead of applying a guessed command.

7. **Local-first state with tracked reference.** Read ignored `environment.local.yaml` and `vm-inventory.local.yaml` before broad discovery, validate their domain/disk/address references, and refresh them when stale. Keep a tracked, redacted snapshot and example configuration as documentation only. Actual local credentials remain in an ignored, permission-restricted source or use an SSH key/environment secret.

8. **Dual-stack readiness.** Use a bounded QGA/IP polling loop that prefers target-subnet IPv4 but can use a valid IPv6 address for interim SSH access. Keep IPv4 pending until DHCP/guest interface data confirms it, because IPv6 readiness does not prove DHCP IPv4 readiness.

## Risks / Trade-offs

- [Sparse disk growth can still consume host space later] -> Check free space before clone and resize, report virtual and actual sizes separately, and avoid preallocation.
- [Guest filesystem layouts vary] -> Detect the layout, support explicit common paths, and preserve the VM when unsupported.
- [QGA may be connected but not fully useful] -> Use QGA only for readiness/address discovery and use SSH for guest inspection.
- [Network lease lookup may not be available on a bridge outside libvirt DHCP] -> Prefer QGA interface data and use bridge/subnet filtering instead of relying on `virsh net-dhcp-leases`.
- [Credentials can leak through command lines or logs] -> Prefer SSH keys, source passwords from restricted local storage, redact reports, and never print secret values.
- [Local state can be stale] -> Validate domain, disk, node, and address before reuse, then refresh only the affected records.
- [IPv6 can hide a slow or broken IPv4 path] -> Record address-family-specific readiness and retain a pending IPv4 state until the configured timeout.
- [Low default memory can cause real guest or test failures] -> Require evidence before escalation, use 512 MiB increments, check host capacity, and stop at the configured maximum.

## Migration Plan

1. Add the skill, tracked environment example, and redacted current snapshot.
2. Run static skill validation and OpenSpec validation.
3. Create one hub and one agent with unique names on the authorized test node.
4. Execute host resize, guest resize, QGA/IP/SSH readiness checks, and record results.
5. If validation fails, preserve the created domains and use the recorded disk/layout evidence for diagnosis. No rollback deletes resources automatically.

## Open Questions

None. Template and role defaults were confirmed as Rocky hub and Fedora agent for the real acceptance run.
