# 我的 Skills

个人 Skill 仓库，用于保存和分享自定义的 AI 编程助手 skills。

## Skills 列表

| Skill | 描述 |
|-------|------|
| [context-efficient-rules](context-efficient-rules/) | 上下文精简 Agent 规则 - 适用于 Claude Code / Router / ccswitch，默认不调用 MCP、不读大文件、不做大范围搜索，含 K8s / OpenStack / Git / 日志 / GUI 测试领域精简规则 |
| [windows-mcp-operation](windows-mcp-operation/) | Windows MCP 桌面操作 - 通过 windows-mcp server 操作和观察真实 Windows 桌面，包括截屏、窗口控制、鼠标键盘操作、系统管理等 |
| [easystack-env-debugging](easystack-env-debugging/) | EasyStack 环境调试 - 根据 IP 自动选择 SSH 方式（172.18.x.x 走跳板机，其他直连），验证环境可访问性后对 OpenStack 服务进行调试 |
| [easystack-ci-test](easystack-ci-test/) | EasyStack OpenStack 项目通用 CI 测试 - 运行 tox cover/pep8，自动修复失败项直到测试全部通过并满足覆盖率要求 |
| [media-library-organizer](media-library-organizer/) | 媒体库整理 - TMDB 刮削 + 重命名 + NFO 生成 + 图片下载，支持电影/电视剧/综艺/纪录片/动漫，含完整安全机制和回滚 |
| [easystack-cloud-web-e2e](easystack-cloud-web-e2e/) | EasyStack 云平台 Web UI 端到端自动化测试 - 基于 agent-browser 的原子操作库、页面知识库和测试编排规范，支持云主机/云硬盘/网络等资源操作的 UI 自动化 |

## 使用方法

将本仓库 clone 到本地，在 AI 编程助手中引用 skill 路径即可使用。

```bash
git clone https://git.soocoo.xyz/superc/my-skill.git
```

## 添加新 Skill

在本仓库根目录下新建 skill 文件夹，编写 `SKILL.md` 和 `README.md` 及相关文档即可。
