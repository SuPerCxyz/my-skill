# 我的 Skills

个人 Skill 仓库，用于保存和分享自定义的 Claude Code skills。

## Skills 列表

| Skill | 描述 |
|-------|------|
| [easystack-osinos-debugging](easystack-osinos-debugging/) | EasyStack OSINOS 环境调试 skill，涵盖服务状态检查、日志分析、Pod 诊断、Nova 维护、脚本工具等 |

## 使用方法

将本仓库 clone 到本地，在你的 Claude Code 配置中引用 skill 路径即可使用。

```bash
git clone https://git.soocoo.xyz/superc/my-skill.git
```

## 目录结构

```
.
├── easystack-osinos-debugging/
│   ├── SKILL.md            # Skill 主入口定义
│   ├── access.md           # 访问与网络连通性检查
│   ├── auth.md             # 认证与鉴权排查
│   ├── code-debug.md       # 代码级调试指南
│   ├── logs.md             # 日志查看与分析
│   ├── nova-maintenance.md # Nova 维护操作
│   ├── pods.md             # K8s Pod 诊断
│   ├── reference.md        # 参考信息速查
│   ├── scenarios.md        # 常见故障场景
│   └── scripts.md          # 常用脚本与命令
└── README.md
```

## 添加新 Skill

在本仓库根目录下新建 skill 文件夹，按照 `osinos-debugging` 的结构编写 `SKILL.md` 及相关文档即可。
