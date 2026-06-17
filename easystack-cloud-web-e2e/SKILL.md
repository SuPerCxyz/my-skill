---
name: easystack-cloud-web-e2e
description: "Use when testing EasyStack Cloud Web UI resource operations, validating EasyStack Cloud E2E cases, or maintaining reusable EasyStack UI operation patterns."
---

# EasyStack Cloud Web E2E

## 执行硬规则

- 必须通过 `agent-browser` 操作 EasyStack Cloud Web 页面。
- UI 测试必须优先使用 `agent-browser` CLI；如果本机没有该命令，先安装：
  `npm i -g agent-browser && agent-browser install`。无权限全局安装时使用
  `npm i -g --prefix "$HOME/.local" agent-browser && "$HOME/.local/bin/agent-browser" install`。
- `agent-browser` 安装或启动失败时，不继续推进真实 UI 测试。
- 执行前必须加载版本匹配说明：`agent-browser skills get core`。
- EasyStack 环境默认按自签名证书和容器/VM Chrome sandbox 限制处理；首次打开
  页面必须使用 `agent-browser --args '--no-sandbox' --ignore-https-errors open <url>`。
  建议为每次运行设置专用 `AGENT_BROWSER_SESSION`。
- 如果 daemon 已运行且参数未生效，不要无条件执行 `agent-browser close --all`。
  只有确认当前 daemon/会话由本次任务独占，或用户明确同意关闭所有
  agent-browser 会话时，才可 `close --all` 后用上述参数重启。
- 页面动作优先合并到单次 `agent-browser eval --stdin` 或 `agent-browser batch`。
- 不使用其他浏览器自动化脚本作为当前执行入口。
- 不把 Playwright 风格伪选择器（如 `:has-text()`、`text=`）传给
  `agent-browser click/fill/wait`；文本定位使用 `agent-browser find text ...`
  或 `interactions.md` 中的 `byText()` / `buttonByText()` / `fieldInput()`。
- 不逐步依赖 snapshot；snapshot 只用于必要诊断。
- 目标是减少跨步骤上下文、截图和 snapshot 带来的 token 消耗。
- 每个测试用例必须创建新的测试资源；用例前置里的 `vm1`、`volume1`
  等逻辑名表示本用例内要新建的资源，不允许复用环境旧资源或
  `/tmp/easystack-env.json` 中的历史 `test_resources`。
- 报告必须记录逻辑名到实际唯一资源名的映射，例如
  `vm1 -> <case-id>-vm1-<runid>`；后续步骤只能使用本次映射。
- 资源创建提交后如果没有通过 UI 列表确认成功，必须记为
  `creation_unconfirmed`，重新执行时换新的 run id 创建，不沿用未确认名称。
- 清理测试资源前必须先向用户说明待清理资源、影响和建议顺序；未得到用户明确
  确认时，只在报告中记录 `cleanup: recommended`，不得主动删除 VM、浮动 IP、
  云硬盘、快照等资源。
- 长耗时用例需要后台执行时：
  - Codex 场景：默认使用 `gpt-5.4-mini`，`reasoning_effort` 使用 `medium`。
  - Claude Code / OpenCode 场景：按当前会话模型和推理强度执行，无需指定。
- 除非用户明确要求，Codex 场景不升级 `gpt-5.3-codex` 或 `xhigh`。
- 使用过程中发现新的可复用操作时，必须沉淀到对应 `patterns/*-ops.md`，
  并同步 `patterns/quick-reference.md`。
- 操作状态分为 `ready-validated`、`ready-template`、`planned`；优先使用
  `ready-validated`，`ready-template` 执行时必须现场确认页面状态，
  `planned` 不作为当前执行入口。

## 入口选择

| 用户目标 | 先读 |
|----------|------|
| 登录、环境、会话复用 | [connection.md](connection.md) |
| 页面路径、菜单入口 | [navigation.md](navigation.md) |
| 执行流程、env、截图、报告 | [execution.md](execution.md) |
| 组件交互 helper | [interactions.md](interactions.md) |
| 测试编排规则 | [patterns.md](patterns.md) |
| 资源关系和联动 | [relationships.md](relationships.md) |

## 原子操作库

| 资源域 | 文档 |
|--------|------|
| 登录前置 | [patterns/login.md](patterns/login.md) |
| 实例 | [patterns/instance-ops.md](patterns/instance-ops.md) |
| 云硬盘与镜像 | [patterns/volume-ops.md](patterns/volume-ops.md) |
| 网络 | [patterns/network-ops.md](patterns/network-ops.md) |
| 页面只读探测 | [patterns/page-probes.md](patterns/page-probes.md) |
| 清理资源编排 | [patterns/cleanup-resources.md](patterns/cleanup-resources.md) |
| 常用操作索引 | [patterns/quick-reference.md](patterns/quick-reference.md) |
| 操作模板 | [patterns/operation-template.md](patterns/operation-template.md) |
| 平台信息和主路径 | [patterns/platform-info.md](patterns/platform-info.md) |

## 页面知识库

| 资源域 | 文档 |
|--------|------|
| 云主机 | [instance/instance.md](instance/instance.md) |
| 云主机快照 | [instance/snapshot.md](instance/snapshot.md) |
| 云主机回收站 | [instance/recycle-bin.md](instance/recycle-bin.md) |
| 云主机分组 | [instance/group.md](instance/group.md) |
| SSH 密钥对 | [instance/keypair.md](instance/keypair.md) |
| 实例规格 | [instance/flavor.md](instance/flavor.md) |
| 可用域与主机聚合 | [instance/az.md](instance/az.md) |
| 计算节点 | [instance/compute-node.md](instance/compute-node.md) |
| 云硬盘 | [volume/volume.md](volume/volume.md) |
| 云硬盘快照 | [volume/snapshot.md](volume/snapshot.md) |
| 云硬盘类型 | [volume/volume-type.md](volume/volume-type.md) |
| 镜像 | [image/image.md](image/image.md) |
| 网络 | [network/network.md](network/network.md) |
| 虚拟网卡 | [network/vnic.md](network/vnic.md) |
| 路由器 | [network/router.md](network/router.md) |
| 浮动 IP | [network/floating-ip.md](network/floating-ip.md) |

## 决策路径

1. 直接创建、删除、挂载、绑定资源：读 `patterns/login.md` 和对应 `patterns/*-ops.md`。
2. 执行测试用例：读 `execution.md`、`patterns.md` 和相关原子操作文档。
3. 查询页面字段、按钮、表格列：先读 `patterns/page-probes.md`，再读对应页面知识库。
4. 处理跨资源场景：读 `relationships.md` 后再选择原子操作。
5. 新增操作能力：先按 `patterns/operation-template.md` 在对应 `patterns/*-ops.md` 补 `ready-template`，再同步 `patterns/quick-reference.md`。
