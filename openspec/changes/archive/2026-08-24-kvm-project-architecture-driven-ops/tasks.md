## 1. Architecture-driven planning

- [x] 1.1 Remove fixed hub/agent template mappings from `environment.example.yaml`
- [x] 1.2 Update the skill entry and README to describe project-defined VM roles
- [x] 1.3 Add architecture evidence and VM plan requirements to the existing references

## 2. Concrete command templates

- [x] 2.1 Add discovery and precondition commands with dynamic placeholders
- [x] 2.2 Add clone, resource, disk resize, and runtime disk inspection commands
- [x] 2.3 Add QGA, address wait, IPv6 fallback, SSH, and guest evidence commands
- [x] 2.4 Add direct partition, XFS/ext4, and LVM command branches with safety checks
- [x] 2.5 Add memory evidence and 512 MiB staged escalation commands

## 3. Validation and handoff

- [x] 3.1 Validate OpenSpec artifacts and the modified capability
- [x] 3.2 Validate YAML, internal links, frontmatter, full-width punctuation, and diff whitespace
- [x] 3.3 Confirm no skill files were added or deleted and current project VM state is unchanged
