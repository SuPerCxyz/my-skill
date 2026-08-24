## 1. Routing and state model

- [x] 1.1 Narrow trigger description and add operation-mode routing
- [x] 1.2 Reorder project architecture discovery before local state reuse
- [x] 1.3 Add project identity, revision, fingerprint, precise timestamps, and freshness rules
- [x] 1.4 Make completion checks plan-driven and mutation-conditional

## 2. Canonical commands

- [x] 2.1 Replace angle placeholders and duplicated forms with valid gated variables
- [x] 2.2 Fix QGA JSON quoting, libvirt URI use, path expansion, and power-state assertions
- [x] 2.3 Add dynamic disk/partition/filesystem checks and unsupported-layout stops
- [x] 2.4 Add template identity, multi-disk/NVRAM, host memory, and hotplug safety gates
- [x] 2.5 Add bounded IPv4 polling, IPv6 fallback, SSH auth branches, and host key policy

## 3. Documentation and local security

- [x] 3.1 Remove real environment data from the shared discovery guide
- [x] 3.2 Update example/local/inventory schemas without losing current VM entries
- [x] 3.3 Configure current local Git exclude entries and clarify the skill-local `.gitignore`
- [x] 3.4 Remove duplicated policies, fix bilingual headings, and reconcile README/OpenSpec

## 4. Validation

- [x] 4.1 Run quick validation, OpenSpec strict, YAML, links, punctuation, and diff checks
- [x] 4.2 Syntax-check command blocks and inspect SSH argv through a stub
- [x] 4.3 Review should-trigger and should-not-trigger examples
- [x] 4.4 Confirm the skill file set and live KVM state remain unchanged
