# Media Library Organizer

媒体库整理:TMDB 刮削 + 重命名 + NFO 生成 + 图片下载，支持电影 / 电视剧 / 综艺 / 纪录片 / 动漫，含完整安全机制与回滚。

## 核心特性

- 自动扫描并逐个处理资源文件夹
- 能从 TMDB API 拿就从 API 拿，不能拿再 fallback 网页抓取
- 能用 ffprobe 就不用猜，猜出来的字段标记 `guessed`
- 默认永远 dry-run，真实文件修改需用户明确确认
- 操作前生成 `_rename_mapping.json`，操作后生成 `_rollback.sh`

## 快速开始

```
1. 提供一个文件夹路径(单个资源 或 多个资源的父目录)
2. Skill 自动扫描、匹配 TMDB、生成预览(dry-run)
3. 预览确认后回复「确认执行 / 执行 / apply / run」才执行真实重命名
```

## 文件说明

| 文件 | 内容 | 何时查阅 |
|------|------|---------|
| [SKILL.md](SKILL.md) | 核心原则、安全规则、配置参数、执行门禁 | 执行前必读 |
| [workflow.md](workflow.md) | 步骤 1~9 完整工作流程 | 执行时按步骤查阅 |
| [naming-rules.md](naming-rules.md) | 电影/剧集/特殊内容命名规则 + 字段说明 | 生成文件名时查阅 |
| [nfo-templates.md](nfo-templates.md) | movie / tvshow / episodedetails / season NFO 模板 | 生成 NFO 时查阅 |
| [artwork.md](artwork.md) | 图片下载列表、别名策略、图片来源 | 下载图片时查阅 |
| [tmdb-api.md](tmdb-api.md) | API Key、URL、append_to_response、置信度评分 | 查询 TMDB 时查阅 |
| [technical-reference.md](technical-reference.md) | parse_filename、ffprobe 检测代码、技术信息优先级 | 写脚本时查阅 |
| [safety.md](safety.md) | 回滚要求、mapping 格式、校验、冲突处理、路径安全 | 回滚与冲突处理时查阅 |