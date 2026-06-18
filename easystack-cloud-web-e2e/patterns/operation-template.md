# 原子操作统一模板

所有可沉淀为操作库的页面动作都必须使用本模板。未补齐模板前，只能放入
`待迁移操作`，不能标记为 `ready-template` 或 `ready-validated`。
补齐模板但尚未真实跑通的操作标记为 `ready-template`；通过真实 EasyStack
Web UI 用例验证后才能标记为 `ready-validated`。

## `<operation_name>`

### 用途

说明该操作解决什么资源动作，是否创建、修改、删除或绑定资源。

### 参数

- 必填参数：列出必须由调用方提供的字段
- 环境默认参数：列出从 `/tmp/easystack-env.json` 读取的字段
- 显式可选参数：列出调用方可覆盖的字段

### 前置条件

- `/tmp/easystack-env.json` 中至少存在 `platform.url`
- 调用前已按 `patterns/login.md` 准备可复用 `agent-browser` 会话
- 目标资源、配额或页面入口满足操作要求
- 若操作使用顶部工具栏或 `More` 菜单，必须先定义“选中成功”的可观测条件，例如
  checkbox 已 checked、目标动作按钮已 enabled

### 成功判定

- 必须写清可观测的成功状态
- 不能只以“按钮点击完成”作为成功
- 不能只因为资源名在列表中出现就判定成功；若资源存在中间态，必须写清
  “出现即存在”与“状态稳定完成”之间的差异
- 必须说明当 toast/notification 与列表状态不一致时，以哪个观测源为准；默认以
  列表稳定态或详情页状态为准，toast 只作为弱信号

### 执行步骤概览

- 打开目标页面并确认未跳回登录页
- 定位目标资源或打开创建/编辑入口
- 如果动作走顶部工具栏或 `More` 菜单，先选中目标资源并验证选中成功
- 填写表单或选择目标项
- 对下拉、联动字段、资源选择框，提交前回读当前展示值
- 识别当前页面或弹窗中的必填项，并确认主操作按钮从 disabled 变为 enabled
- 提交操作
- 轮询或验证目标状态，直到资源进入目标稳定态
- 等待资源时优先分段验证：先短时间确认资源是否出现，再轮询状态是否稳定
- 默认等待预算应写清：
  - 出现阶段：短窗口，例如 10 到 30 秒
  - 稳定阶段：按资源类型设置有限上限，例如 30 到 120 秒
  - 长耗时例外：仅对迁移、数据拷贝、`fio` 等任务单独放宽，并注明原因

### 失败信号

- 缺少必填参数
- 页面跳回登录页
- 目标资源不可见或无法选择
- 目标行看似已点中，但 checkbox、工具栏按钮或 `More` 动作状态没有变化
- 提交后状态未达到预期
- 资源虽已出现，但长时间停留在 `Creating`、`Binding`、`Associating`、
  `Detaching`、`Deleting` 等中间态
- 必填项未满足，导致主操作按钮持续 disabled
- 下拉已点击但当前展示值未切换到目标值
- 使用长时间无中止条件的等待循环，导致页面状态变化、筛选失效或定位过期后仍继续空等
- 按钮持续 disabled 或状态长期不推进，却没有切换到诊断分支
- 轮询超时

### 返回值约定

```json
{
  "ok": true,
  "resource": "<resource>",
  "action": "<action>",
  "name": "<resource-name>",
  "status": "<observed-status>",
  "message": "<short result>",
  "url": "<current-url>"
}
```

### `agent-browser eval --stdin` 示例

```bash
agent-browser eval --stdin <<'JS'
const result = {
  ok: true,
  resource: '<resource>',
  action: '<action>',
  name: '<resource-name>',
  status: '<observed-status>',
  message: '<message>',
  url: location.href
};
result;
JS
```
