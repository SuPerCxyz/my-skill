---
name: easystack-env-debugging
description: "Use for live EasyStack Kubernetes/OpenStack environment inspection over SSH, JumpServer, kubectl, pods, services, logs, auth, config, VM/server anomalies, and cloud volume issues. Do not use for offline eslog bundles, repository tox/CI fixes, EasyStack Cloud Web UI E2E, or media/Windows desktop tasks."
---

# EasyStack Environment Debugging

## Overview 概览

OpenStack 服务运行在 Kubernetes 中, 通常通过 Helm 部署在 `openstack` namespace。
本 skill 根据目标环境名称或 IP 模式选择 SSH 访问方式。

当目标是可访问的运行中环境时使用本 skill。离线 `.eslog` 包使用
`easystack-log-analysis`; 仓库 CI 失败使用 `easystack-ci-test`;
EasyStack Cloud Web UI 操作使用 `easystack-cloud-web-e2e`。

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

| 需要做什么 | 阅读 |
|------------------|------|
| 环境后台访问、三种 SSH 入口、JumpServer 堡垒机 | [access.md](access.md) |
| JumpServer 固化访问脚本, 需要用户指定资产 | [scripts/jumpserver-env.sh](scripts/jumpserver-env.sh) |
| OpenStack CLI 认证、busybox pod、admin 凭据 | [auth.md](auth.md) |
| 服务清单、pod 名称、OVN 网络、Helm release、代码仓库布局 | [services.md](services.md) |
| OpenStack 组件部署、pod、启动方式详情 | [openstack/index.md](openstack/index.md) |
| Ceph 组件部署、pod、启动方式详情 | [ceph/index.md](ceph/index.md) |
| Kubernetes 组件部署、节点、pod、启动方式详情 | [k8s/index.md](k8s/index.md) |
| 多容器 pod、label selector、StatefulSet 与 Deployment 区分 | [pods.md](pods.md) |
| 启动脚本、configmap、配置和脚本查看 | [scripts.md](scripts.md) |
| /opt mount code overlay debugging, explicit authorization required | [code-debug.md](code-debug.md) |
| 组件级特殊操作、maintenance pod、授权门禁 | [special-operations.md](special-operations.md) |
| `kubectl logs`、fluentd 历史日志搜索 | [logs.md](logs.md) |
| 常见问题:虚拟机异常、云硬盘异常、服务启动失败、数据库问题、配置排查、只读 Helm 查看 | [scenarios.md](scenarios.md) |
| 节点间网络排查(L1/L2/L3诊断)、ARP状态解读、VLAN子接口排查 | [network.md](network.md) |
| 常用命令、环境常量、namespace | [reference.md](reference.md) |

### Component Detail Index 组件详情索引

| 组件详情 | 阅读 |
|----------|------|
| OpenStack 组件总览 | [openstack/index.md](openstack/index.md) |
| OpenStack 服务映射 | [openstack/service-map.md](openstack/service-map.md) |
| OpenStack 代码仓库布局 | [openstack/project-code-layout.md](openstack/project-code-layout.md) |
| Nova | [openstack/nova.md](openstack/nova.md) |
| Cinder | [openstack/cinder.md](openstack/cinder.md) |
| Glance | [openstack/glance.md](openstack/glance.md) |
| Keystone | [openstack/keystone.md](openstack/keystone.md) |
| Barbican | [openstack/barbican.md](openstack/barbican.md) |
| Baremetal / Ironic | [openstack/baremetal-ironic.md](openstack/baremetal-ironic.md) |
| Networking / OVN / Proton | [openstack/networking.md](openstack/networking.md) |
| Aodh | [openstack/aodh.md](openstack/aodh.md) |
| Ceilometer | [openstack/ceilometer.md](openstack/ceilometer.md) |
| Gnocchi | [openstack/gnocchi.md](openstack/gnocchi.md) |
| Horizon | [openstack/horizon.md](openstack/horizon.md) |
| Infrastructure services | [openstack/infrastructure.md](openstack/infrastructure.md) |
| Monitoring services | [openstack/monitoring.md](openstack/monitoring.md) |
| Extended services | [openstack/extended-services.md](openstack/extended-services.md) |
| Ceph 组件总览 | [ceph/index.md](ceph/index.md) |
| Kubernetes 组件总览 | [k8s/index.md](k8s/index.md) |

## Environment Access Flow 环境访问流程

### Step 1: Determine Access Method 确定访问方式

向用户确认 **目标环境名称或 IP**。

如果用户提到以下信息:
- `ssh js` / JumpServer / 堡垒机 / 类似 js 跳转到某个环境?
- 用户明确给出的 JumpServer 资产名, 例如 `<ASSET_NAME>`?

→ JumpServer 模式，直接跳转到 [JumpServer 堡垒机模式](access.md#jumpserver-堡垒机模式)

否则按 IP 模式判断:

- IP 以 `172.18.` 开头 → 跳板机模式
- 其他 IP → 直连模式

示例入口:

- 普通可直连 IP → 直连模式
- `172.18.*` IP → 跳板机模式
- 用户提供的 JumpServer 资产名 → JumpServer 模式

### Step 2: Check IP Pattern and SSH In 检查 IP 模式并 SSH 接入

具体命令以 [access.md](access.md) 为准；这里仅描述分流规则。

如果 IP 以 `172.18.` 开头 → 跳板机模式:

```bash
# SSH via jump host
sshpass -p "easystack" ssh -F /dev/null -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=8 root@<TARGET_IP> 'ssh -F /dev/null -i /root/.ssh/id_rsa.roller -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@<CONTROL_NODE_IP>'
```

- 跳板机: 用户提供的 `172.18.x.x` 地址
- K8s 控制节点 IP:通常 **10.20.0.3**，失败时询问用户

其他 IP → 直连模式:

```bash
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@<TARGET_IP>
```

- 如果密码错误，先试 `easystack`，再问用户

进入后台后，通过主机名访问其他 K8s 节点(`/etc/hosts` 由部署工具维护，始终使用主机名而非 IP):

```bash
ssh node-3 'hostname; whoami; pwd'
```

### Step 3: Verify Access 验证可访问性

SSH 进入后, 先执行最小只读检查:

```bash
whoami
id -u
hostname
pwd
```

如果目标节点有 kubectl 和 kubeconfig, 再执行:

```bash
kubectl get namespaces | grep openstack
```

然后用 Kubernetes node 名称确认环境节点列表:

```bash
kubectl get nodes -o name
```

- **identity/hostname 检查成功** → 环境 shell 访问已确认。
- **找到 `openstack`** → Kubernetes 访问已确认。后续按上方参考文档执行只读排查。
- **返回 node 名称** → 后续选择 SSH 节点或检查 pod 分布前, 以该列表作为权威节点清单。
- **kubectl 失败** → 使用 kubeconfig 路径重试:
  ```bash
  kubectl get namespaces --kubeconfig=/etc/kubernetes/admin.conf | grep openstack
  ```
- **仍然失败** → 报告 shell 访问成功但 kubectl 不可用, 并询问用户正确节点或访问方式。

### Step 4: Fallback 回退方案

如果 JumpServer、跳板机模式和直连模式都失败:

> ⚠ SSH 连接失败。请提供正确的进入方法(SSH 命令、跳板机信息或其他方式)。

等待用户提供正确访问命令后再继续。

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

节点清单查询:

```bash
kubectl get nodes -o name
```

## Skill Maintenance Principles Skill 维护原则

不是每次调查都要更新 skill。只有满足以下条件才值得加:

1. **通用性** — 多个环境都会遇到的模式或问题，而非某个特定组件的单次排查
2. **复用性** — 下次排查同类问题时可以直接参考，不需要重新分析
3. **跨环境** — 不依赖特定版本或配置，在不同部署中都有价值

单个组件的细节、特定场景的一次性排查步骤，不要写入 skill 文件。
