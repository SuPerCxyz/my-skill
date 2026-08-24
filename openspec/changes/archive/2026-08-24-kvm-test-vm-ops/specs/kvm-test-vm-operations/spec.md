## Purpose

为真实 KVM 测试提供可重复且可审计的 hub/agent 虚拟机生命周期操作, 使节点、模板、网络和 guest 布局变化不会导致流程依赖过期记忆.

## ADDED Requirements

### Requirement: Discover and record the KVM test environment

The skill SHALL resolve the authorized KVM node dynamically and record the discovered libvirt connection, available tools, templates, disk paths, network bridge, QGA capability, and verification time. Credential values MUST NOT be written to tracked documentation.

#### Scenario: Node alias or hostname changes

- **WHEN** the configured node alias is unavailable or differs from the previous snapshot
- **THEN** the skill SHALL re-probe the authorized target and use the current node facts instead of assuming `kvm2` or a previous template name

#### Scenario: Environment snapshot is refreshed

- **WHEN** discovery succeeds
- **THEN** the skill SHALL write a human-readable snapshot and a local configuration template containing the current facts, with credentials redacted from the tracked snapshot

### Requirement: Clone hub and agent VMs without changing the source template

The skill SHALL require a powered-off source template, a non-conflicting VM name, an independent destination disk, and an explicit role before cloning. The source domain and source disk MUST remain unchanged.

#### Scenario: Safe clone succeeds

- **WHEN** the selected template is powered off, the destination name is unused, and storage checks pass
- **THEN** the skill SHALL clone the VM with a unique identity and report the destination domain, disk, role, and source template

#### Scenario: Clone precondition fails

- **WHEN** the source is running, the destination exists, the source disk is ambiguous, or storage is insufficient
- **THEN** the skill SHALL stop before mutation and report the blocking condition

### Requirement: Expand the cloned virtual disk to 20 GiB

The skill SHALL expand only the cloned disk, while the guest is powered off, to a virtual size of at least 20 GiB. It SHALL verify the resulting virtual size and SHALL distinguish sparse virtual capacity from actual host allocation.

#### Scenario: Clone disk is smaller than the target

- **WHEN** the independent clone disk is smaller than 20 GiB
- **THEN** the skill SHALL use the host disk tooling to grow that disk to 20 GiB and verify the result before boot

#### Scenario: Clone disk already meets the target

- **WHEN** the clone disk is already at least 20 GiB
- **THEN** the skill SHALL skip host resizing, retain the existing disk, and continue with guest capacity verification

### Requirement: Apply default compute sizing and staged memory escalation

The skill SHALL configure newly created test VMs with 2 vCPUs and 1 GiB memory by default. It SHALL increase memory only when a documented guest or test observation indicates memory pressure, using 512 MiB increments, checking host capacity before each change, and stopping at the configured maximum, which defaults to 4 GiB.

#### Scenario: New VM receives default resources

- **WHEN** a new hub or agent VM is cloned and no role-specific resource override is present
- **THEN** the skill SHALL persistently configure 2 vCPUs and 1 GiB memory before readiness testing

#### Scenario: Memory pressure is evidenced

- **WHEN** guest OOM evidence, guest memory pressure, or an explicitly reported memory-related test failure is observed
- **THEN** the skill SHALL increase memory by exactly 512 MiB, record the reason and previous value, and rerun the relevant readiness or test check

#### Scenario: Memory pressure is not evidenced

- **WHEN** a VM is merely slow, has delayed DHCP/QGA, or fails for a non-memory reason
- **THEN** the skill SHALL not increase memory automatically and SHALL diagnose the original failure path

#### Scenario: Memory limit or host capacity is reached

- **WHEN** the next 512 MiB increment would exceed the configured maximum or safe host capacity
- **THEN** the skill SHALL stop increasing memory, preserve the VM, and report the limit and evidence

### Requirement: Grow the guest partition and filesystem

The skill SHALL inspect the guest root disk, partition layout, filesystem, and any LVM layer after boot, then apply only a supported expansion path. It SHALL verify both block-device size and mounted root filesystem capacity.

#### Scenario: Common direct root partition expands

- **WHEN** the guest exposes a growable root partition and a supported filesystem such as XFS or ext4
- **THEN** the skill SHALL grow the partition and filesystem inside the guest and report the resulting root capacity

#### Scenario: Unsupported guest layout is detected

- **WHEN** the root layout cannot be safely mapped to a supported partition, LVM, or filesystem expansion path
- **THEN** the skill SHALL stop guest mutation, preserve the VM for diagnosis, and report the exact detected layout and missing capability

### Requirement: Verify QGA, DHCP address, and SSH access as one readiness gate

The skill SHALL wait for QGA readiness, obtain a non-loopback IPv4 address from the guest, and verify an authorized SSH login before declaring a hub or agent ready. It SHALL record the domain, MAC, address, guest identity, and verification results.

#### Scenario: Guest becomes reachable

- **WHEN** QGA responds, the address belongs to the cloned interface, and SSH authentication succeeds
- **THEN** the skill SHALL mark the VM ready and return connection details without exposing the password

#### Scenario: QGA or SSH does not become ready

- **WHEN** the configured timeout expires or only loopback/IPv6 addresses are found
- **THEN** the skill SHALL mark readiness as failed, retain the VM, and report the last QGA, address, and SSH observations

### Requirement: Prefer fresh local environment and VM inventory

The skill SHALL read the local environment record and VM inventory before broad remote discovery. It SHALL prefer a locally recorded node, domain, disk, and address after validating that the domain and disk still exist and the address is usable. It SHALL refresh the local records when they are missing, stale, or inconsistent.

#### Scenario: Local records are current

- **WHEN** the local environment and VM inventory identify an existing domain and its disk, and a lightweight validation succeeds
- **THEN** the skill SHALL use those records as the first access path and avoid an unnecessary full inventory scan

#### Scenario: Local records are stale

- **WHEN** a recorded domain, disk, node, or address cannot be validated
- **THEN** the skill SHALL perform targeted discovery, update the local records, and report which values changed

### Requirement: Allow IPv6 fallback while waiting for DHCP IPv4

The skill SHALL use a bounded retry window for guest boot, QGA, and DHCP IPv4 readiness. If a valid non-loopback IPv6 address is available before IPv4, it MAY use IPv6 SSH for interim guest verification while continuing to wait for IPv4. It MUST record both address families and their readiness times.

#### Scenario: IPv4 arrives after a delay

- **WHEN** QGA is ready but DHCP IPv4 is not yet visible
- **THEN** the skill SHALL continue polling within the configured timeout and use the IPv4 once it is available

#### Scenario: IPv6 is ready before IPv4

- **WHEN** QGA returns a usable IPv6 address and IPv4 is still pending
- **THEN** the skill MAY verify SSH over IPv6, SHALL keep the VM in a pending-IPv4 state, and SHALL not claim that DHCP IPv4 is complete

### Requirement: Protect credentials and preserve failure evidence

The skill SHALL keep secrets out of tracked skill files, command output, reports, and normal logs. It SHALL use a local permission-restricted credential source and SHALL preserve newly created VMs on failure unless the user explicitly requests cleanup.

#### Scenario: Credential source is missing

- **WHEN** no authorized SSH key or local credential source is available
- **THEN** the skill SHALL stop before guest mutation or SSH verification and request an authorized credential source

#### Scenario: Operation fails after VM creation

- **WHEN** clone, resize, boot, QGA, guest expansion, or SSH verification fails after a VM exists
- **THEN** the skill SHALL preserve the VM, record the failure stage, and provide the exact domain and disk for follow-up
