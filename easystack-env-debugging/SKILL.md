---
name: easystack-env-debugging
description: "Use for live EasyStack Kubernetes/OpenStack environment inspection over SSH, kubectl, pods, services, logs, auth, config, JumpServer assets, and read-only diagnosis. Do not use for offline eslog bundles, repository tox/CI fixes, EasyStack Cloud Web UI E2E, or media/Windows desktop tasks."
---

# EasyStack Environment Debugging

## Overview 概览

OpenStack services run on Kubernetes (Helm-deployed) in the `openstack` namespace.
This skill automates SSH access based on the target environment IP pattern.

Use this skill when the target is a reachable running environment. For offline `.eslog` bundles use `easystack-log-analysis`; for repository CI failures use `easystack-ci-test`; for EasyStack Cloud Web UI actions use `easystack-cloud-web-e2e`.

## Read-Only Safety Gate 只读安全门禁

默认只能执行查看类操作。进入环境后，除非用户明确授权某个具体变更动作，否则不要执行会影响环境状态的命令。

允许的默认命令:

```bash
whoami
id -u
hostname
pwd
kubectl get ...
kubectl describe ...
kubectl logs ... --tail=<N>
helm list -n openstack
helm history -n openstack <release-name>
```

`helm get values` 是只读命令，但部分环境会返回 `Unauthorized operation`。
不要把它作为默认验证命令；失败时记录权限限制并继续其它只读检查。

禁止作为默认动作执行:

```bash
kubectl edit ...
kubectl delete ...
kubectl apply ...
kubectl patch ...
kubectl rollout restart ...
kubectl scale ...
helm rollback ...
systemctl restart ...
service ... restart
mysql/update/delete/insert/alter/drop
```

如果排障确实需要变更环境，先说明影响范围、回滚方式和验证方式，并等待用户确认。

## Quick Reference 快速参考 - 文件索引

| When you need... | Read |
|------------------|------|
| 环境后台访问、三种 SSH 入口、JumpServer 堡垒机 | [access.md](access.md) |
| OpenStack CLI auth, busybox pod, admin credentials | [auth.md](auth.md) |
| Service list, pod names, OVN networking, Helm releases, code repo layout | [services.md](services.md) |
| Multi-container pods, label selectors, StatefulSet vs Deployment | [pods.md](pods.md) |
| Startup scripts, configmaps, config/script inspection | [scripts.md](scripts.md) |
| /opt mount code overlay debugging, explicit authorization required | [code-debug.md](code-debug.md) |
| Nova maintenance pod read-only inspection and authorization guard | [nova-maintenance.md](nova-maintenance.md) |
| kubectl logs, fluentd history log search | [logs.md](logs.md) |
| Service failing to start, database issues, config debugging, read-only helm inspection | [scenarios.md](scenarios.md) |
| 节点间网络排查(L1/L2/L3诊断)、ARP状态解读、VLAN子接口排查 | [network.md](network.md) |
| Essential commands, environment constants, namespaces | [reference.md](reference.md) |

## Environment Access Flow 环境访问流程

### Step 1: Determine Access Method 确定访问方式

Ask the user for the **target environment name or IP**.

**Did the user mention:**
- `ssh js` / JumpServer / 堡垒机 / 类似 js 跳转到某个环境?
- Asset name like `BJ-32`, `SH-xx`, `GZ-xx`?

→ JumpServer 模式，直接跳转到 [JumpServer 堡垒机模式](access.md#jumpserver-堡垒机模式)

**Otherwise**, check the IP pattern:

- IP starts with `172.18.` → Jump host mode
- Other IPs → Direct SSH mode

示例入口:

- `192.168.3.3` → Direct SSH mode
- `172.18.0.118` → Jump host mode
- `BJ-35` → JumpServer mode

### Step 2: Check IP Pattern and SSH In 检查 IP 模式并 SSH 接入

具体命令以 [access.md](access.md) 为准；这里仅描述分流规则。

**If IP starts with `172.18.`** → Jump host mode:

```bash
# SSH via jump host
sshpass -p "easystack" ssh -F /dev/null -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=8 root@<TARGET_IP> 'ssh -F /dev/null -i /root/.ssh/id_rsa.roller -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@<CONTROL_NODE_IP>'
```

- Jump host: the `172.18.x.x` address provided
- K8s 控制节点 IP:通常 **10.20.0.3**，失败时询问用户

**Other IPs** → Direct SSH mode:

```bash
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@<TARGET_IP>
```

- 如果密码错误，先试 `easystack`，再问用户

进入后台后，通过主机名访问其他 K8s 节点(`/etc/hosts` 由部署工具维护，始终使用主机名而非 IP):

```bash
ssh node-3 'hostname; whoami; pwd'
```

### Step 3: Verify Access 验证可访问性

After SSH, first run the minimal read-only checks:

```bash
whoami
id -u
hostname
pwd
```

If the target node has kubectl and kubeconfig, then run:

```bash
kubectl get namespaces | grep openstack
```

- **identity/hostname checks succeed** → Environment shell access confirmed.
- **`openstack` found** → Kubernetes access confirmed. Proceed with read-only debugging tasks using the reference docs above.
- **kubectl fails** → Retry with kubeconfig path:
  ```bash
  kubectl get namespaces --kubeconfig=/etc/kubernetes/admin.conf | grep openstack
  ```
- **Still fails** → Report shell access succeeded but kubectl unavailable. Ask user for correct node or access method.

### Step 4: Fallback 回退方案

If JumpServer, jump host mode, and direct SSH mode all fail:

> ⚠ SSH 连接失败。请提供正确的进入方法(SSH 命令、跳板机信息或其他方式)。

Wait for user to provide the correct access command, then proceed.

## Quick Start 快速开始 - 进入环境后

```bash
# Confirm identity and target host
whoami
id -u
hostname
pwd

# Inspect namespaces and pods
kubectl get namespaces | grep openstack
kubectl get pods -n openstack

# Check logs without changing state
kubectl logs -n openstack -l service=<service-name> --tail=100

# Inspect Helm release metadata
helm list -n openstack
helm history -n openstack <release-name>
```

## Skill Maintenance Principles Skill 维护原则

不是每次调查都要更新 skill。只有满足以下条件才值得加:

1. **通用性** — 多个环境都会遇到的模式或问题，而非某个特定组件的单次排查
2. **复用性** — 下次排查同类问题时可以直接参考，不需要重新分析
3. **跨环境** — 不依赖特定版本或配置，在不同部署中都有价值

单个组件的细节、特定场景的一次性排查步骤，不要写入 skill 文件。
