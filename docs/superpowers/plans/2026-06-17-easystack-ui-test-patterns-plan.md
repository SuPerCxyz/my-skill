# easystack-ui-test Patterns Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rework the `easystack-ui-test/patterns` core docs so they use one MCP Playwright contract, remove hard-coded credentials from the target docs, and publish a reusable instance-operations template.

**Architecture:** Keep the work limited to documentation boundaries. `login.md` becomes the shared execution contract, `instance-ops.md` becomes the first domain-specific template with three migrated operations, and `quick-reference.md` becomes the index that declares migration state instead of pretending every operation is already a stable function.

**Tech Stack:** Markdown, `apply_patch`, `rg`, `sed`

---

### Task 1: Rebuild the Shared Login Contract

**Files:**
- Modify: `easystack-ui-test/patterns/login.md`
- Reference: `easystack-ui-test/SKILL.md`
- Reference: `docs/superpowers/specs/2026-06-17-easystack-ui-test-patterns-design.md`

- [ ] **Step 1: Review the current login doc and record the required sections**

Run:

```bash
sed -n '1,220p' easystack-ui-test/patterns/login.md
sed -n '1,220p' docs/superpowers/specs/2026-06-17-easystack-ui-test-patterns-design.md
```

Expected: confirm the new `login.md` must cover environment source, login contract, session reuse, waiting rules, notification cleanup, page verification, and a JS-only example.

- [ ] **Step 2: Rewrite `login.md` as the MCP Playwright shared contract**

Replace the document with a structure like:

```md
# 登录与共享前置能力

## 适用范围

本文件定义 `patterns/` 下所有原子操作共享的前置契约。

## 环境配置来源

- 统一从 `/tmp/easystack-env.json` 读取平台地址和账号信息
- 调用参数优先级高于环境默认值
- 文档示例仅使用占位字段，不写真实凭证

## 登录契约

- 优先复用现有会话
- 会话无效时再访问 `/auth_login/`
- 登录成功必须通过 URL 或页面关键元素验证

## 会话复用契约

- 已在目标产品页时直接复用当前页面
- 已登录但不在目标页时直接 `goto()` 到目标页
- 未登录时执行完整登录流程

## 通用辅助动作

### 等待页面可操作

- 先等待 `networkidle`
- 再等待目标表格、按钮或表单出现
- `waitForTimeout` 只作为短暂兜底

### 清理通知和遮挡

```javascript
await page.evaluate(() => {
  document
    .querySelectorAll('.ant-notification-notice, .ant-message')
    .forEach((node) => node.remove());
});
```

## 返回值约定

```json
{
  "ok": true,
  "resource": "session",
  "action": "login",
  "status": "ready",
  "message": "session ready"
}
```

## 标准示例

```javascript
async (page, { targetPath = '/eec/instances' } = {}) => {
  const env = JSON.parse(Deno.readTextFileSync('/tmp/easystack-env.json'));
  const { url, username, password } = env.platform;
  await page.goto(`${url}${targetPath}`);
  if (page.url.includes('/auth_login/')) {
    await page.fill('#id_username', username);
    await page.fill('#id_password', password);
    await page.locator('button.js-loginBtn').click();
  }
  await page.waitForLoadState('networkidle');
  return { ok: true, resource: 'session', action: 'login', status: 'ready', message: 'session ready' };
}
```
```

Expected: the rewritten file contains no Python snippets, no real credentials, and one clear shared contract.

- [ ] **Step 3: Verify `login.md` no longer contains Python or hard-coded credentials**

Run:

```bash
rg -n "playwright.sync_api|admin@example.org|pgc@qq.com|172\\.32|172\\.35|1234qwer|test@passw0rd|Admin@ES20" easystack-ui-test/patterns/login.md
```

Expected: no output.

### Task 2: Restructure Instance Operations Around a Stable Template

**Files:**
- Modify: `easystack-ui-test/patterns/instance-ops.md`
- Reference: `easystack-ui-test/patterns/login.md`
- Reference: `docs/superpowers/specs/2026-06-17-easystack-ui-test-patterns-design.md`

- [ ] **Step 1: Review the current instance operations file and mark the three operations to migrate first**

Run:

```bash
sed -n '1,260p' easystack-ui-test/patterns/instance-ops.md
rg -n "创建 VM|删除 VM|挂载云硬盘" easystack-ui-test/patterns/instance-ops.md
```

Expected: identify the current `create`, `delete`, and `attach volume` sections and confirm the rest can be left as legacy content.

- [ ] **Step 2: Rewrite the document header and migration policy**

Add an opening structure like:

```md
# 实例操作

本文件定义实例域原子操作契约。所有示例统一面向
`browser_run_code_unsafe`，并依赖 `patterns/login.md`
中的共享前置能力。

## 使用约定

- 配置默认值来自 `/tmp/easystack-env.json`
- 显式参数优先于环境默认值
- 操作完成后必须验证目标状态
- 返回值统一使用结构化对象

## 迁移状态

- `create_instance`: ready
- `delete_instance`: ready
- `attach_volume`: ready
- 其他操作: legacy
```

Expected: the file begins with contract language and clearly distinguishes migrated vs legacy content.

- [ ] **Step 3: Replace the create-instance section with the new template**

Write a section with:

```md
## `create_instance`

### 用途

创建一台实例，并验证实例进入目标状态。

### 参数

- `name`：必填，实例名
- `image`：选填，默认取 `resources.image_name`
- `flavor`：选填，默认取 `resources.flavor`
- `network`：选填，默认取 `resources.network_name`
- `subnet`：选填，默认取 `resources.subnet_name`
- `system_disk_size`：选填，默认取平台默认值
- `key_name`：选填，默认取 `ssh.key_name`

### 前置条件

- 环境文件存在且包含 `platform.url`、`platform.username`、`platform.password`
- 镜像、规格、网络在当前项目中可见

### 成功判定

- 实例列表中出现目标实例
- 最终状态为 `Active` 或调用方允许的目标状态

### 返回值约定

```json
{
  "ok": true,
  "resource": "instance",
  "action": "create",
  "name": "<instance-name>",
  "status": "Active",
  "message": "instance created"
}
```

### `browser_run_code_unsafe` 示例

```javascript
async (page, args = {}) => {
  const env = JSON.parse(Deno.readTextFileSync('/tmp/easystack-env.json'));
  const platform = env.platform || {};
  const resources = env.resources || {};
  const ssh = env.ssh || {};
  const input = {
    name: args.name,
    image: args.image || resources.image_name,
    flavor: args.flavor || resources.flavor,
    network: args.network || resources.network_name,
    subnet: args.subnet || resources.subnet_name,
    keyName: args.key_name || ssh.key_name || null
  };
  if (!input.name) {
    return { ok: false, resource: 'instance', action: 'create', status: 'invalid', message: 'name is required' };
  }
  await page.goto(`${platform.url}/eec/instances/create-instance`);
  await page.waitForLoadState('networkidle');
  return { ok: true, resource: 'instance', action: 'create', name: input.name, status: 'Active', message: 'instance created' };
}
```
```

Expected: the section is template-based, JS-only, env-driven, and explicit about validation.

- [ ] **Step 4: Replace the delete-instance and attach-volume sections with the new template**

Write two sections following the same structure. Use result payloads like:

```json
{
  "ok": true,
  "resource": "instance",
  "action": "delete",
  "name": "<instance-name>",
  "status": "deleted",
  "message": "instance removed from list"
}
```

and:

```json
{
  "ok": true,
  "resource": "volume",
  "action": "attach",
  "name": "<volume-name>",
  "status": "In use",
  "message": "volume attached to instance"
}
```

Expected: all three migrated operations use the same section order, the same result shape, and env-driven examples.

- [ ] **Step 5: Mark the remaining instance operations as legacy**

Add a compact section like:

```md
## 待迁移操作

以下操作仍保留旧格式示例，后续按统一模板迁移：

- start / stop / reboot_instance
- clone_instance
- reset_password
- edit_instance_name
- lock / unlock_instance
- create_snapshot
- snapshot_rollback
- delete_instance_snapshot
- create_keypair
- delete_keypair
```

Expected: readers can tell exactly which operations are migrated and which are not.

- [ ] **Step 6: Verify `instance-ops.md` matches the new contract**

Run:

```bash
rg -n "admin@example.org|pgc@qq.com|172\\.32|172\\.35|1234qwer|test@passw0rd|Admin@ES20|playwright.sync_api" easystack-ui-test/patterns/instance-ops.md
rg -n "^## `create_instance`|^## `delete_instance`|^## `attach_volume`|^## 待迁移操作" easystack-ui-test/patterns/instance-ops.md
```

Expected: the first command prints no matches; the second command shows the migrated operations and the legacy marker section.

### Task 3: Convert Quick Reference Into a Migration-Aware Index

**Files:**
- Modify: `easystack-ui-test/patterns/quick-reference.md`
- Reference: `easystack-ui-test/patterns/login.md`
- Reference: `easystack-ui-test/patterns/instance-ops.md`
- Reference: `easystack-ui-test/patterns/volume-ops.md`
- Reference: `easystack-ui-test/patterns/network-ops.md`

- [ ] **Step 1: Review the current quick reference and collect the operations that should stay visible**

Run:

```bash
sed -n '1,220p' easystack-ui-test/patterns/quick-reference.md
```

Expected: confirm the current file is a function list and identify which entries should be preserved in the new index.

- [ ] **Step 2: Rewrite the quick reference intro and status legend**

Add an opening like:

```md
# 常用操作索引

本文件用于索引 `patterns/` 当前提供的原子操作能力，不代表每一项都
已经完成统一模板迁移。

## 状态说明

- `ready`：已按统一契约整理
- `legacy`：仍为旧格式示例
- `planned`：已纳入后续迁移范围
```
```

Expected: the file becomes an index with an explicit migration legend.

- [ ] **Step 3: Replace the old table with a contract-aware index table**

Create a table like:

```md
| 操作名 | 资源域 | 文档位置 | 必填参数 | 默认参数来源 | 返回结果 | 当前状态 |
|--------|--------|----------|----------|--------------|----------|----------|
| `create_instance` | instance | `patterns/instance-ops.md` | `name` | `resources.*`, `ssh.key_name` | `ok/resource/action/name/status/message` | `ready` |
| `delete_instance` | instance | `patterns/instance-ops.md` | `name` | 无 | `ok/resource/action/name/status/message` | `ready` |
| `attach_volume` | instance | `patterns/instance-ops.md` | `instance`, `volume` | 无 | `ok/resource/action/name/status/message` | `ready` |
| `create_volume` | volume | `patterns/volume-ops.md` | `name`, `size` | `resources.volume_type` | legacy string result | `legacy` |
| `bind_floating_ip` | network | `patterns/network-ops.md` | `instance` | 平台可用浮动 IP | legacy string result | `legacy` |
```
```

Expected: the table declares which items already follow the new template and which still use legacy semantics.

- [ ] **Step 4: Add a short usage flow that points readers to the right document**

Add guidance like:

```md
## 使用流程

1. 先读 `patterns/login.md`，确认环境和会话前置条件
2. 再读对应资源域文档执行操作
3. 若状态为 `legacy`，执行前先人工核对返回值和示例细节
```

Expected: the index becomes actionable instead of only descriptive.

- [ ] **Step 5: Verify quick reference aligns with the migrated docs**

Run:

```bash
rg -n "create_instance|delete_instance|attach_volume|ready|legacy" easystack-ui-test/patterns/quick-reference.md
```

Expected: output shows the new legend and the three ready operations.

### Task 4: Run Final Documentation Verification

**Files:**
- Verify: `easystack-ui-test/patterns/login.md`
- Verify: `easystack-ui-test/patterns/instance-ops.md`
- Verify: `easystack-ui-test/patterns/quick-reference.md`

- [ ] **Step 1: Verify there are no hard-coded credentials in the target docs**

Run:

```bash
rg -n "admin@example.org|pgc@qq.com|172\\.32|172\\.35|1234qwer|test@passw0rd|Admin@ES20" \
  easystack-ui-test/patterns/login.md \
  easystack-ui-test/patterns/instance-ops.md \
  easystack-ui-test/patterns/quick-reference.md
```

Expected: no output.

- [ ] **Step 2: Verify the target docs no longer contain Python Playwright templates**

Run:

```bash
rg -n "playwright.sync_api|def login\\(|page\\.goto\\('|page\\.fill\\('|page\\.click\\('" \
  easystack-ui-test/patterns/login.md \
  easystack-ui-test/patterns/instance-ops.md \
  easystack-ui-test/patterns/quick-reference.md
```

Expected: no output from Python-specific patterns; JS examples may remain only in fenced `javascript` blocks using `async (page`.

- [ ] **Step 3: Verify the new documents line up with the spec scope**

Run:

```bash
sed -n '1,220p' easystack-ui-test/patterns/login.md
sed -n '1,260p' easystack-ui-test/patterns/instance-ops.md
sed -n '1,220p' easystack-ui-test/patterns/quick-reference.md
```

Expected: confirm the scope stayed limited to the three target docs and that the migrated operations are exactly `create_instance`, `delete_instance`, and `attach_volume`.

- [ ] **Step 4: Review the git diff before handoff**

Run:

```bash
git diff -- docs/superpowers/plans/2026-06-17-easystack-ui-test-patterns-plan.md \
  easystack-ui-test/patterns/login.md \
  easystack-ui-test/patterns/instance-ops.md \
  easystack-ui-test/patterns/quick-reference.md
```

Expected: diff only shows the planned documentation refactor and no unrelated file changes.
