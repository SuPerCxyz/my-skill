## 1. Skill structure and environment records

- [x] 1.1 Create `kvm-test-vm-ops/SKILL.md` with trigger, safety gate, workflow, and file index
- [x] 1.2 Add discovery, clone/resize, and verification reference documents
- [x] 1.3 Add tracked environment example and redacted current environment snapshot
- [x] 1.4 Add local environment and VM inventory files, credential ignore rule, and update the root Skills list

## 2. Dynamic KVM workflow

- [x] 2.1 Document dynamic node, libvirt, template, storage, bridge, QGA, and tool discovery
- [x] 2.2 Document safe hub/agent clone preconditions and source-template protection
- [x] 2.3 Document 20 GiB sparse host disk expansion and actual-space checks
- [x] 2.4 Document guest partition, filesystem, and LVM expansion paths with unsupported-layout handling
- [x] 2.5 Document QGA, DHCP/IP filtering, SSH, and readiness reporting
- [x] 2.6 Document local-first freshness checks and IPv6 fallback while waiting for IPv4
- [x] 2.7 Document default 2 vCPU/1 GiB resources and evidence-based 512 MiB memory escalation up to 4 GiB

## 3. Real acceptance

- [x] 3.1 Create a unique Rocky hub VM from the confirmed template
- [x] 3.2 Create a unique Fedora agent VM from the confirmed template
- [x] 3.3 Verify both clone disks and expand them to 20 GiB when needed
- [x] 3.4 Boot both VMs and verify QGA, IPv4, guest identity, and SSH access
- [x] 3.5 Expand and verify the guest root filesystem on both VMs
- [x] 3.6 Record the resulting environment and acceptance evidence without credentials
- [x] 3.7 Update local environment and VM inventory files with final address-family and readiness results

## 4. Validation and handoff

- [x] 4.1 Validate OpenSpec artifacts and reconcile tasks with implementation
- [x] 4.2 Run frontmatter, full-width punctuation, internal-link, and Markdown checks
- [x] 4.3 Review the final workflow against the confirmed behavior checklist and report unverified items
