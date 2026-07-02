---
name: easystack-env-debugging
description: "Use for live EasyStack Kubernetes/OpenStack environment inspection through the bundled env-access script: SSH/JumpServer access, kubectl, pods, services, logs, auth, config, VM/server anomalies, and cloud volume issues. Do not use for offline eslog, repo CI, Web UI E2E, or media/Windows tasks."
---

# EasyStack Environment Debugging

## Overview 概览

OpenStack 服务运行在 Kubernetes 中, 通常通过 Helm 部署在 `openstack` namespace。
本 skill 通过固化的 [env-access.sh](scripts/env-access.sh) 进入目标环境, 再执行
kubectl、OpenStack CLI、日志和配置等只读排查命令。

当目标是可访问的运行中环境时使用本 skill。离线 `.eslog` 包使用
`easystack-log-analysis`; 仓库 CI 失败使用 `easystack-ci-test`;
EasyStack Cloud Web UI 操作使用 `easystack-cloud-web-e2e`。

## Read-Only Safety Gate 只读安全门禁

默认只能执行查看类操作。进入环境后, 除非用户明确授权某个具体变更动作, 否则不要执行会影响环境状态的命令。

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

`helm get values` 是只读命令, 但部分环境会返回 `Unauthorized operation`。
不要把它作为默认验证命令; 失败时记录权限限制并继续其它只读检查。

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

如果排障确实需要变更环境, 先说明影响范围、回滚方式和验证方式, 并等待用户确认。

## Access Script Gate 访问脚本门禁

进入目标环境时, MUST 使用 [scripts/env-access.sh](scripts/env-access.sh)。不要手写
`ssh`、`ssh js`、多层跳板命令或临时 expect 脚本来登录环境。`env-access.sh`
负责封装直连、`172.18.*` 跳板、BJ-xx SSH config 跳板直达和 JumpServer 菜单
fallback。

JumpServer 连接信息优先从用户 SSH 配置读取。读取不到 alias、host、user、
port 或认证方式时, 按 [access.md](access.md#jumpserver-前置条件与配置缺失处理)
说明缺失项并向用户索取, 不要猜测或硬编码。

不要修改 [scripts/env-access.sh](scripts/env-access.sh) 或
[scripts/jumpserver-env.sh](scripts/jumpserver-env.sh)。如果脚本执行确实失败, 先
向用户报告目标、命令、完整错误现象和你需要的改动点; 只有获得用户明确允许后,
才能修改脚本。

## Quick Reference 快速参考 - 文件索引

| 需要做什么 | 阅读 |
|------------------|------|
| 环境后台访问入口、172.18 跳板、BJ-xx SSH config 跳板直达、JumpServer 菜单 fallback | [access.md](access.md) |
| 统一环境访问脚本, 登录链路封装后追加业务命令 | [scripts/env-access.sh](scripts/env-access.sh) |
| JumpServer 菜单内部 fallback 脚本, 由统一访问脚本调用 | [scripts/jumpserver-env.sh](scripts/jumpserver-env.sh) |
| OpenStack CLI 认证、busybox pod、admin 凭据 | [auth.md](auth.md) |
| 服务清单、pod 名称、OVN 网络、Helm release、代码仓库布局 | [services.md](services.md) |
| OpenStack 组件部署、pod、启动方式详情 | [openstack/index.md](openstack/index.md) |
| Ceph 组件部署、pod、启动方式详情 | [ceph/index.md](ceph/index.md) |
| Kubernetes 组件、pod、启动方式详情 | [k8s/index.md](k8s/index.md) |
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

## Environment Access Summary 环境访问摘要

确认目标环境名称或 IP 后, 只选择 [access.md](access.md) 中的统一脚本参数。
不要在 `SKILL.md` 复制访问命令, 避免与脚本入口漂移。

| 目标 | 入口 |
|------|------|
| 普通可直连 IP | `env-access.sh --target <TARGET_IP>` |
| `172.18.*` IP | `env-access.sh --target <JUMP_IP> --control-node <CONTROL_NODE_IP>` |
| `172.<N>.0.2` 或 `BJ-xx` | `env-access.sh --env BJ-<ENV_ID>` |
| JumpServer 资产名 | `env-access.sh --asset <ASSET_NAME> --mode jumpserver` |

进入环境后先按 [access.md](access.md#进入后台后) 完成身份、kubectl 和 node
名称验证, 再按 Quick Reference 选择对应排查文档。

## Skill Maintenance Principles Skill 维护原则

不是每次调查都要更新 skill。只有满足以下条件才值得加:

1. **通用性** — 多个环境都会遇到的模式或问题, 而非某个特定组件的单次排查
2. **复用性** — 下次排查同类问题时可以直接参考, 不需要重新分析
3. **跨环境** — 不依赖特定版本或配置, 在不同部署中都有价值

单个组件的细节、特定场景的一次性排查步骤, 不要写入 skill 文件。
