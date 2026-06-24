---
name: media-library-organizer
description: "Use when the user wants to organize a media library: TMDB scraping, renaming, NFO generation, and artwork download for movies/TV/variety/documentary/anime. Enforces dry-run by default, rollback support, and conflict handling."
---

# Media Library Organizer

媒体库整理

## Core Principles 核心原则

```
自动扫描 + 自动匹配 + 自动预览
但不自动执行

高置信度自动填充
低置信度必须让用户选

能从 TMDB API 拿就从 API 拿
不能拿再 fallback 网页抓取

能用 ffprobe 就不用猜
猜出来的字段必须标记 guessed

移动文件前先建映射
移动文件后必须能回滚

重命名、NFO、图片下载可以自动化
但真实文件修改必须经过明确确认
```

## Key Safety Rules 关键安全规则

1. **默认永远 dry-run**，不允许直接修改文件。
2. 只有用户明确回复「确认执行 / 执行 / apply / run」后，才允许执行真实重命名。
3. 目标文件已存在时默认跳过，禁止覆盖。
4. TMDB 匹配置信度不足时，必须列出候选项让用户选择。
5. 所有文件移动前必须生成 `_rename_mapping.json`。
6. 所有真实操作完成后必须生成 `_rollback.sh`，并支持 dry-run 回滚。
7. Kodi / Jellyfin / Emby 剧集识别依赖文件名中的 `SxxExx`，因此即使生成 NFO，文件名也必须保留标准季集号。
8. 电影 NFO 默认生成与视频同名的 `.nfo`，可选额外生成 `movie.nfo`。
9. 剧集核心 NFO 为 `tvshow.nfo` + 每集同名 `.nfo`;`season.nfo` 可选生成。
10. 图片下载失败不能阻断重命名，但必须记录失败清单。
11. ffprobe 检测结果优先于文件名猜测。
12. 任何 guessed 字段必须在预览中标记。
13. 删除空目录前必须确认目录内没有非本次处理文件。
14. 回滚脚本不能删除用户在执行后新增的文件。

---

## Input 输入

用户提供一个**文件夹路径**，可以是:

- **单个资源文件夹**:如 `综艺/五十公里桃花坞/` 或 `电影/阿凡达/`
- **多个资源的父文件夹**:如 `综艺/` 或 `电视剧/` 或 `下载/待整理/`

Skill 会自动扫描并逐个处理。

---

## Configuration Parameters 配置参数

```yaml
options:
  dry_run: true                    # 默认永远 dry-run
  language: zh-CN                  # TMDB 语言
  country: CN                      # 国家
  tmdb_id: null                    # 显式 TMDB ID(可选)
  tmdb_api_key: null               # TMDB API Key(优先读环境变量 TMDB_API_KEY)
  media_type: auto                 # auto / movie / tv / variety / documentary / anime
  season_mode: auto                # auto / single / multi
  special_mode: season00           # season00 / inline / skip
  overwrite: false                 # 禁止覆盖
  conflict_policy: skip            # skip / suffix / replace(默认 skip)
  generate_nfo: true               # 生成 NFO
  download_artwork: true           # 下载图片
  artwork_quality: original        # original / w500 / w300
  artwork_alias: true              # 是否生成图片别名(hardlink)
  max_workers: 4                   # 最大并发数
  delete_empty_dirs: true          # 删除空目录
  prefer_ffprobe: true             # ffprobe 优先
  nfo_format: kodi                 # kodi / jellyfin / emby
  jellyfin_compatible: true
  emby_compatible: true
  tmm_compatible: true
  generate_season_nfo: false       # season.nfo 可选生成
  generate_movie_nfo_duplicate: false  # 是否额外生成 movie.nfo
  execution_mode: direct           # direct / staging
  full_hash: false                 # 是否计算完整 sha256(大文件默认 quick_hash)
  media_root: null                 # 媒体库根目录，目标路径必须在此目录内
  target_root: null                # 可选目标整理目录，不填则使用 media_root
  staging_root: null               # 可选 staging 根目录，不填则在 target_root 下创建
```

---

## Media Root Rules 媒体库根目录规则

- 如果 `media_root` 未设置，则默认使用用户输入路径的父目录作为安全边界
- `target_root` 必须位于 `media_root` 内
- `staging_root` 必须位于 `media_root` 或 `target_root` 内
- 所有 `old_path` / `new_path` / `staging_path` 都必须经过 `realpath` 校验
- 禁止 `new_path` 跳出 `media_root`

---

## Execution Gate 执行门禁

```
默认永远 dry-run，不允许直接修改文件。

只有用户明确回复以下任一内容，才允许执行真实文件修改:
- 确认执行
- 执行
- apply
- run

以下回复不允许执行:
- 看起来可以
- 差不多
- 继续看看
- 还有吗
- 应该可以
- 嗯
- 好
```

---

## Dry-Run Behavior Rules Dry-Run 行为规则

dry-run 模式下允许的操作:
- 扫描文件
- 执行 ffprobe
- 查询 TMDB API
- 生成预览
- 输出「将生成的 mapping / rollback 预览」

dry-run 模式下禁止的操作:
- 创建目录
- 移动 / 重命名文件
- 写入 NFO
- 下载图片
- 删除空目录
- 生成真实 rollback 脚本

---

## File Type Recognition 文件类型识别

### Video File Extensions 视频文件扩展名

```
.mp4 .mkv .avi .mov .wmv .flv .ts .m2ts .mts .webm .rmvb .mpg .mpeg .iso
```

只有视频文件参与 movie / episode 判断。

### Subtitle File Extensions 字幕文件扩展名

```
.srt .ass .ssa .sub .idx .sup .vtt
```

字幕文件必须绑定主视频，不单独作为资源。跟随主视频重命名，保留语言后缀。

### Image / NFO / Accessory Extensions 图片 / NFO / 附属文件扩展名

```
.nfo .jpg .jpeg .png .webp .txt .url
```

NFO / 图片 / txt / url 默认作为附属文件处理，不参与媒体类型判断。

### Unrecognized Extensions 未识别扩展名

默认保留，不删除、不移动，除非用户明确要求。

---

## Sub-file Index 子文件索引

| 文件 | 内容 | 何时查阅 |
|------|------|---------|
| `workflow.md` | 步骤 1~9 完整工作流程 | 执行时按步骤查阅 |
| `naming-rules.md` | 电影/剧集/特殊内容命名规则 + 字段说明 | 生成文件名时查阅 |
| `nfo-templates.md` | movie / tvshow / episodedetails / season NFO 模板 | 生成 NFO 时查阅 |
| `artwork.md` | 图片下载列表、别名策略、图片来源 | 下载图片时查阅 |
| `tmdb-api.md` | API Key、URL、append_to_response、置信度评分、图片拼接 | 查询 TMDB 时查阅 |
| `technical-reference.md` | parse_filename、ffprobe 检测代码、技术信息优先级 | 写脚本时查阅 |
| `safety.md` | 回滚要求、mapping 格式、校验策略、冲突处理、路径安全 | 回滚和冲突处理时查阅 |
