## MODIFIED Requirements

### Requirement: Discover and record the KVM test environment

The skill SHALL bind environment records to an explicit project identity, root, revision, architecture fingerprint, authorized KVM node, libvirt URI, and precise verification timestamp. It SHALL separate stable metadata from volatile facts and MUST refresh template state, VM state, addresses, host free memory, storage free space, and disk capacity before any mutation. Real environment facts MUST remain in project-local files rather than the shared skill package.

#### Scenario: Node alias or hostname changes

- **WHEN** the configured node alias is unavailable, resolves to a different host, or differs from the project-local identity
- **THEN** the skill SHALL stop state reuse, re-probe the authorized target, and update the project-local record only after identity validation

#### Scenario: Environment discovery record is refreshed

- **WHEN** discovery succeeds
- **THEN** the skill SHALL update the project-local environment record with ISO 8601 timestamps and SHALL keep the shared discovery document free of real host, IP, path, template, or VM values

### Requirement: Clone project-defined VMs without changing the source template

The skill SHALL clone only in provision mode and only for VMs present in the confirmed project plan. It SHALL assert a powered-off, generalized single-disk template, a non-conflicting destination, independent storage, sufficient capacity, a supported disk target, and no unhandled NVRAM or multi-disk requirement. The source domain and source disk MUST remain unchanged.

#### Scenario: Architecture requires a custom VM set

- **WHEN** the confirmed project plan identifies one or more VM purposes with OS, network, resource, and service-boundary requirements
- **THEN** the skill SHALL clone only those planned VMs using templates verified to match the plan

#### Scenario: Architecture does not require hub or agent

- **WHEN** the project plan has no hub or agent role
- **THEN** the skill SHALL not create hub or agent VMs from historical inventory or skill examples

#### Scenario: Safe clone succeeds

- **WHEN** every clone precondition is asserted and the destination domain, disk, UUID, MAC, and guest identity are independently verified
- **THEN** the skill SHALL record the clone as created and preserve its source relation

#### Scenario: Clone precondition fails

- **WHEN** the template is running or un-generalized, the destination exists, storage is insufficient, disk mapping is ambiguous, or multi-disk/NVRAM handling is required
- **THEN** the skill SHALL stop before mutation and report the exact blocking state

### Requirement: Expand the cloned virtual disk to 20 GiB

The skill SHALL use the VM plan disk target, which defaults to 20 GiB, and SHALL expand only an independent destination disk while the domain is shut off. It SHALL skip resizing when capacity already meets or exceeds the planned target, and SHALL use libvirt runtime inspection rather than ordinary direct image inspection for running domains.

#### Scenario: Clone disk is smaller than the target

- **WHEN** the shut-off destination disk is independent and smaller than the planned target
- **THEN** the skill SHALL grow it to the planned target and verify virtual and allocated capacity before boot

#### Scenario: Clone disk already meets the target

- **WHEN** the destination disk already meets or exceeds the planned target
- **THEN** the skill SHALL record `already_satisfied`, skip host resizing, and continue without a no-op mutation

### Requirement: Apply default compute sizing and staged memory escalation

The skill SHALL use project-plan CPU and memory values, falling back to 2 vCPUs and 1 GiB only when no override exists. It SHALL verify domain maximums and host capacity before configuration. Memory escalation SHALL require documented evidence, use 512 MiB steps by default, separate live and persistent updates, verify each result, and stop at the configured or safe host limit.

#### Scenario: New VM receives default resources

- **WHEN** provision mode requires a new VM and the project plan has no resource override
- **THEN** the skill SHALL configure and verify the fallback resource values without assuming the template inherited them

#### Scenario: Project architecture overrides resources

- **WHEN** the confirmed project plan specifies resource values
- **THEN** the skill SHALL use those values and record the evidence source and domain maximum checks

#### Scenario: Memory pressure is evidenced

- **WHEN** OOM, sustained guest pressure, or an explicit memory-related test failure is correlated to the failed workload
- **THEN** the skill SHALL verify host free memory, attempt one configured step, persist configuration separately from any live change, and rerun the failed check

#### Scenario: Memory pressure is not evidenced

- **WHEN** the symptom is DHCP, QGA, SSH, storage, application, or generic startup delay without memory evidence
- **THEN** the skill SHALL not increase memory and SHALL continue diagnosis in the relevant path

#### Scenario: Memory limit or host capacity is reached

- **WHEN** the next step exceeds the project maximum, domain capability, or safe host capacity
- **THEN** the skill SHALL stop escalation, preserve the VM, and record the limiting value

### Requirement: Grow the guest partition and filesystem

The skill SHALL inspect the actual root source, parent disk, partition number, filesystem, LVM mapping, and required guest tools. It SHALL grow guest storage only when host capacity increased and the guest does not already use the planned capacity. It SHALL branch explicitly for supported direct XFS, direct ext-family, and supported LVM layouts.

#### Scenario: Common direct root partition expands

- **WHEN** a direct root partition is the growable final partition, required tools exist, and its filesystem is supported
- **THEN** the skill SHALL grow the discovered partition and matching filesystem, then verify block and mounted capacity

#### Scenario: Unsupported guest layout is detected

- **WHEN** the root layout is ambiguous, encrypted, unsupported, not last, multi-device, or lacks required tools
- **THEN** the skill SHALL stop guest mutation, preserve the VM, and report the discovered layout and missing prerequisite

### Requirement: Verify QGA, DHCP address, and SSH access as one readiness gate

The skill SHALL apply readiness checks only to the selected operation mode. It SHALL use the discovered libvirt URI, correctly quoted QGA JSON, bounded polling with connect timeouts and success exit, MAC/interface correlation, and separate key/password SSH paths. Verify-only and inspect/reuse modes MUST NOT imply clone or resize.

#### Scenario: Project-defined guest becomes reachable

- **WHEN** QGA responds, a validated address belongs to the planned interface, and authorized SSH succeeds
- **THEN** the skill SHALL record guest identity, address family, authentication mode, and readiness without exposing secrets

#### Scenario: Architecture or network evidence is insufficient

- **WHEN** the plan cannot identify the expected interface/network or an address cannot be correlated to the destination MAC
- **THEN** the skill SHALL stop readiness classification and report the missing evidence

#### Scenario: Guest becomes reachable

- **WHEN** the selected mode requires readiness and the planned readiness checks succeed
- **THEN** the skill SHALL mark only that VM and requested mode complete

#### Scenario: QGA or SSH does not become ready

- **WHEN** the configured deadline expires without a valid access path
- **THEN** the skill SHALL return a non-success readiness result, preserve the VM, and report the last QGA, address, and SSH state

### Requirement: Prefer fresh local environment and VM inventory

The skill SHALL identify and fingerprint the target project before reading its local environment and inventory. It SHALL reuse records only when project identity and semantic plan match, and SHALL always refresh volatile facts immediately before mutation.

#### Scenario: Local records are current

- **WHEN** project identity, revision/fingerprint, VM purpose, domain/disk identity, and requested mode remain compatible
- **THEN** the skill SHALL reuse stable records and perform only the mode-specific freshness checks

#### Scenario: Local records are stale

- **WHEN** project identity differs, architecture changed materially, or any referenced resource cannot be validated
- **THEN** the skill SHALL prevent implicit reuse, perform targeted discovery, and record the changed fields

### Requirement: Allow IPv6 fallback while waiting for DHCP IPv4

The skill SHALL treat planned IPv4 as the primary access path. It SHALL poll until the configured IPv4 deadline and SHALL use IPv6 only when IPv4 remains unavailable and a global IPv6 or correctly scoped link-local IPv6 is validated against the destination interface. It MUST record the access family, fallback reason, and family-specific readiness timestamps.

#### Scenario: IPv4 arrives after a delay

- **WHEN** QGA is ready and IPv4 appears within the configured wait policy
- **THEN** the skill SHALL use IPv4 and SHALL not switch to IPv6 merely because IPv6 appeared first

#### Scenario: IPv6 is ready before IPv4

- **WHEN** IPv4 remains unavailable according to policy and a validated IPv6 path is reachable
- **THEN** the skill SHALL use IPv6 as fallback, record `pending_ipv4` and the fallback reason, and SHALL use interface scope for link-local addresses

### Requirement: Protect credentials and preserve failure evidence

The skill SHALL keep secrets out of tracked files, argv, reports, and normal logs. It SHALL verify that project-local state is ignored by Git before storing credential references, use mode `0600`, separate key and password authentication commands, and isolate test guest host keys from unrelated known-host entries. Failed resources SHALL be preserved unless cleanup is separately authorized.

#### Scenario: Credential source is missing

- **WHEN** the selected SSH authentication mode lacks an authorized key or protected local secret source
- **THEN** the skill SHALL stop before SSH-dependent mutation and request the missing authorized source

#### Scenario: Operation fails after VM creation

- **WHEN** any clone, resource, storage, boot, QGA, address, SSH, or guest step fails after creation
- **THEN** the skill SHALL preserve the destination, record the precise failed gate and last verified state, and SHALL not clean up without separate authorization

### Requirement: Build a VM plan from project architecture

The skill SHALL inspect only actual project entry files and deployment/test configuration selected from a bounded file inventory. It SHALL not assume or search for a technology, deployment system, or VM role absent from the project evidence and user request. The plan SHALL identify VM purpose, OS/template requirement, resources, disk target, network, access, and responsibility.

#### Scenario: Architecture is explicit

- **WHEN** actual project files clearly define VM boundaries and requirements
- **THEN** the skill SHALL produce a plan with evidence paths and SHALL avoid broad keyword scans

#### Scenario: Architecture is ambiguous

- **WHEN** project root, VM boundary, OS, template, network, or service placement has multiple material interpretations
- **THEN** the skill SHALL stop before mutation and request one consolidated decision

### Requirement: Provide concrete command templates for each operation stage

The skill SHALL provide one canonical remote-command form using valid gated variables, the discovered libvirt URI, safe quoting, asserted preconditions, expected results, and explicit failure status. Executable blocks MUST NOT contain angle-bracket placeholders or duplicated forms that can diverge.

#### Scenario: Model executes a standard clone flow

- **WHEN** the selected mode is provision and all variables and gates are satisfied
- **THEN** the skill SHALL expose syntax-validated commands for the exact plan without requiring invented quoting, disk mapping, or connection options

#### Scenario: Command is unsafe in the current state

- **WHEN** a power state, identity, capacity, privilege, tool, layout, auth, or capability gate fails
- **THEN** the command sequence SHALL stop nonzero before mutation and report the failed gate

#### Scenario: Runtime disk query is needed

- **WHEN** a domain is running and capacity inspection is requested
- **THEN** the skill SHALL use the discovered libvirt disk target and runtime-safe libvirt inspection rather than ordinary direct image inspection

## ADDED Requirements

### Requirement: Route requests by operation mode

The skill SHALL classify each request as inspect/reuse, provision, resize/reconfigure, or verify-only before loading detailed procedures. Cleanup SHALL require separate explicit authorization. Each mode SHALL load only relevant references and SHALL not imply mutations from another mode.

#### Scenario: Verify-only request

- **WHEN** the user asks only to validate QGA, addressing, SSH, or guest readiness
- **THEN** the skill SHALL not clone, resize, or change compute resources

#### Scenario: Provision request

- **WHEN** the user explicitly requests new project test VMs and confirms the VM plan
- **THEN** the skill MAY enter clone and provisioning after all gates pass
