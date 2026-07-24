---
name: easystack-env-debugging
description: "Use when investigating live EasyStack Kubernetes/OpenStack incidents or performing explicitly authorized runtime code, overlay, or patch-path validation through env-access. Use `easystack-test-executor` for planned resource tests; combine for backend root cause or runtime changes. Combine offline historical logs with `easystack-log-analysis`."
---

# EasyStack Environment Debugging

## Overview 概览

OpenStack 服务运行在 Kubernetes 中, 通常通过 Helm 部署在 `openstack` namespace。
本 skill 通过固化的 [env-access.sh](scripts/env-access.sh) 进入目标环境, 支持两个
同等有效的入口: 在线问题调查, 以及用户明确授权后的 runtime code、overlay 或
patch 路径验证。完整资源功能和回归用例由 `easystack-test-executor` 执行。

当目标是可访问的运行中环境时使用本 skill。仅分析离线 `.eslog` 或已解压的
`ecs.*` 目录时使用 `easystack-log-analysis`; 历史故障同时涉及当前环境和本地离线
日志时联合使用两个 skill。仓库 CI 失败使用 `easystack-ci-test`;
EasyStack Cloud Web UI 操作使用 `easystack-cloud-web-e2e`。
Web UI 用例需要 backend 根因分析时, 以 `easystack-cloud-web-e2e` 执行 UI 流程,
联合本 skill 收集和分析后台证据。

## Task Mode Selection 任务模式选择

进入环境前先根据用户目标选择模式, 不要把所有请求都当作问题调查:

1. 问题调查模式: 用户询问故障原因、异常状态或提供错误、UUID、故障时间时, 使用
   日志优先的只读根因排查流程。
2. 代码调试模式: 用户要求修改 runtime code、部署临时 overlay、调试代码路径或
   验证 patch 路径时, 在完成授权门禁后直接使用 [code-debug.md](code-debug.md)。
   该模式不负责完整资源功能用例, 也不要求先构造故障根因。
3. 混合模式: 用户需要通过代码改动验证故障假设时, 先记录只读基线, 再执行授权修改,
   最后同时报告根因证据、代码变更、验证结果和回滚状态。

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

## Authorized Change Scope 授权变更范围

代码调试是本 skill 的一等入口, 不是根因调查失败后的 fallback。用户明确要求在环境中
修改 runtime code、验证 patch 路径、临时 overlay 代码或调整启动脚本做调试时,
仍属于本 skill 范围。执行前必须获得用户对目标环境、目标服务、目标节点、待修改文件、回滚
方式和验证命令的明确授权。

经授权的代码调试流程见 [code-debug.md](code-debug.md)。未经授权时, 不要执行
`scp`、编辑启动脚本、复制代码到 `/opt`、重启 pod 或任何会改变环境状态的操作。

## Access Script Gate 访问脚本门禁

进入目标环境时, MUST 使用 [scripts/env-access.sh](scripts/env-access.sh)。不要手写
`ssh`、`ssh js`、多层跳板命令或临时 expect 脚本来登录环境。`env-access.sh`
负责封装直连、`172.18.*` 跳板、BJ-xx SSH config 跳板直达和 JumpServer 菜单
fallback。
调用脚本时优先使用 `bash [script] ...`, 不要依赖直接执行位; 这样即使安装副本
丢了 `+x` 也能继续工作。
一次性只读命令的默认超时与超时后重试也由 `env-access.sh` 统一处理; 详细规则见
[access.md](access.md#查询超时选择)。

JumpServer 连接信息优先从用户 SSH 配置读取。读取不到 alias、host、user、
port 或认证方式时, 按 [access.md](access.md#jumpserver-前置条件与配置缺失处理)
说明缺失项并向用户索取, 不要猜测或硬编码。

不要修改 [scripts/env-access.sh](scripts/env-access.sh) 或
[scripts/jumpserver-env.sh](scripts/jumpserver-env.sh)。如果脚本执行确实失败, 先
向用户报告目标、命令、完整错误现象和你需要的改动点; 只有获得用户明确允许后,
才能修改脚本。

## Root Cause Triage Order 根因排查顺序

用户询问 “为什么失败”、“异常原因”、“创建失败”、“挂载失败”, 或提供 traceback、
错误栈、server UUID、volume UUID 时, 将任务视为根因排查, 而不是资源清单查询。

进入环境并完成最小连接验证后, 先读取相关业务 pod 当前日志。只允许用
`kubectl get pods` / label 查询来发现日志目标; 不要把 `openstack server show`,
`openstack volume show` 或 list 类资源状态查询作为第一步。

如果当前 pod 日志没有目标 UUID 或时间段, 再按 [logs.md](logs.md) 使用 fluentd
历史日志补齐。OpenStack CLI 状态查询只在日志线索需要补充上下文、需要确认关联
server/volume, 或用户明确要求查看状态时使用。

## Offline Historical Log Coordination 离线历史日志协同

故障时间超出当前 pod 或 fluentd 的可用日志时间窗, 且用户提供本地 `.eslog` 文件
或已解压的 `ecs.*` 目录时, MUST 同时加载并使用 `easystack-log-analysis`, 不要只
依赖运行中环境的当前状态推断历史根因。用户明确要求结合本地离线日志时也直接触发,
不再用主观的“时间较久”作为唯一判断条件。

按以下顺序解析离线日志位置:

1. 用户指定文件或目录路径时, 仅使用该路径。
2. 用户未指定路径时, 只在当前工作目录查找 `.eslog` 文件和顶层 `ecs.*` 目录。
3. 不要递归扫描当前工作目录以外的位置, 也不要把普通日志文件自动纳入此流程。
4. 找不到匹配项时, 明确报告已检查的当前目录, 再向用户索取路径。
5. 同一 bundle 同时存在 `.eslog` 和对应 `ecs.*` 时, 优先使用已解压目录。
6. 存在多个候选时, 先按文件名时间窗与故障时间匹配; 多个候选都覆盖故障时间时
   联合分析。用户未提供故障时间且无法唯一选择时, 再向用户确认。

联合分析时, 用 `easystack-log-analysis` 确认离线包时间窗、解压并构建历史证据链;
用本 skill 补充仍有价值的当前环境状态或执行验证。当前状态与历史日志不一致时,
按事件发生时间区分证据, 不得用当前正常状态否定历史故障。最终结论统一按
[report-format.md](report-format.md) 输出, 先给出一句话总结且不使用表格; 离线证据
保留本地 `file:line` 引用, 在线证据标明 pod、服务、对象和时间。

完成问题分析后, MUST 按 [report-format.md](report-format.md) 输出结论。问题分析结论
禁止使用 Markdown 表格, 标题使用普通文本, 列表使用数字项。任何一行都不得以
`-`、`#` 或 `$` 开头, fenced code block 内同样适用; 原始证据命中时增加
`原文: ` 前缀。第 1 至第 4 节必须输出, 第 5 至第 8 节仅在有实际内容或确有必要
时输出。

上述 [report-format.md](report-format.md) 仅约束问题调查或混合模式中的问题分析结论。
纯代码调试任务不强制输出第 1 至第 8 节, 应按 [code-debug.md](code-debug.md) 记录
授权范围、实际改动、验证结果、回滚状态和剩余风险。

## Quick Reference 快速参考 - 文件索引

| 需要做什么 | 阅读 |
|------------------|------|
| 环境后台访问入口、172.18 跳板、BJ-xx SSH config 跳板直达、JumpServer 菜单 fallback | [access.md](access.md) |
| 统一环境访问脚本, 登录链路封装后追加业务命令 | [scripts/env-access.sh](scripts/env-access.sh) |
| JumpServer 菜单内部 fallback 脚本, 由统一访问脚本调用 | [scripts/jumpserver-env.sh](scripts/jumpserver-env.sh) |
| 验证访问参数、安全重试和 JumpServer 传参 | [tests/test-access-scripts.sh](tests/test-access-scripts.sh) |
| 根因排查顺序、当前 pod 日志、fluentd 历史日志回退 | [logs.md](logs.md) |
| 无表格、行首安全且含一句话总结的问题分析结论格式 | [report-format.md](report-format.md) |
| 常见问题:虚拟机异常、云硬盘异常、服务启动失败、数据库问题、配置排查、只读 Helm 查看 | [scenarios.md](scenarios.md) |
| OpenStack CLI 认证、busybox pod、admin 凭据 | [auth.md](auth.md) |
| 服务清单、pod 名称、OVN 网络、Helm release、代码仓库布局 | [services.md](services.md) |
| OpenStack 组件部署、pod、启动方式详情 | [openstack/index.md](openstack/index.md) |
| Ceph 组件部署、pod、启动方式详情 | [ceph/index.md](ceph/index.md) |
| Kubernetes 组件、pod、启动方式详情 | [k8s/index.md](k8s/index.md) |
| 多容器 pod、label selector、StatefulSet 与 Deployment 区分 | [pods.md](pods.md) |
| 启动脚本、configmap、配置和脚本查看 | [scripts.md](scripts.md) |
| /opt mount code overlay debugging, explicit authorization required | [code-debug.md](code-debug.md) |
| 组件级特殊操作、maintenance pod、授权门禁 | [special-operations.md](special-operations.md) |
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

## Execution Feedback 执行反馈

执行本 skill 时, 若规则不明确、工具限制导致绕行、同一步骤反复执行或流程无法顺利
推进, 任务结束时必须向用户报告:

- 触发位置和问题现象
- 造成的中断、重复次数或额外开销
- 实际采用的临时处理
- 建议补充或修改的 skill 规则

没有实际问题时不输出空反馈。反馈不得包含密码、token、cookie 或未脱敏的用户数据。
