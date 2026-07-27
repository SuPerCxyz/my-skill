# 连接与登录

## 适用范围

本文件定义 EasyStack Cloud Web E2E的基础连接、登录、会话复用与页面
验证规则。

所有真实 UI 操作统一使用 `agent-browser`。其他浏览器自动化框架不得作为默认执行入口。

## agent-browser 前置

执行真实 UI 测试前先检查 `agent-browser`。命令不存在时, 不要自动安装; 先向用户
报告缺失项、以下建议命令和环境影响, 等待明确确认。

```bash
command -v agent-browser
```

用户确认后优先安装到用户目录:

```bash
npm i -g --prefix "$HOME/.local" agent-browser
"$HOME/.local/bin/agent-browser" install
"$HOME/.local/bin/agent-browser" skills get core
```

只有用户明确要求全局安装时才使用 `npm i -g agent-browser`。安装或启动失败时,
停止 UI 测试, 不降级到其他浏览器自动化框架。

## 默认启动参数

EasyStack 测试环境默认按自签名证书处理;本机常见容器/VM 环境也可能需要
禁用 Chrome sandbox。首次启动浏览器必须使用全局参数:

```bash
export AGENT_BROWSER_SESSION="easystack-<run-id>"
agent-browser --args '--no-sandbox' --ignore-https-errors open "$PLATFORM_URL/auth_login/"
```

如果看到 `net::ERR_CERT_AUTHORITY_INVALID`，说明未使用
`--ignore-https-errors`。如果看到 `No usable sandbox` 或 Chrome
`DevToolsActivePort` 启动失败，说明未使用 `--args '--no-sandbox'`。

如果 agent-browser daemon 已经运行，后续命令可能提示这些参数被忽略。此时
不要直接关闭所有会话;先判断当前 daemon 是否由本次任务独占。若不能确认，
停止真实 UI 测试并向用户说明需要关闭或重启 agent-browser daemon。

只有确认当前 daemon/会话由本次任务独占，或用户明确同意关闭所有
agent-browser 会话时，才执行:

```bash
agent-browser close --all
agent-browser --args '--no-sandbox' --ignore-https-errors open "$PLATFORM_URL/auth_login/"
```

## 环境配置来源

- 统一从 `/tmp/easystack-env.json` 读取环境配置
- 登录相关必填字段:
  - `platform.url`
  - `platform.username`
  - `platform.password`
- 项目上下文可选字段:
  - `resources.project_name`
- 截图目录可选字段:
  - `screenshot_dir`
- 测试环境凭据可直接由环境文件或调用参数提供
- skill 示例和报告不沉淀真实密码，避免把临时测试信息写入仓库

推荐的最小环境结构:

```json
{
  "platform": {
    "url": "https://example.local",
    "username": "<USERNAME>",
    "password": "<PASSWORD>"
  }
}
```

## 浏览器上下文与 SSL

EasyStack Cloud 常见为自签名证书场景，浏览器上下文应允许忽略证书错
误。

约定:

- 优先复用已有浏览器上下文与当前页面
- 仅在会话无效时重新走登录流程
- 会话复用优先于重复登录

## 登录契约

1. 先读取 `platform.url`、`platform.username`、`platform.password`
2. 结合目标路径拼出登录页地址
3. 优先判断当前会话是否已可复用
4. 若会话不可复用，再访问登录页并填写表单
5. 登录成功必须通过 URL 与稳定页面标记联合验证

登录页特殊注意:

- 当前 EasyStack 登录页的可见密码框 `#id_password` 本身没有 `name`;真正提交到
  后端的是隐藏字段 `#pwd[name="password"]`。
- 因此不要只依赖“字段里看起来有值”就立刻提交;必须确认 `Sign In` 已从不可提交
  的普通容器/占位态切换为真正的可点击 `button`。
- 现场验证中，先对用户名和密码做真实输入，再触发一次 `Tab` 或等价焦点切换，
  能更稳定地让前端校验和密码处理逻辑完成。
- 如果提交后仍停在 `/auth_login/` 或 `/ems_dashboard_api/auth_login/`，先检查
  页面是否出现 `Please input user password`、`Invalid credentials.` 或 captcha，
  不要立即假定是 ref 失效或按钮点击失败。

登录表单的稳定定位方式基线:

| 字段 | 定位方式 |
|------|--------|
| 用户名 | `#id_username` |
| 密码 | `#id_password` |
| 登录按钮 | `button.js-loginBtn` |

## 会话复用契约

- 当前页面已位于目标受保护路径，且稳定页面标记可见时，可直接复用会话
- 若已登录但当前不在目标页面，先导航到目标页面，再做最终验证
- 若页面跳回 `/auth_login/`，视为会话失效，需重新登录
- 复用判断优先依据 URL、主区域、主表格等可观测信号

## 项目上下文契约

登录后必须校验左上角项目切换器 `.projects-switch-wrapper` 的当前项目。
如果用例或环境配置指定了 `resources.project_name`，当前项目不一致时必须先切换
到目标项目，再执行资源创建、挂载、绑定等操作。

项目上下文错误会导致页面按钮被置为 disabled，或者列表资源为空。例如当前用户
菜单显示为 `pgc` 不代表左上角项目也是 `pgc`;必须以 `.projects-switch-wrapper`
显示值为准。

现场验证补充:

- `/tmp/easystack-env.json` 未显式提供 `resources.project_name` 时，也应先检查
  左上角项目。
- 如果当前项目没有创建目标资源所需的配额、网络、镜像或卷类型，必须先切到
  正确项目，再执行资源创建、挂载、绑定等操作。

项目切换示例:

```bash
agent-browser eval --stdin <<'JS'
(() => {
  const targetProject = 'pgc';
  const current = document.querySelector('.projects-switch-wrapper')?.innerText.trim();
  if (current === targetProject) {
    return { ok: true, terminal: true, submitted: false, project: current, switched: false };
  }

  document.querySelector('.projects-switch-wrapper')?.click();
  const option = [...document.querySelectorAll('.es-dropdown-projects li, .es-header__projects-list li')]
    .find((item) => item.innerText.trim() === targetProject);
  if (!option) {
    return { ok: false, terminal: true, submitted: false, project: current, message: 'target project not found' };
  }
  option.click();
  return { ok: true, terminal: true, submitted: true, project: targetProject, switched: true };
})()
JS
```

## 等待与页面验证

- 首选 `agent-browser wait`、`agent-browser get url`、`agent-browser snapshot -i`
  验证页面状态
- 固定时长等待仅作为兜底，不作为主成功信号
- 登录后优先清理通知类遮挡，再验证页面已可操作

常用验证信号:

- 目标 URL 片段命中
- `main` 区域可见
- 主表格 `.ant-table` 可见

## 标准执行形态

登录操作应合并为少量 `agent-browser` 调用。环境文件由 shell 读取后注入。
测试环境密码可直接用于执行, 但不要写入 skill 文档、操作库模板或测试报告。运行时
生成的 VM 密码只保存在当前进程内存; 工具必须落盘时写入权限为 `0600` 的本次运行
临时文件, 报告仅记录该临时引用和生成方式。验证结束后删除临时文件。

```bash
export AGENT_BROWSER_SESSION="easystack-<run-id>"
agent-browser --args '--no-sandbox' --ignore-https-errors open "$LOGIN_URL"
agent-browser fill '#id_username' "$EASYSTACK_USERNAME"
agent-browser fill '#id_password' "$EASYSTACK_PASSWORD"
agent-browser click 'button.js-loginBtn'
agent-browser wait 'main, .ant-table'
agent-browser get url
```
