---
name: easystack-env-debugging
description: Use when debugging EasyStack services deployed on Kubernetes. Determines SSH access method based on target IP: jump host for 172.18.x.x, direct SSH otherwise. Verifies environment access via kubectl. Covers pod operations, log search, config editing, and common debugging scenarios.
---

# EasyStack Environment Debugging

## Overview

OpenStack services run on Kubernetes (Helm-deployed) in the `openstack` namespace.
This skill automates SSH access based on the target environment IP pattern.

## Quick Reference - File Index

| When you need... | Read |
|------------------|------|
| SSH access details, local openstack client setup | [access.md](access.md) |
| OpenStack CLI auth, busybox pod, admin credentials | [auth.md](auth.md) |
| Service list, pod names, OVN networking, Helm releases, code repo layout | [services.md](services.md) |
| Multi-container pods, label selectors, StatefulSet vs Deployment | [pods.md](pods.md) |
| Startup scripts, configmaps, startup-time code overlay debugging, config/script editing | [scripts.md](scripts.md) |
| /opt mount for overlay code debugging | [code-debug.md](code-debug.md) |
| Nova maintenance pod for cell/evacuation operations | [nova-maintenance.md](nova-maintenance.md) |
| kubectl logs, fluentd history log search | [logs.md](logs.md) |
| Service failing to start, database issues, config debugging, helm rollback | [scenarios.md](scenarios.md) |
| Essential commands, environment constants, namespaces | [reference.md](reference.md) |

## Environment Access Flow

### Step 1: Determine target IP

Ask the user for the target environment IP or hostname.

### Step 2: Check IP pattern and SSH in

**If IP starts with `172.18.`** → Jump host mode:

```bash
# SSH via jump host
sshpass -p "easystack" ssh -F /dev/null -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=8 root@<TARGET_IP> 'ssh -F /dev/null -i /root/.ssh/id_rsa.roller -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@<CONTROL_NODE_IP>'
```

- Jump host: the `172.18.x.x` address provided
- K8s 控制节点 IP：通常 **10.20.0.3**，失败时询问用户

**Other IPs** → Direct SSH mode:

```bash
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@<TARGET_IP>
```

- 如果密码错误，先试 `easystack`，再问用户

**进入控制节点后**，通过 `ssh node-xxx` 访问其他 K8s 节点：

```bash
ssh node-3 'multipath -ll'
```

### Step 3: Verify access

After SSH, run:

```bash
kubectl get namespaces | grep openstack
```

- **`openstack` found** → ✓ Environment access confirmed. Proceed with debugging tasks using the reference docs above.
- **Command fails** → Retry with kubeconfig path:
  ```bash
  kubectl get namespaces --kubeconfig=/etc/kubernetes/admin.conf | grep openstack
  ```
- **Still fails** → Report SSH succeeded but kubectl unavailable. Ask user for correct node or access method.

### Step 4: Fallback

If neither jump host mode nor direct SSH mode work:

> ⚠ SSH 连接失败。请提供正确的进入方法（SSH 命令、跳板机信息或其他方式）。

Wait for user to provide the correct access command, then proceed.

## Quick Start - Once Inside

```bash
# Enter busybox pod (has openstack CLI, mysql client)
kubectl exec -it -n openstack services/busybox -- bash

# 进入 busybox 后先 source 认证
source /openrc

# Restart a service
kubectl rollout restart deployment -n openstack <service-name>

# Check logs
kubectl logs -n openstack -l service=<service-name> --tail=100

# 访问其他 K8s 节点（节点间已配免密）
ssh node-3 'multipath -ll'
```

## Skill 维护原则

不是每次调查都要更新 skill。只有满足以下条件才值得加：

1. **通用性** — 多个环境都会遇到的模式或问题，而非某个特定组件的单次排查
2. **复用性** — 下次排查同类问题时可以直接参考，不需要重新分析
3. **跨环境** — 不依赖特定版本或配置，在不同部署中都有价值

单个组件的细节、特定场景的一次性排查步骤，不要写入 skill 文件。
