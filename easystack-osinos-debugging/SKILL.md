---
name: easystack-osinos-debugging
description: Use when debugging EasyStack OSINOS services deployed on Kubernetes via SSH jump hosts. Covers SSH access chain, OpenStack CLI auth from busybox pod, configmap editing, pod restart, startup-time code overlay debugging, and fluentd log search.
---

# EasyStack OSINOS Environment Debugging

## Overview

OpenStack services run on Kubernetes (Helm-deployed) in the `openstack` namespace.
Debugging requires SSH through a jump host, then `kubectl` to interact with pods.

## Quick Reference - File Index

| When you need... | Read |
|------------------|------|
| SSH access, local openstack client setup | [access.md](access.md) |
| OpenStack CLI auth, busybox pod, admin credentials | [auth.md](auth.md) |
| Service list, pod names, OVN networking, Helm releases, code repo layout | [services.md](services.md) |
| Multi-container pods, label selectors, StatefulSet vs Deployment | [pods.md](pods.md) |
| Startup scripts, configmaps, startup-time code overlay debugging, config/script editing | [scripts.md](scripts.md) |
| /opt mount for overlay code debugging | [code-debug.md](code-debug.md) |
| Nova maintenance pod for cell/evacuation operations | [nova-maintenance.md](nova-maintenance.md) |
| kubectl logs, fluentd history log search | [logs.md](logs.md) |
| Service failing to start, database issues, config debugging, helm rollback | [scenarios.md](scenarios.md) |
| Essential commands, environment constants, namespaces | [reference.md](reference.md) |

## Quick Start - 固定访问路径

**SSH 链：跳板机 → 10.20.0.3（K8s 控制节点）**

```bash
# 1. 一步执行远端 kubectl 命令
sshpass -p "easystack" ssh -F /dev/null -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=8 root@<JUMP_IP> 'ssh -F /dev/null -i /root/.ssh/id_rsa.roller -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@10.20.0.3' "<kubectl-command>"

# 2. 进入 busybox pod（有 openstack CLI、mysql 客户端）
kubectl exec -it -n openstack services/busybox -- bash

# 3. 重启服务
kubectl rollout restart deployment -n openstack <service-name>
```

**重要：** K8s 控制节点固定为 10.20.0.3，不要扫描网络或试探其他节点。跳板机本身没有 kubectl，必须内层 SSH 到 10.20.0.3。
