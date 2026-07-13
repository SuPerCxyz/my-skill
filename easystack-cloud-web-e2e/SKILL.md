---
name: easystack-cloud-web-e2e
description: "Use when automating EasyStack Cloud Web UI with agent-browser: resource create/delete/attach/associate flows, floating IPs, buttons, tables, forms, E2E validation, page probing, and UI patterns. Do not use for backend debugging, offline eslog analysis, repository CI, or generic browser tasks."
---

# EasyStack Cloud Web E2E

## Scope Boundary 适用边界

使用本 skill 处理 EasyStack Cloud Web 页面上的真实 UI 操作、资源类 E2E 用例、按钮/表格/表单状态验证和可复用页面操作沉淀。后端服务排查归 `easystack-env-debugging`, 离线日志根因分析归 `easystack-log-analysis`, 仓库 CI 修复归 `easystack-ci-test`, 非 EasyStack Cloud 的普通网页自动化不属于本 skill 范围。

## Hard Rules 执行硬规则

- 必须通过 `agent-browser` 操作 EasyStack Cloud Web 页面。
- UI 测试必须优先使用 `agent-browser` CLI。如果本机没有该命令, 先报告缺失项、
  安装命令和影响, 等待用户明确确认后再安装。优先安装到 `$HOME/.local`, 不默认
  修改全局 npm 环境。
- `agent-browser` 安装或启动失败时,不继续推进真实 UI 测试。
- 执行前必须加载版本匹配说明:`agent-browser skills get core`。
- EasyStack 环境默认按自签名证书和容器/VM Chrome sandbox 限制处理;首次打开
  页面必须使用 `agent-browser --args '--no-sandbox' --ignore-https-errors open <url>`。
  建议为每次运行设置专用 `AGENT_BROWSER_SESSION`。
- 如果 daemon 已运行且参数未生效,不要无条件执行 `agent-browser close --all`。
  只有确认当前 daemon/会话由本次任务独占,或用户明确同意关闭所有
  agent-browser 会话时,才可 `close --all` 后用上述参数重启。
- 页面动作优先合并到单次 `agent-browser eval --stdin` 或 `agent-browser batch`。
- 不使用其他浏览器自动化脚本作为当前执行入口。
- 不把 Playwright 风格伪选择器(如 `:has-text()`、`text=`)传给
  `agent-browser click/fill/wait`;文本定位使用 `agent-browser find text ...`
  或 `interactions.md` 中的 `byText()` / `buttonByText()` / `fieldInput()`。
- 不逐步依赖 snapshot;snapshot 只用于必要诊断。
- 目标是减少跨步骤上下文、截图和 snapshot 带来的 token 消耗。
- 每个测试用例必须创建新的测试资源;用例前置里的 `vm1`、`volume1`
  等逻辑名表示本用例内要新建的资源,不允许复用环境旧资源或
  `/tmp/easystack-env.json` 中的历史 `test_resources`。
- 上述规则只约束独立 E2E 测试用例。用户明确要求对现有资源执行直接操作并提供精确
  资源名时, 可以使用该资源; 操作前必须回读名称、项目和当前状态, 并说明影响。
- 报告必须记录逻辑名到实际唯一资源名的映射,例如
  `vm1 -> <case-id>-vm1-<runid>`;后续步骤只能使用本次映射。
- 资源创建提交后如果没有通过 UI 列表确认成功,必须记为
  `creation_unconfirmed`,重新执行时换新的 run id 创建,不沿用未确认名称。
- 创建或操作资源后,不能因为“列表里立刻出现了资源名”就判定成功;必须继续
  观察资源状态从中间态转为目标稳定态,例如 `Creating -> Available`、
  `Creating -> Active`、`In use -> Available`。
- 如果资源已经出现但仍处于 `Creating`、`Binding`、`Associating`、`Detaching`、
  `Deleting` 等中间态,报告中应记录当前状态并继续轮询,不得提前结束为成功。
- 顶部工具栏按钮、`More` 菜单动作通常依赖“先选中资源”;不能只因为页面上出现了
  `Start`、`Attach`、`Detach`、`More` 就直接点击。必须先确认目标行已选中,且
  对应动作按钮已从 disabled 变为 enabled。
- 行名称、详情链接、行内非批量动作与顶部工具栏动作不是同一种入口;需要先判断
  当前动作属于“行内入口”“顶部工具栏”还是“More 菜单”,再决定是否必须先选中行。
- 对页面或弹窗内的主操作按钮(如 `Create`、`Confirm`、`Associate`、`Attach`、
  `Save`),不能先点再看报错;必须先识别必填参数、完成填值/选择并触发页面
  需要的 `input/change/blur` 或等价事件,再检查按钮是否从 disabled 变为 enabled。
- 如果主按钮仍 disabled,优先回查当前页面或弹窗里尚未满足的必填项、联动下拉、
  配额提示或校验错误,而不是重复点击失效按钮。
- 下拉选择、实例/vNIC 选择、类型切换等操作完成后,必须回读当前展示值确认真的已
  切换成功;不能只因为 dropdown 关闭了,就判定选择成功。
- 等待策略不得写成长时间无区别的 `for` 循环傻等。应拆成两段:
  1. 短窗口等待资源名出现
  2. 资源出现后的状态轮询
- 单段轮询必须有明确超时、间隔和提前中止条件;如果超过短窗口仍未出现资源,
  先重新加载页面、重新定位或重新查询筛选条件,再决定是否继续。
- 默认禁止超过几十秒的无差别页面等待。普通 UI 交互、列表刷新、按钮启用、
  modal 提交结果、常规资源创建/绑定/解绑,应在短预算内完成诊断或结束本轮等待。
- 只有明确属于长耗时任务时,才允许扩大等待预算,例如云硬盘迁移数据、
  云主机迁移、`fio` 等压测或用户已明确说明的后台长任务;此时必须在报告中标注
  “长耗时等待”原因、目标状态、预计上限和当前观测状态。
- 如果等待目标在短预算内没有推进,例如按钮持续 disabled、资源状态不变化、
  列表不刷新、筛选结果为空,必须停止原等待循环,转入诊断:检查必填项、项目、
  配额、筛选条件、当前页面上下文、是否需要改走 `More` 菜单或重新选择资源。
- 表格行、分页位置、snapshot ref 在列表实时刷新、高频新增、切换排序/筛选后都可能
  立即失效;不得依赖“第 1 行/第 2 行”这类位置假设。必须优先按资源名、状态文本、
  详情入口重新定位。
- 结果判定优先级默认为:资源列表稳定态 > 资源详情页状态 > toast/notification 文案。
  toast 只可作为“操作已提交”的弱信号,不能单独作为最终成功依据。
- 清理测试资源前必须先向用户说明待清理资源、影响和建议顺序;未得到用户明确
  确认时,只在报告中记录 `cleanup: recommended`,不得主动删除 VM、浮动 IP、
  云硬盘、快照等资源。
- 长耗时用例需要后台执行时:
  - 不在 skill 中固定模型名称或推理等级。
  - 按当前会话 `AGENTS.md`、用户要求和平台可用能力选择。
- 使用过程中发现新的可复用操作时, 先在报告中记录 `skill_improvements`; 当前任务
  明确包含 skill 维护或用户确认更新后, 再沉淀到 `patterns/*-ops.md` 并同步
  `patterns/quick-reference.md`。
- 操作状态分为 `ready-validated`、`ready-template`、`planned`;优先使用
  `ready-validated`,`ready-template` 执行时必须现场确认页面状态,
  `planned` 不作为当前执行入口。

## Entry Selection 入口选择

| 用户目标 | 先读 |
|----------|------|
| 登录、环境、会话复用 | [connection.md](connection.md) |
| 页面路径、菜单入口 | [navigation.md](navigation.md) |
| 执行流程、env、截图、报告 | [execution.md](execution.md) |
| 组件交互 helper | [interactions.md](interactions.md) |
| 当前控制台探索结果 | [patterns/current-console-discovery.md](patterns/current-console-discovery.md) |
| 测试编排规则 | [patterns.md](patterns.md) |
| 资源关系和联动 | [relationships.md](relationships.md) |

## Atomic Operations 原子操作库

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

## Page Knowledge Base 页面知识库

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

## Decision Path 决策路径

1. 直接创建、删除、挂载、绑定资源:读 `patterns/login.md` 和对应 `patterns/*-ops.md`。
2. 执行测试用例:读 `execution.md`、`patterns.md` 和相关原子操作文档。
3. 查询页面字段、按钮、表格列:先读 `patterns/page-probes.md`,再读对应页面知识库。
4. 处理跨资源场景:读 `relationships.md` 后再选择原子操作。
5. 新增操作能力:先按 `patterns/operation-template.md` 在对应 `patterns/*-ops.md` 补 `ready-template`,再同步 `patterns/quick-reference.md`。

## Execution Feedback 执行反馈

执行本 skill 时, 若规则不明确、工具限制导致绕行、同一步骤反复执行或流程无法顺利
推进, 任务结束时必须向用户报告:

- 触发位置和问题现象
- 造成的中断、重复次数或额外开销
- 实际采用的临时处理
- 建议补充或修改的 skill 规则

没有实际问题时不输出空反馈。反馈不得包含密码、token、cookie 或未脱敏的用户数据。
