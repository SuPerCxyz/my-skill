## Why

The current KVM skill is structurally valid but contains command templates that fail Shell parsing, contradictory IPv6 guidance, over-broad trigger and workflow routing, stale shared environment data, and completion rules that force unnecessary mutations. These issues can waste time and token budget or cause a weaker model to operate the wrong resource.

## What Changes

- Narrow automatic triggering to project-scoped test VM provisioning and validation, with explicit exclusions for production, OpenStack-managed instances, and generic libvirt diagnosis.
- Route inspect/reuse, provision, resize/reconfigure, and verify-only requests separately so read-only work never enters clone implicitly.
- Identify the actual project and architecture evidence before reusing project-local VM state, and bind state to project identity, revision, architecture fingerprint, and precise timestamps.
- Replace broad technology keyword searches with bounded discovery of entry files that actually exist; do not assume any stack, deployment system, or VM role.
- Replace invalid placeholders and duplicated command forms with one canonical, syntax-checked remote command contract using validated variables and the discovered libvirt URI.
- Make disk, CPU, memory, guest expansion, QGA, IPv4/IPv6, SSH authentication, host key, and failure handling plan-driven and state-checked.
- Keep IPv4 primary and use validated IPv6 only as a fallback when IPv4 is unavailable within the configured wait policy.
- Repurpose the shared environment discovery document as a generic schema/freshness guide, keep real environment state project-local, and protect local state from Git tracking.
- Align README, headings, environment schema, OpenSpec, and completion semantics without adding or deleting skill files.

## Capabilities

### New Capabilities

无.

### Modified Capabilities

- `kvm-test-vm-operations`: Harden routing, state identity/freshness, canonical commands, plan-driven mutations, IPv6 fallback, credential safety, and completion semantics.

## Impact

- Modifies existing `kvm-test-vm-ops` entry, references, README, environment example, discovery guide, local project state schema, and local Git exclude settings.
- Updates the existing KVM OpenSpec behavior contract and archives this change when validation completes.
- Does not add or delete skill files, install dependencies, or execute KVM/libvirt mutations.
