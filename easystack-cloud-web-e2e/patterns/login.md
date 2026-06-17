# 登录与共享前置能力

## 适用范围

本文件定义 `patterns/` 层所有原子操作共享的前置能力契约。
所有示例都以 `agent-browser` CLI 编写，不再使用其他浏览器自动化框架作为默认执行入口。

## 环境配置来源

- 统一从 `/tmp/easystack-env.json` 读取环境配置
- 运行前先读取配置，再决定登录地址、用户名和密码
- 测试环境凭据可直接由环境文件或入参提供
- skill 示例和测试报告不沉淀真实密码
- 如果缺少 `agent-browser`，先安装并执行 `agent-browser skills get core`

### 必填前置字段

- `platform.url`
- `platform.username`
- `platform.password`

### 可选运行时覆盖

- 调用方可通过 `args.targetPath` 覆盖默认跳转路径；示例里它可以回退到固定路径
- 调用方可通过 `args.username`、`args.password` 覆盖环境中的账号信息
- 若未传入覆盖值，则使用环境配置中的 `platform.username` 与 `platform.password`

## 登录契约

1. 先读取环境配置，拼出目标登录地址
2. 进入页面后先检查是否已经处于已登录状态
3. 如未登录，再填写账号与密码并提交表单
4. 登录成功必须通过 URL 变化或关键页面元素确认，不能只看点击结果
5. 登录后如出现通知、遮挡层或首次弹窗，先清理再做页面验证

## 会话复用契约

- 优先复用当前 `agent-browser` 会话
- 只有当当前页面已经位于目标受保护路径（或与目标路径匹配的子路径），并且稳定页面标记已可见时，才可判定会话可复用
- 若已登录但当前不在目标页面，先跳转到目标页面，再做最终验证
- 若会话失效，再回到登录流程
- 复用判断应尽量基于可观测状态，不依赖固定等待

## 通用辅助动作

- 页面加载后优先等待目标页面进入可操作状态
- 首选 `agent-browser wait`、`agent-browser get url`、`agent-browser snapshot -i`
- 固定等待只能作为兜底，不可作为主成功信号
- 遇到通知弹层时，优先清理 `.ant-notification-notice` 等遮挡元素
- 清理动作只用于解除遮挡，不替代页面验证

## 返回值约定

所有登录相关共享能力统一返回结构化对象：

```json
{
  "ok": true,
  "loggedIn": true,
  "reusedSession": false,
  "envSource": "/tmp/easystack-env.json",
  "url": "https://example.local/overview",
  "message": "login ready"
}
```

失败时保持同一结构，至少包含：

- `ok: false`
- `loggedIn: false`
- `message` 写入关键失败原因
- `url` 写入最后可见页面地址

## 标准示例

```bash
export AGENT_BROWSER_SESSION="easystack-<run-id>"
agent-browser --args '--no-sandbox' --ignore-https-errors open "$LOGIN_URL"
agent-browser fill '#id_username' "$EASYSTACK_USERNAME"
agent-browser fill '#id_password' "$EASYSTACK_PASSWORD"
agent-browser click 'button.js-loginBtn' || agent-browser find text 'Sign In' click
agent-browser wait 'main, .ant-table'
agent-browser get url
```

注意：不同版本登录页的提交按钮可能没有 `button.js-loginBtn`，但按钮文本为
`Sign In`。提交后必须用 URL 或 `Overview` / `Service Catalog` 等受保护页标记
验证登录成功，不能只以点击命令返回成功作为登录成功。
