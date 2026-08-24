## Context

See `proposal.md` for motivation. The existing skill has a generic local-state layout and three reference documents, but its entry and environment example still describe hub/agent and specific Rocky/Fedora templates as if they were universal. The target environment exposes native libvirt tools over SSH, so command templates can be explicit without adding a new executable dependency.

## Goals / Non-Goals

**Goals:**

- Make project architecture the source of the VM set, role names, OS choice, resources, network, and service placement.
- Keep the skill entry short while making the existing references operationally copyable.
- Separate discovery commands from mutation commands and state the preconditions for each mutation.
- Preserve current local project state files, VM safety gates, 20 GiB disk behavior, 2 vCPU/1 GiB defaults, staged memory growth, QGA/IP/SSH verification, and failure preservation.

**Non-Goals:**

- Add a new command script, provider integration, or VM orchestration engine.
- Infer undocumented application semantics or automatically choose between equally plausible architectures.
- Remove support for hub/agent; they remain valid when the project architecture requires them.

## Decisions

1. **Architecture evidence before template selection.** Read project README, design/deployment files, test scripts, and existing project state before listing or selecting templates. This prevents the current node's role names from becoming a product default. A fixed role catalog was considered and rejected because it cannot represent projects that use a single VM, multiple agents, or different service boundaries.

2. **VM plan as the mutation boundary.** Derive a compact plan with VM purpose, OS, template, resources, network, services, and dependencies before clone. If a material field is ambiguous, stop at the plan stage. This is safer than discovering ambiguity after disks or domains already exist.

3. **Command templates in existing references.** Add copyable shell commands with placeholders and checks to `discovery.md`, `clone-and-resize.md`, and `verification.md`. Do not add scripts because the commands must remain visible, adaptable to the discovered node, and auditable by the model and user.

4. **Native command boundaries.** Use `virsh` for domain and runtime state, `virt-clone` for independent identity/storage, `qemu-img` for shut-off disk resize, QGA commands for guest readiness/address, and SSH for guest inspection/mutation. Use `virsh domblkinfo` for running-disk capacity because ordinary `qemu-img info` can hit libvirt's shared write lock.

5. **Architecture overrides generic resources.** Keep 2 vCPU / 1 GiB and 512 MiB escalation as generic defaults, but allow the project VM plan or local project configuration to override them. Record the source of every override in VM inventory.

## Risks / Trade-offs

- [Incomplete architecture docs] -> Stop before mutation and show missing or competing assumptions.
- [Copyable command used with stale placeholders] -> Require discovery values, quote domain/path arguments, and recheck preconditions immediately before mutation.
- [Guest OS command differences] -> Inspect tools and filesystem layout first, then select the matching guest command branch.
- [More verbose references] -> Keep `SKILL.md` as a router and place command detail only in the relevant existing reference.

## Migration Plan

1. Remove fixed role/template defaults from the environment example and generalize the entry and README.
2. Add architecture planning and concrete command contracts to existing references.
3. Validate links, YAML, frontmatter, full-width punctuation, OpenSpec, and command placeholder coverage.
4. Keep existing project-root local state and current VM inventory unchanged; future runs use architecture-derived plans.

## Open Questions

None. Hub/agent are optional roles and the project architecture is the authoritative source for the VM plan.
