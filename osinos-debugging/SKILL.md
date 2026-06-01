---
name: openstack-env-debugging
description: Use when debugging OpenStack services deployed on Kubernetes via SSH jump hosts. Covers SSH access chain, OpenStack CLI auth from busybox pod, configmap editing, pod restart, manual service debugging with sleep 10d pattern, and fluentd log search.
---

# OpenStack K8s Environment Debugging

## Overview

OpenStack services run on Kubernetes (Helm-deployed) in the `openstack` namespace.
Debugging requires SSH through a jump host, then `kubectl` to interact with pods.

## Quick Reference — File Index

| When you need... | Read |
|------------------|------|
| SSH access, local openstack client setup | [access.md](access.md) |
| OpenStack CLI auth, busybox pod, admin credentials | [auth.md](auth.md) |
| Service list, pod names, OVN networking, Helm releases, code repo layout | [services.md](services.md) |
| Multi-container pods, label selectors, StatefulSet vs Deployment | [pods.md](pods.md) |
| Startup scripts, configmaps, sleep 10d debugging, config/script editing | [scripts.md](scripts.md) |
| /opt mount for overlay code debugging | [code-debug.md](code-debug.md) |
| Nova maintenance pod for cell/evacuation operations | [nova-maintenance.md](nova-maintenance.md) |
| kubectl logs, fluentd history log search | [logs.md](logs.md) |
| Service failing to start, database issues, config debugging, helm rollback | [scenarios.md](scenarios.md) |
| Essential commands, environment constants, namespaces | [reference.md](reference.md) |

## Quick Start — 3 Most Used Commands

```bash
# 1. SSH to target node
sshpass -p "easystack" ssh -tt -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@<JUMP_IP> 'ssh -i .ssh/id_rsa.roller <TARGET_NODE_IP>'

# 2. Enter busybox pod (has openstack CLI, mysql client)
kubectl exec -it -n openstack services/busybox -- bash

# 3. Restart a service
kubectl rollout restart deployment -n openstack <service-name>
```
