# easystack-ui-test Volume Network Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the remaining `patterns/volume-ops.md` and `patterns/network-ops.md` docs to the same ready/planned contract model already used by `login.md` and `instance-ops.md`, then sync `quick-reference.md`.

**Architecture:** Treat `volume-ops.md` and `network-ops.md` as domain-specific operation-contract docs. Each file gets a consistent header, a small ready set of migrated operations, and a name-only planned list for everything else. `quick-reference.md` becomes the authoritative status board for those new ready entries.

**Tech Stack:** Markdown, `apply_patch`, `rg`, `sed`

---

### Task 1: Rebuild `volume-ops.md` Around a Stable Ready/Planned Contract

**Files:**
- Modify: `easystack-ui-test/patterns/volume-ops.md`
- Reference: `easystack-ui-test/patterns/login.md`
- Reference: `easystack-ui-test/patterns/instance-ops.md`
- Reference: `docs/superpowers/specs/2026-06-17-easystack-ui-test-volume-network-design.md`

- [ ] **Step 1: Review the current volume operations doc and identify the high-value entries**

Run:

```bash
sed -n '1,260p' easystack-ui-test/patterns/volume-ops.md
rg -n "创建云硬盘|删除云硬盘|上传镜像|删除镜像|创建云硬盘快照|扩容云硬盘" easystack-ui-test/patterns/volume-ops.md
```

Expected: confirm `create_volume`, `delete_volume`, and `upload_image` are the ready targets; the rest can move to a planned name list.

- [ ] **Step 2: Rewrite the document header and migration-status section**

Add an opening like:

```md
# 云硬盘与镜像操作

本文件定义块存储与镜像入口的原子操作契约。所有示例统一面向
`browser_run_code_unsafe`，并依赖 `patterns/login.md`
中的共享前置能力准备登录态与目标页面。

## 使用约定

- 配置默认值来自 `/tmp/easystack-env.json`
- 显式参数优先于环境默认值
- 所有 ready 操作必须显式验证目标状态
- 返回值统一使用结构化对象

## 迁移状态

- `create_volume`: `ready`
- `delete_volume`: `ready`
- `upload_image`: `ready`
- 其他 volume / image 操作: `planned`
```

Expected: the doc clearly distinguishes the migrated volume/image entries from the planned ones.

- [ ] **Step 3: Replace the create-volume section with the new template**

Write a section like:

```md
## `create_volume`

### 用途

创建一块云硬盘，并验证其状态进入 `Available`。

### 参数

- 必填参数: `name`
- 必填参数: `size`
- 环境默认参数: `vol_type` -> `resources.volume_type`
- 显式可选参数: `description`

### 前置条件

- `/tmp/easystack-env.json` 中至少存在 `platform.url`
- 调用前已按 `patterns/login.md` 准备可复用会话
- 目标卷类型在当前项目中可见

### 成功判定

- 卷列表中出现目标卷
- 状态达到 `Available`

### 执行步骤概览

- 进入卷列表页并打开创建弹窗
- 填写名称、大小、卷类型等字段
- 提交创建请求
- 轮询卷列表直到状态达到 `Available`

### 失败信号

- 缺少 `name` / `size` / `platform.url`
- 页面跳回登录页
- 卷类型无法在当前弹窗中找到
- 轮询超时后卷仍未进入 `Available`

### 返回值约定

```json
{
  "ok": true,
  "resource": "volume",
  "action": "create",
  "name": "<volume-name>",
  "status": "Available",
  "message": "volume created",
  "url": "<current-url>"
}
```
```

Expected: create-volume now matches the same section order used in `instance-ops.md`.

- [ ] **Step 4: Replace the delete-volume and upload-image sections with the new template**

Use the same section order for:

```md
## `delete_volume`
## `upload_image`
```

For `upload_image`, use env-safe placeholder input names like `source_url`, `name`, and `os_category`, and return a structured result such as:

```json
{
  "ok": true,
  "resource": "image",
  "action": "upload",
  "name": "<image-name>",
  "status": "uploaded",
  "message": "image uploaded",
  "url": "<current-url>"
}
```

Expected: all three ready entries use JS-only, env-driven, structured-result templates.

- [ ] **Step 5: Convert the rest of the file into a planned-name section**

Add a compact section like:

```md
## 待迁移操作

以下名称当前仅保留为待迁移操作清单（`planned`），不作为当前 ready 示例：

- `create_volume_snapshot`
- `extend_volume`
- `edit_volume`
- `create_image_from_volume`
- `delete_volume_snapshot`
- `delete_image`
```

Expected: the old long-form legacy snippets are replaced by a narrow planned list instead of being left mixed into the file.

- [ ] **Step 6: Verify `volume-ops.md` no longer contains real URLs and now exposes the ready sections**

Run:

```bash
rg -n "https://172\\.|pgc@qq.com|1234qwer|playwright.sync_api" easystack-ui-test/patterns/volume-ops.md
rg -n "^## `create_volume`|^## `delete_volume`|^## `upload_image`|^## 待迁移操作" easystack-ui-test/patterns/volume-ops.md
```

Expected: the first command shows no matches; the second shows the three ready sections and the planned section.

### Task 2: Rebuild `network-ops.md` Around a Stable Ready/Planned Contract

**Files:**
- Modify: `easystack-ui-test/patterns/network-ops.md`
- Reference: `easystack-ui-test/patterns/login.md`
- Reference: `easystack-ui-test/navigation.md`
- Reference: `docs/superpowers/specs/2026-06-17-easystack-ui-test-volume-network-design.md`

- [ ] **Step 1: Review the current network operations doc and identify the ready targets**

Run:

```bash
sed -n '1,260p' easystack-ui-test/patterns/network-ops.md
rg -n "分配浮动 IP|创建网络|创建路由器|关联额外网络|解除网络关联|编辑安全组" easystack-ui-test/patterns/network-ops.md
```

Expected: confirm `allocate_floating_ip`, `create_network`, and `create_router` are the ready targets; the instance-side helper actions become planned names.

- [ ] **Step 2: Rewrite the document header and migration-status section**

Add an opening like:

```md
# 网络操作

本文件定义网络域原子操作契约。所有示例统一面向
`browser_run_code_unsafe`，并依赖 `patterns/login.md`
中的共享前置能力准备登录态与目标页面。

## 使用约定

- 配置默认值来自 `/tmp/easystack-env.json`
- 执行入口路径遵循 `navigation.md` 的当前主路径
- 所有 ready 操作必须显式验证目标状态
- 返回值统一使用结构化对象

## 迁移状态

- `allocate_floating_ip`: `ready`
- `create_network`: `ready`
- `create_router`: `ready`
- 其他 network 操作: `planned`
```

Expected: the doc clearly distinguishes ready network entries from planned names.

- [ ] **Step 3: Replace the allocate-floating-ip section with the new template**

Write a section like:

```md
## `allocate_floating_ip`

### 用途

分配一个浮动 IP，并验证新资源出现在浮动 IP 列表中。

### 参数

- 显式可选参数: `bandwidth`
- 显式可选参数: `resource_pool`

### 前置条件

- `/tmp/easystack-env.json` 中至少存在 `platform.url`
- 调用前已按 `patterns/login.md` 准备可复用会话

### 成功判定

- 列表中出现新的浮动 IP 记录

### 执行步骤概览

- 进入浮动 IP 列表页
- 打开 Allocate 弹窗
- 填写带宽等参数
- 提交后回到列表页验证新增记录

### 失败信号

- 页面跳回登录页
- Allocate 按钮不可用
- 提交后列表没有新增记录

### 返回值约定

```json
{
  "ok": true,
  "resource": "floating_ip",
  "action": "allocate",
  "name": "<allocated-ip-or-id>",
  "status": "allocated",
  "message": "floating ip allocated",
  "url": "<current-url>"
}
```
```

Expected: the floating-IP entry now matches the same contract style as the other ready docs.

- [ ] **Step 4: Replace the create-network and create-router sections with the new template**

Use the same section order for:

```md
## `create_network`
## `create_router`
```

These examples must:

- read `platform.url` from env
- use current primary paths like `/ens/networks/creator` and `/ens/routers/creator`
- return structured objects instead of free-form strings

Expected: all three ready network entries use the same stable template.

- [ ] **Step 5: Convert remaining network actions into a planned-name section**

Add:

```md
## 待迁移操作

以下名称当前仅保留为待迁移操作清单（`planned`）：

- `associate_network`
- `disassociate_network`
- `edit_security_group`
```

Expected: non-migrated network helpers are name-only entries rather than mixed old snippets.

- [ ] **Step 6: Verify `network-ops.md` now matches the new contract**

Run:

```bash
rg -n "https://172\\.|pgc@qq.com|1234qwer|playwright.sync_api" easystack-ui-test/patterns/network-ops.md
rg -n "^## `allocate_floating_ip`|^## `create_network`|^## `create_router`|^## 待迁移操作" easystack-ui-test/patterns/network-ops.md
```

Expected: the first command shows no matches; the second shows the three ready sections and the planned section.

### Task 3: Sync `quick-reference.md` With the New Ready/Planned State

**Files:**
- Modify: `easystack-ui-test/patterns/quick-reference.md`
- Reference: `easystack-ui-test/patterns/volume-ops.md`
- Reference: `easystack-ui-test/patterns/network-ops.md`

- [ ] **Step 1: Review the current quick-reference rows for volume and network entries**

Run:

```bash
sed -n '1,120p' easystack-ui-test/patterns/quick-reference.md
```

Expected: identify the current `legacy` volume rows and the currently `planned` network name-only rows that must now be updated.

- [ ] **Step 2: Update the ready rows for migrated volume and network operations**

Change the table so it includes ready rows like:

```md
| `create_volume` | `volume` | `patterns/volume-ops.md` | `name`、`size` | `resources.volume_type` | 结构化对象 `{ok,resource,action,status,message,url}` | `ready` |
| `delete_volume` | `volume` | `patterns/volume-ops.md` | `volume` / `name` | 无 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready` |
| `upload_image` | `image` | `patterns/volume-ops.md` | `name`、`source_url`、`os_category` | 调用方入参 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready` |
| `allocate_floating_ip` | `network` | `patterns/network-ops.md` | 无 | 调用方入参 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready` |
| `create_network` | `network` | `patterns/network-ops.md` | `name` | 调用方入参 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready` |
| `create_router` | `network` | `patterns/network-ops.md` | `name` | 调用方入参 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready` |
```

Expected: the index now reflects the new migrated volume/network entries.

- [ ] **Step 3: Downgrade non-migrated volume/network names to planned-only entries**

Ensure non-migrated names are represented as `planned` rather than mixed old snippets when the file only contains a name list.

Expected: the quick-reference status board matches the actual file state.

- [ ] **Step 4: Verify the ready/planned rows are visible**

Run:

```bash
rg -n "create_volume|delete_volume|upload_image|allocate_floating_ip|create_network|create_router|ready|planned" easystack-ui-test/patterns/quick-reference.md
```

Expected: output shows all six ready entries and the remaining planned entries.

### Task 4: Run Final Verification for the Volume/Network Migration

**Files:**
- Verify: `easystack-ui-test/patterns/volume-ops.md`
- Verify: `easystack-ui-test/patterns/network-ops.md`
- Verify: `easystack-ui-test/patterns/quick-reference.md`

- [ ] **Step 1: Verify there are no real URLs or credentials in the migrated target docs**

Run:

```bash
rg -n "https://172\\.|pgc@qq.com|1234qwer|Admin@ES20|test@passw0rd" \
  easystack-ui-test/patterns/volume-ops.md \
  easystack-ui-test/patterns/network-ops.md \
  easystack-ui-test/patterns/quick-reference.md
```

Expected: no output.

- [ ] **Step 2: Verify the ready sections exist and the files no longer look like old snippet dumps**

Run:

```bash
rg -n "^## `create_volume`|^## `delete_volume`|^## `upload_image`|^## `allocate_floating_ip`|^## `create_network`|^## `create_router`|^## 待迁移操作" \
  easystack-ui-test/patterns/volume-ops.md \
  easystack-ui-test/patterns/network-ops.md
```

Expected: all six ready sections and both planned-name sections are present.

- [ ] **Step 3: Verify the quick-reference status board matches the migrated files**

Run:

```bash
sed -n '1,140p' easystack-ui-test/patterns/quick-reference.md
```

Expected: `quick-reference.md` shows the six new ready entries and does not leave them as legacy/planned.

- [ ] **Step 4: Review the final patch boundary**

Run:

```bash
git status --short -- \
  docs/superpowers/specs/2026-06-17-easystack-ui-test-volume-network-design.md \
  docs/superpowers/plans/2026-06-17-easystack-ui-test-volume-network-plan.md \
  easystack-ui-test/patterns/volume-ops.md \
  easystack-ui-test/patterns/network-ops.md \
  easystack-ui-test/patterns/quick-reference.md
```

Expected: only the scoped spec/plan files and the three target docs appear.
