## MODIFIED Requirements

### Requirement: Clone hub and agent VMs without changing the source template

The skill SHALL derive each destination VM from the current project's architecture and test plan. It SHALL require a powered-off source template, a non-conflicting VM name, an independent destination disk, and an explicit project-defined purpose before cloning. `hub` and `agent` SHALL be treated as optional role names rather than defaults, and the source domain and source disk MUST remain unchanged.

#### Scenario: Architecture requires a custom VM set

- **WHEN** the project architecture identifies one or more VM roles with operating-system and service requirements
- **THEN** the skill SHALL create only the required roles using matching discovered templates and SHALL record the project-specific plan

#### Scenario: Architecture does not require hub or agent

- **WHEN** the project architecture has no hub or agent dependency
- **THEN** the skill SHALL not create hub or agent VMs merely because the skill supports those role names

#### Scenario: Safe clone succeeds

- **WHEN** the selected template is powered off, the destination name is unused, and storage checks pass
- **THEN** the skill SHALL clone the VM with a unique identity and report the destination domain, disk, purpose, and source template

#### Scenario: Clone precondition fails

- **WHEN** the source is running, the destination exists, the source disk is ambiguous, or storage is insufficient
- **THEN** the skill SHALL stop before mutation and report the blocking condition

### Requirement: Apply default compute sizing and staged memory escalation

The skill SHALL configure each newly created project-defined test VM with 2 vCPUs and 1 GiB memory by default unless the architecture plan or project configuration specifies an override. It SHALL increase memory only when a documented guest or test observation indicates memory pressure, using 512 MiB increments, checking host capacity before each change, and stopping at the configured maximum, which defaults to 4 GiB.

#### Scenario: New VM receives default resources

- **WHEN** a new VM is required and no architecture or project resource override is present
- **THEN** the skill SHALL persistently configure 2 vCPUs and 1 GiB memory before readiness testing

#### Scenario: Project architecture overrides resources

- **WHEN** the architecture plan explicitly requires different CPU or memory resources
- **THEN** the skill SHALL apply the explicit override and record its source instead of applying the generic default

#### Scenario: Memory pressure is evidenced

- **WHEN** guest OOM evidence, guest memory pressure, or an explicitly reported memory-related test failure is observed
- **THEN** the skill SHALL increase memory by exactly 512 MiB, record the reason and previous value, and rerun the relevant readiness or test check

#### Scenario: Memory pressure is not evidenced

- **WHEN** a VM is merely slow, has delayed DHCP/QGA, or fails for a non-memory reason
- **THEN** the skill SHALL not increase memory automatically and SHALL diagnose the original failure path

#### Scenario: Memory limit or host capacity is reached

- **WHEN** the next 512 MiB increment would exceed the configured maximum or safe host capacity
- **THEN** the skill SHALL stop increasing memory, preserve the VM, and report the limit and evidence

### Requirement: Verify QGA, DHCP address, and SSH access as one readiness gate

The skill SHALL wait for QGA readiness, obtain a non-loopback address appropriate to the project's network plan, and verify an authorized SSH login before declaring a project-defined VM ready. It SHALL record the domain, MAC, address-family state, guest identity, and verification results.

#### Scenario: Project-defined guest becomes reachable

- **WHEN** QGA responds, an address matches the planned interface or network, and SSH authentication succeeds
- **THEN** the skill SHALL mark that VM ready and return connection details without exposing the password

#### Scenario: Architecture or network evidence is insufficient

- **WHEN** the project plan does not identify a usable interface or the discovered address cannot be mapped to the cloned VM
- **THEN** the skill SHALL stop readiness validation and report the missing architecture or network evidence

#### Scenario: Guest becomes reachable

- **WHEN** QGA responds, an address belongs to the planned interface, and SSH authentication succeeds
- **THEN** the skill SHALL mark that VM ready and return connection details without exposing the password

#### Scenario: QGA or SSH does not become ready

- **WHEN** the configured timeout expires or only unusable addresses are found
- **THEN** the skill SHALL mark readiness as failed, retain the VM, and report the last QGA, address, and SSH observations

## ADDED Requirements

### Requirement: Build a VM plan from project architecture

The skill SHALL inspect project architecture evidence before creating VMs and SHALL produce a plan containing only required VM roles, operating-system requirements, selected templates, resources, networks, service responsibilities, and inter-VM dependencies. It MUST ask for clarification or stop when a material requirement cannot be inferred safely.

#### Scenario: Architecture is explicit

- **WHEN** project documentation or deployment/test configuration identifies the required services and their VM boundaries
- **THEN** the skill SHALL convert that evidence into a VM plan before any clone mutation

#### Scenario: Architecture is ambiguous

- **WHEN** multiple operating systems, templates, network topologies, or service placements are plausible
- **THEN** the skill SHALL show the competing assumptions and request a decision instead of creating a guessed VM set

### Requirement: Provide concrete command templates for each operation stage

The skill SHALL provide executable command templates for discovery, precondition checks, clone, resource configuration, disk resize, boot, QGA/IP lookup, SSH verification, guest filesystem expansion, and evidence collection. Each mutating command MUST identify its required placeholders, power state, expected result, and safe failure handling.

#### Scenario: Model executes a standard clone flow

- **WHEN** the VM plan and discovered values are available
- **THEN** the skill SHALL expose copyable commands using those values for `virsh`, `virt-clone`, `qemu-img`, QGA, and SSH without requiring the model to invent command syntax

#### Scenario: Command is unsafe in the current state

- **WHEN** a command requires a shut-off guest, a different libvirt connection, or a guest-specific filesystem tool that is not present
- **THEN** the skill SHALL state the precondition, provide the safe alternative or diagnostic command, and prevent blind execution

#### Scenario: Runtime disk query is needed

- **WHEN** a domain is running and disk capacity must be checked
- **THEN** the skill SHALL use the libvirt runtime-safe inspection command and SHALL not instruct direct ordinary `qemu-img info` against a disk held by a running guest
