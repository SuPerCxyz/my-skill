# easystack-ui-test Foundation Paths Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Unify the EasyStack UI test foundation docs around one MCP Playwright contract, one env schema, and one dual-track page-path model while removing sensitive samples from the touched files.

**Architecture:** Treat `connection.md`, `navigation.md`, and `SKILL.md` as the authority layer, then fix only the directly conflicting path fragments in a small set of downstream docs. Use “current primary path + historical/alias path + note” everywhere paths are authoritative, and keep non-authoritative docs narrowly patched instead of broadly rewritten.

**Tech Stack:** Markdown, `apply_patch`, `rg`, `sed`

---

### Task 1: Rebuild `connection.md` as the Authority for Env and Login Rules

**Files:**
- Modify: `easystack-ui-test/connection.md`
- Reference: `easystack-ui-test/patterns/login.md`
- Reference: `easystack-ui-test/SKILL.md`
- Reference: `docs/superpowers/specs/2026-06-17-easystack-ui-test-foundation-paths-design.md`

- [ ] **Step 1: Review the current connection doc and the new authority contract**

Run:

```bash
sed -n '1,220p' easystack-ui-test/connection.md
sed -n '1,220p' easystack-ui-test/patterns/login.md
sed -n '1,220p' docs/superpowers/specs/2026-06-17-easystack-ui-test-foundation-paths-design.md
```

Expected: confirm `connection.md` must become an MCP Playwright authority doc for env source, login rules, session reuse, waiting, and verification; it must no longer look like a Python script tutorial.

- [ ] **Step 2: Rewrite `connection.md` into a JavaScript / MCP Playwright authority doc**

Replace the file with a structure like:

```md
# 连接与登录

## 适用范围

本文件定义 EasyStack UI 自动化的基础连接与登录规则。
所有示例统一面向 MCP Playwright 的 `browser_run_code_unsafe`。

## 环境配置来源

- 统一从 `/tmp/easystack-env.json` 读取
- 必填字段：
  - `platform.url`
  - `platform.username`
  - `platform.password`
- 示例不写真实凭证

## SSL 与浏览器上下文

- 自签名证书场景下使用 `ignoreHTTPSErrors` / 等价配置
- 会话复用优先于重复登录

## 登录契约

1. 读取 `platform.*`
2. 优先复用现有会话
3. 必要时访问 `/auth_login/?next=<目标路径>`
4. 使用显式选择器填写 `#id_username`、`#id_password`
5. 用 URL 和稳定页面标记验证成功

## 会话复用

- 当前已在目标受保护路径且稳定标记可见时，可复用
- 已登录但不在目标页时，先导航到目标页再验证
- 失效则走登录流程

## 等待与验证

- 优先 `waitForURL`、`waitForLoadState`、`locator(...).waitFor()`
- `waitForTimeout` 只做兜底

## 标准示例

```javascript
async (page, args = {}) => {
  const fs = await import('node:fs/promises');
  const env = JSON.parse(await fs.readFile('/tmp/easystack-env.json', 'utf8'));
  const targetPath = args.targetPath ?? '/overview';
  const username = args.username ?? env.platform.username;
  const password = args.password ?? env.platform.password;
  const loginUrl = new URL(`/auth_login/?next=${targetPath}`, env.platform.url).toString();
  await page.goto(loginUrl);
  if (page.url().includes('/auth_login')) {
    await page.locator('#id_username').fill(username);
    await page.locator('#id_password').fill(password);
    await page.locator('button.js-loginBtn').click();
  }
  await page.waitForLoadState('networkidle');
  return {
    ok: true,
    resource: 'session',
    action: 'login',
    status: 'ready',
    message: 'session ready',
    url: page.url()
  };
}
```
```

Expected: the new file is JS-only, env-driven, de-sensitized, and aligned with `patterns/login.md`.

- [ ] **Step 3: Verify `connection.md` no longer contains Python templates or real credentials**

Run:

```bash
rg -n "playwright.sync_api|admin@example.org|pgc@qq.com|172\\.32|172\\.35|1234qwer|test@passw0rd|Admin@ES20" easystack-ui-test/connection.md
```

Expected: no output.

### Task 2: Rebuild `navigation.md` as the Authority for Menu and Path Baselines

**Files:**
- Modify: `easystack-ui-test/navigation.md`
- Reference: `easystack-ui-test/patterns/platform-info.md`
- Reference: `easystack-ui-test/network/network.md`
- Reference: `easystack-ui-test/network/router.md`
- Reference: `easystack-ui-test/network/vnic.md`
- Reference: `easystack-ui-test/image/image.md`

- [ ] **Step 1: Review the current navigation doc and collect conflicting path systems**

Run:

```bash
sed -n '1,220p' easystack-ui-test/navigation.md
rg -n "/neutron/|/ens/|/glance/|/container-registry/" easystack-ui-test/navigation.md easystack-ui-test/patterns/platform-info.md easystack-ui-test/network/network.md easystack-ui-test/network/router.md easystack-ui-test/network/vnic.md easystack-ui-test/image/image.md
```

Expected: identify the current `/neutron/*` vs `/ens/*` and `/glance/*` vs `/container-registry/*` conflicts.

- [ ] **Step 2: Rewrite `navigation.md` around MCP Playwright semantics and the dual-track path model**

Replace the Python-style examples and URL table with content like:

```md
# 页面导航

## 适用范围

本文件定义菜单导航、页面入口和路径基线。

## 导航语义

- 所有示例统一面向 MCP Playwright / JavaScript
- 已知 URL 时可直接 `goto()`
- 不确定入口时优先通过“产品与服务”菜单导航

## 顶部导航元素

| 元素 | 选择器 | 说明 |
|------|--------|------|
| 产品与服务 | `a.action-products-menu` | 打开服务目录 |
| 用户菜单 | `a.action-user` | 用户会话操作 |

## 当前主路径与历史/别名路径

| 页面 | 当前主路径 | 历史/别名路径 | 说明 |
|------|------------|---------------|------|
| 网络 | `/ens/networks` | `/neutron/networks` | 默认执行入口使用主路径 |
| 路由器 | `/ens/routers` | `/neutron/routers` | 默认执行入口使用主路径 |
| 虚拟网卡 | `/ens/nics` | 无 | 当前资料一致 |
| 镜像 | `/container-registry/image` | `/glance/images` | 旧文档可能出现别名路径 |
| 云主机 | `/eec/instances` | 无 | 当前资料一致 |

## 导航验证

- 到达目标页后使用 URL + 页面主表格/主区域验证
- 不以固定 sleep 作为主成功信号

## 标准示例

```javascript
async (page, { targetPath = '/eec/instances' } = {}) => {
  await page.goto(new URL(targetPath, 'https://example.local').toString());
  await page.waitForLoadState('networkidle');
  await page.locator('main, .ant-table').first().waitFor({ state: 'visible', timeout: 5000 });
  return { ok: true, action: 'navigate', path: targetPath, url: page.url() };
}
```
```

Expected: `navigation.md` becomes the authoritative path baseline and explicitly explains primary vs historical paths.

- [ ] **Step 3: Verify `navigation.md` now uses the dual-track path model**

Run:

```bash
rg -n "当前主路径|历史/别名路径|/ens/|/neutron/|/glance/|/container-registry/" easystack-ui-test/navigation.md
```

Expected: output shows the authority table and the dual-track wording.

### Task 3: Align `SKILL.md` With the New Authority Layer and Remove Sensitive Samples

**Files:**
- Modify: `easystack-ui-test/SKILL.md`
- Reference: `easystack-ui-test/connection.md`
- Reference: `easystack-ui-test/navigation.md`
- Reference: `easystack-ui-test/patterns/login.md`

- [ ] **Step 1: Review `SKILL.md` sections that duplicate env, login, and path rules**

Run:

```bash
sed -n '1,280p' easystack-ui-test/SKILL.md
rg -n "platform\\.url|platform\\.username|platform\\.password|/auth_login|/ens/|/neutron/|/glance/|/container-registry|1234qwer|pgc@qq.com|172\\.32|172\\.35" easystack-ui-test/SKILL.md
```

Expected: identify the duplicated env schema, path statements, and real credential examples that should now defer to `connection.md` and `navigation.md`.

- [ ] **Step 2: Rewrite duplicated authority sections to reference the foundation docs**

Update the relevant sections so they say things like:

```md
### 共享基础

| 当前需要... | 阅读 |
|------------|------|
| 环境配置、登录契约、会话复用 | [connection.md](connection.md) |
| 菜单导航、页面入口、路径基线 | [navigation.md](navigation.md) |

### 环境配置文件（/tmp/easystack-env.json）

使用 `platform.url`、`platform.username`、`platform.password` 作为基础登录字段。
示例值统一使用占位值或由用户运行时提供，不在 skill 中保存真实凭证。

### 路径说明

页面路径以 `navigation.md` 的“当前主路径 + 历史/别名路径”表为准。
顶层 skill 不重复定义另一套冲突路径表。
```

Expected: `SKILL.md` becomes a coordinator/index instead of a competing authority source.

- [ ] **Step 3: De-sensitize any touched env and login examples in `SKILL.md`**

Replace any real values with content like:

```json
{
  "platform": {
    "url": "https://example.local",
    "username": "<USERNAME>",
    "password": "<PASSWORD>"
  }
}
```
```

Expected: no real URL, username, or password remain in touched sections.

- [ ] **Step 4: Verify `SKILL.md` no longer contains real credentials in the touched scope**

Run:

```bash
rg -n "pgc@qq.com|1234qwer|172\\.32|172\\.35|Admin@ES20|test@passw0rd" easystack-ui-test/SKILL.md
```

Expected: no output.

### Task 4: Sync Directly Conflicting Downstream Path Fragments to the Authority Model

**Files:**
- Modify: `easystack-ui-test/patterns/platform-info.md`
- Modify: `easystack-ui-test/relationships.md`
- Modify: `easystack-ui-test/network/network.md`
- Modify: `easystack-ui-test/network/router.md`
- Modify: `easystack-ui-test/network/vnic.md`
- Modify: `easystack-ui-test/image/image.md`
- Reference: `easystack-ui-test/navigation.md`

- [ ] **Step 1: Review the directly conflicting downstream path fragments**

Run:

```bash
rg -n "/neutron/|/ens/|/glance/|/container-registry/" easystack-ui-test/patterns/platform-info.md easystack-ui-test/relationships.md easystack-ui-test/network/network.md easystack-ui-test/network/router.md easystack-ui-test/network/vnic.md easystack-ui-test/image/image.md
```

Expected: collect the exact lines that need dual-track wording or direct path correction.

- [ ] **Step 2: Normalize `patterns/platform-info.md` and `relationships.md` to authority wording**

Update these files so path lines look like:

```md
| 网络管理页 | 当前主路径：`/ens/networks`；历史/别名路径：`/neutron/networks` |
| 路由器页 | 当前主路径：`/ens/routers`；历史/别名路径：`/neutron/routers` |
| 镜像管理页 | 当前主路径：`/container-registry/image`；历史/别名路径：`/glance/images` |
```

Expected: these bridging docs no longer state a single conflicting path as absolute fact.

- [ ] **Step 3: Patch `network/*.md` and `image/image.md` only where execution would be misled**

For example, update introductory URL blocks to include both path types:

```md
| URL | 当前主路径：`https://<IP>/ens/networks` |
| 历史/别名路径 | `https://<IP>/neutron/networks` |
```

and:

```md
| URL | 当前主路径：`https://<IP>/container-registry/image` |
| 历史/别名路径 | `https://<IP>/glance/images` |
```

Expected: only the directly conflicting path statements are changed; the rest of each large doc stays intact.

- [ ] **Step 4: Verify the downstream path fragments now align with the authority layer**

Run:

```bash
rg -n "当前主路径|历史/别名路径|/neutron/|/ens/|/glance/|/container-registry/" easystack-ui-test/patterns/platform-info.md easystack-ui-test/relationships.md easystack-ui-test/network/network.md easystack-ui-test/network/router.md easystack-ui-test/network/vnic.md easystack-ui-test/image/image.md
```

Expected: output shows dual-track wording instead of unexplained conflicting single-path statements.

### Task 5: Run Final Foundation-Layer Verification

**Files:**
- Verify: `easystack-ui-test/connection.md`
- Verify: `easystack-ui-test/navigation.md`
- Verify: `easystack-ui-test/SKILL.md`
- Verify: `easystack-ui-test/patterns/platform-info.md`
- Verify: `easystack-ui-test/relationships.md`
- Verify: `easystack-ui-test/network/network.md`
- Verify: `easystack-ui-test/network/router.md`
- Verify: `easystack-ui-test/network/vnic.md`
- Verify: `easystack-ui-test/image/image.md`

- [ ] **Step 1: Verify touched authority files contain no real credentials**

Run:

```bash
rg -n "pgc@qq.com|1234qwer|172\\.32|172\\.35|Admin@ES20|test@passw0rd" \
  easystack-ui-test/connection.md \
  easystack-ui-test/navigation.md \
  easystack-ui-test/SKILL.md \
  easystack-ui-test/patterns/platform-info.md \
  easystack-ui-test/relationships.md \
  easystack-ui-test/network/network.md \
  easystack-ui-test/network/router.md \
  easystack-ui-test/network/vnic.md \
  easystack-ui-test/image/image.md
```

Expected: no output.

- [ ] **Step 2: Verify the touched authority files no longer contain Python Playwright templates**

Run:

```bash
rg -n "playwright.sync_api|def login\\(|page\\.goto\\('|page\\.fill\\('|page\\.click\\('" \
  easystack-ui-test/connection.md \
  easystack-ui-test/navigation.md
```

Expected: no output.

- [ ] **Step 3: Verify the authority layer agrees on the env contract**

Run:

```bash
rg -n "platform\\.url|platform\\.username|platform\\.password" \
  easystack-ui-test/connection.md \
  easystack-ui-test/SKILL.md \
  easystack-ui-test/patterns/login.md
```

Expected: all three files use the same `platform.*` contract.

- [ ] **Step 4: Verify path statements now use the dual-track model in the touched scope**

Run:

```bash
rg -n "当前主路径|历史/别名路径" \
  easystack-ui-test/navigation.md \
  easystack-ui-test/patterns/platform-info.md \
  easystack-ui-test/relationships.md \
  easystack-ui-test/network/network.md \
  easystack-ui-test/network/router.md \
  easystack-ui-test/network/vnic.md \
  easystack-ui-test/image/image.md
```

Expected: touched path-authority fragments use the dual-track wording.

- [ ] **Step 5: Review the final patch boundary**

Run:

```bash
git status --short -- \
  docs/superpowers/specs/2026-06-17-easystack-ui-test-foundation-paths-design.md \
  docs/superpowers/plans/2026-06-17-easystack-ui-test-foundation-paths-plan.md \
  easystack-ui-test/connection.md \
  easystack-ui-test/navigation.md \
  easystack-ui-test/SKILL.md \
  easystack-ui-test/patterns/platform-info.md \
  easystack-ui-test/relationships.md \
  easystack-ui-test/network/network.md \
  easystack-ui-test/network/router.md \
  easystack-ui-test/network/vnic.md \
  easystack-ui-test/image/image.md
```

Expected: only the scoped spec/plan files and the touched authority/sync docs appear.
