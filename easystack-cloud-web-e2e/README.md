# EasyStack Cloud Web E2E

EasyStack 云平台 Web UI 端到端自动化测试 Skill。基于 `agent-browser` 提供可复用的原子操作、页面知识库和测试编排规范，支持云主机、云硬盘、网络等核心资源的 UI 操作自动化。

## 概述

本项目是一个 Claude Code Skill，用于通过 `agent-browser` 对 EasyStack Cloud Web 页面执行 UI 自动化操作和端到端测试。核心设计原则：

- **统一入口**：所有 UI 操作统一通过 `agent-browser` CLI 执行，不混合其他浏览器自动化框架。
- **原子操作库**：页面交互封装为可复用的原子操作（`patterns/`），返回结构化结果。
- **页面知识库**：按资源域维护页面字段、定位方式和交互细节（`instance/`、`volume/`、`network/`、`image/`）。
- **测试编排**：定义测试用例结构、编排流程和结果约定（`patterns.md`、`execution.md`）。
- **减少 token 消耗**：多步骤页面动作合并为批量调用，不逐步依赖 snapshot。

## 文档结构

```
easystack-cloud-web-e2e/
├── SKILL.md               # Skill 顶层入口：硬规则、入口路由、决策路径
├── README.md              # 本文件：项目概述与使用指南
│
├── connection.md          # 连接与登录：agent-browser 前置、启动参数、环境配置、登录契约
├── navigation.md          # 页面导航：菜单结构、当前主路径与历史/别名路径
├── interactions.md        # UI 组件交互：按钮、文本输入、表格、下拉、对话框等定位 helper
├── execution.md           # 执行规范：执行流程、后台任务策略、操作库维护规则
├── patterns.md            # 测试编排规范：用例结构、原子操作调用约定
├── relationships.md       # 资源关联关系：云主机↔网络、云主机↔浮动 IP、云主机↔云硬盘等
│
├── patterns/              # 原子操作库
│   ├── login.md                           # 登录与共享前置能力
│   ├── instance-ops.md                    # 实例操作索引
│   ├── instance-ops/                      # 实例操作详细文档
│   │   ├── create-instance.md             #   - 创建云主机 (ready-validated)
│   │   ├── delete-instance.md             #   - 删除云主机 (ready-template)
│   │   ├── attach-volume.md               #   - 挂载云硬盘 (ready-validated)
│   │   ├── rename-instance.md             #   - 重命名云主机 (ready-template)
│   │   ├── start-stop-reboot.md           #   - 开机/关机/重启 (ready-template)
│   │   └── create-snapshot.md             #   - 创建云主机快照 (ready-template)
│   ├── volume-ops.md                      # 云硬盘与镜像操作 (create/detach/delete/snapshot/rollback/upload)
│   ├── network-ops.md                     # 网络操作 (floating IP allocate/associate/release, network, router)
│   ├── page-probes.md                     # 页面只读探测
│   ├── cleanup-resources.md               # 清理资源编排
│   ├── platform-info.md                   # 平台信息和主路径
│   ├── quick-reference.md                 # 常用操作索引
│   └── operation-template.md              # 操作文档模板
│
├── instance/              # 计算资源页面知识库
│   ├── instance.md                        # 云主机页面
│   ├── instance-details/                  # 云主机详情子页面
│   ├── snapshot.md                        # 云主机快照
│   ├── recycle-bin.md                     # 云主机回收站
│   ├── group.md                           # 云主机分组
│   ├── keypair.md                         # SSH 密钥对
│   ├── flavor.md                          # 实例规格
│   ├── az.md                              # 可用域与主机聚合
│   └── compute-node.md                    # 计算节点
│
├── volume/               # 存储资源页面知识库
│   ├── volume.md                          # 云硬盘页面
│   ├── volume-details/                    # 云硬盘详情子页面
│   ├── snapshot.md                        # 云硬盘快照
│   └── volume-type.md                     # 云硬盘类型
│
├── network/              # 网络资源页面知识库
│   ├── network.md                         # 网络页面
│   ├── network-details/                   # 网络详情子页面
│   ├── router.md                          # 路由器页面
│   ├── router-details/                    # 路由器详情子页面
│   ├── floating-ip.md                     # 浮动 IP 页面
│   ├── vnic.md                            # 虚拟网卡页面
│   └── vnic-details/                      # 虚拟网卡详情子页面
│
└── image/                # 镜像资源页面知识库
    ├── image.md                           # 镜像页面
    └── image-details/                     # 镜像详情子页面
```

## 快速开始

### 前置条件

- `agent-browser` CLI（如未安装，会自动安装）
- EasyStack 云平台访问地址和凭据
- 环境配置文件 `/tmp/easystack-env.json`

### 最小环境配置

```json
{
  "platform": {
    "url": "https://your-easystack-platform.local",
    "username": "admin",
    "password": "your-password"
  }
}
```

### 典型使用流程

1. **加载 Skill**：在 Claude Code 中调用 `easystack-cloud-web-e2e` skill。
2. **准备环境**：确保 `agent-browser` 可用，加载版本匹配说明。
3. **配置登录**：读取 `/tmp/easystack-env.json`，执行登录或复用会话。
4. **选择操作**：根据任务从 `patterns/quick-reference.md` 选择原子操作。
5. **执行用例**：按 `execution.md` 和 `patterns.md` 编排测试流程。
6. **报告结果**：记录资源映射、执行结果和截图路径。

### 示例

```bash
# 1. 确保 agent-browser 可用
agent-browser skills get core

# 2. 读取环境配置
cat /tmp/easystack-env.json

# 3. 打开登录页面
agent-browser --args '--no-sandbox' --ignore-https-errors open "$PLATFORM_URL/auth_login/"
```

## 能力状态

原子操作按验证成熟度分为三级：

| 状态 | 含义 |
|------|------|
| `ready-validated` | 已通过真实 EasyStack Web UI 用例验证，可直接使用 |
| `ready-template` | 已补齐操作模板但尚未完成真实用例闭环验证，执行时需现场确认页面状态 |
| `planned` | 仅保留操作名称清单，不作为当前可执行入口 |

### 已验证可用的核心操作 (`ready-validated`)

- 创建云主机 (`create_instance`)
- 挂载云硬盘 (`attach_volume`)
- 创建云硬盘 (`create_volume`)
- 卸载云硬盘 (`detach_volume`)
- 删除云硬盘 (`delete_volume`)
- 回滚云硬盘快照 (`rollback_volume_snapshot`)
- 删除云硬盘快照 (`delete_volume_snapshot`)
- 分配浮动 IP (`allocate_floating_ip`)
- 绑定浮动 IP (`associate_floating_ip`)

完整列表见 `patterns/quick-reference.md`。

## 关键规范

### 执行硬规则

- 所有 UI 操作统一通过 `agent-browser` 执行，不混合其他框架。
- 多步骤页面动作合并到单次 `agent-browser eval --stdin` 或 `agent-browser batch`。
- 不逐步依赖 snapshot 驱动操作；snapshot 只用于必要诊断。
- 每个测试用例必须创建新的测试资源，不复用历史资源。
- 资源创建提交后未确认成功时记为 `creation_unconfirmed`。
- 清理资源前必须先向用户说明待清理清单，得到确认后才执行。

### 资源命名

用例中 `vm1`、`volume1` 等逻辑名映射为唯一资源名：
`<case-id>-<resource-type>-<runid>`

报告中同时记录逻辑名和实际资源名。

### 返回值约定

所有原子操作返回统一结构化对象：

```json
{
  "ok": true,
  "resource": "volume",
  "action": "create",
  "name": "tc-vol001-volume1-abc123",
  "status": "Available",
  "message": "volume created",
  "url": "https://platform.local/ebs/volumes"
}
```

## 维护指南

### 新增原子操作

1. 按 `patterns/operation-template.md` 补齐操作文档。
2. 沉淀到对应资源域的 `patterns/*-ops.md`。
3. 同步更新 `patterns/quick-reference.md` 索引。

### 操作沉淀触发条件

执行过程中发现以下情况时，必须更新 skill 文档：

- 同一页面动作可能被多个用例复用
- 操作包含 3 步以上稳定页面交互
- 操作会创建、修改、删除或绑定平台资源

### 后台任务

长耗时用例后台任务策略：
- **Codex 场景**：默认使用 `gpt-5.4-mini` 模型、`reasoning_effort=medium`。
- **Claude Code / OpenCode 场景**：按当前会话模型和推理强度执行，无需指定。

后台任务只负责执行用例和写报告，发现可沉淀操作时记录 `skill_improvements`，由主会话统一更新。
