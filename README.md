# 我的 Skills

个人 Skill 仓库，用于保存和分享自定义的 AI 编程助手 skills。

## Skills 列表

| Skill | 描述 |
|-------|------|
| [context-efficient-rules](context-efficient-rules/) | 上下文精简 Agent 规则 — 适用于 Claude Code / Router / ccswitch，默认不调用 MCP、不读大文 / 不做大范围搜索，含工具调用限制、Autocompact 防护与大输出处理流程 |
| [easystack-ci-test](easystack-ci-test/) | EasyStack OpenStack 项目通用 CI 测试 — 运行 tox cover/pep8，自动修复失败项直到测试全部通过并满足覆盖率要求 |
| [easystack-cloud-web-e2e](easystack-cloud-web-e2e/) | EasyStack 云平台 Web UI 端到端自动化测试 — 基于 agent-browser 的原子操作库、页面知识库与测试编排规范，支持云主机 / 云硬盘 / 网络等资源操作的 UI 自动化 |
| [easystack-env-debugging](easystack-env-debugging/) | EasyStack 环境后台只读检查 — 支持直连、172.18.x.x 跳板机、JumpServer 三种入口，变更操作需明确授权 |
| [easystack-log-analysis](easystack-log-analysis/) | EasyStack OpenStack 集群日志分析 — eslog 解压、容器化日志目录映射、跨服务跨节点根因定位;覆盖云主机生命周期 / 云盘挂载卸载 / 网络 / 镜像 / 裸金属 Ironic 等场景 |
| [media-library-organizer](media-library-organizer/) | 媒体库整理 — TMDB 刮削 + 重命名 + NFO 生成 + 图片下载，支持电影 / 电视剧 / 综艺 / 纪录片 / 动漫，含 dry-run 安全机制与回滚 |
| [windows-mcp-operation](windows-mcp-operation/) | Windows MCP 桌面操作 — 通过 windows-mcp server 操作和观察真实 Windows 桌面，包括截屏、窗口控制、鼠标键盘操作、系统管理等 |

> 目录下 `docs/superpowers/` 为 superpowers 工作流产生的 plan/spec 设计文档存档，并非 skill，仅作参考留档。

## 使用方法

将本仓库 clone 到本地，在 AI 编程助手中引用 skill 路径即可使用。

```bash
# SSH(推荐，对应仓库 remote)
git clone ssh://git@git.soocoo.xyz:10022/superc/my-skills.git

# HTTPS
git clone https://git.soocoo.xyz/superc/my-skills.git
```

## 添加新 Skill

在本仓库根目录下新建 skill 文件夹，按统一约定编写:

- `SKILL.md`(必需):开头 YAML frontmatter，包含 `name` 与双引号包裹的 `description`(建议以 "Use when..." 句式描述触发场景)
- `README.md`(推荐):该 skill 的用途、文件说明与快速开始
- 其余参考文档按需放在同目录下，并在 `SKILL.md` / `README.md` 的文件索引表中登记
