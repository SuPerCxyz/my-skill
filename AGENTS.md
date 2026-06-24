# Skill 生成规范

本文件规范 `my-skills` 仓库中 skill 的目录结构、文件格式与写作风格。新增或修改 skill 前必读。

## 目录结构

```
<skill-name>/
- SKILL.md      (必需)  skill 主入口, 含 YAML frontmatter
- README.md     (推荐)  该 skill 的用途、文件说明与快速开始
- *.md          (按需)  参考文档按需放在同目录或子目录
```

`docs/` 目录用于存放工作流产生的 plan / spec 设计文档存档, **不是 skill**, 不要在其中创建 SKILL.md。

## SKILL.md 规范

### Frontmatter

每个 SKILL.md 必须以 YAML frontmatter 开头:

```yaml
---
name: <skill-name>
description: "Use when ..."
---
```

- `name`: 与目录名一致, 全小写连字符
- `description`: **必须用双引号包裹**, 避免含逗号 / 冒号的长字符串解析问题
- description 以 "Use when ..." 句式描述触发场景; 纯流程加载型 skill (由 AGENTS.md 显式加载) 可用动词起句
- description 长度建议 <= 350 字符; 删除实现细节保留触发场景与核心能力, 避免稀释 skill 匹配信号

### 标题

| 层级 | 规则 | 示例 |
|------|------|------|
| H1 | 纯英文专名, 不加 "Skill"/"Guide" 后缀, 不加中文 | `# EasyStack CI Test` |
| H2/H3 | 中英文双语: 英文在前 + 空格 + 中文 | `## Quick Reference 快速参考` |

Step 子标题 (H3) 保持 "Step N: " 前缀, 中英文随正文语言。

### 正文

- 正文以中文为主, 关键技术名词保留英文 (如 tox, nova, cinder, UUID, dry-run)
- 中英文之间保持半角空格分隔 (如 "运行 tox 命令")
- 保持段落简洁, 避免大段说明; 细节拆到子文件, SKILL.md 只做入口与索引

### 标点

- **禁止全角标点**; 全部使用半角 ASCII: `()` `:` `;` `,` `.`
- 禁止全角括号 `()`, 全角冒号 `:`, 全角分号 `;` 等 "模棱两可" Unicode 字符 (git 服务端会提示)
- 中文顿号 `、` 和句号 `。` 在纯并列中文场景可保留, 但避免混入英文上下文

### 文件索引

SKILL.md 必须包含一个文件索引表, 让 agent 知道何时查哪个文件:

```markdown
## Quick Reference 快速参考

| 需要做什么 | 阅读 |
|------------|------|
| 解压 eslog 文件 | [decompress.md](decompress.md) |
| 日志目录结构映射 | [directory-map.md](directory-map.md) |
```

- 索引表覆盖该 skill 目录下全部参考文档, 不留孤儿文件
- 多层索引可分文件组织, 但顶层 SKILL.md 必须能一站直达每个子文件

## README.md 规范

每个 skill 推荐有 README.md, 内容至少包含:
1. 一句话用途说明
2. 功能列表
3. 文件说明表 (引用 SKILL.md 同样的索引)
4. 快速开始 (最小可执行步骤)

## 添加新 Skill 检查清单

1. 在仓库根目录新建 `<skill-name>/` 目录
2. 编写 `SKILL.md` (含 frontmatter + 文件索引表)
3. 编写 `README.md` (用途 + 文件说明 + 快速开始)
4. 在根 `README.md` 的 Skills 列表中按字母序登记一行
5. 运行全角标点检查:
   ```bash
   rg -P '[\x{FF00}-\x{FFEF}]' */SKILL.md */README.md
   ```
   全角括号 / 冒号 / 分号必须为 0
6. 验证全部内部链接无 broken
7. 验证 frontmatter description 有双引号包裹

## 根 README.md 维护

- Skills 列表按字母排序
- 描述与 SKILL.md description 口径一致, 不夸大不存在的功能
- git clone URL 与实际 remote 一致 (当前: `ssh://git@git.soocoo.xyz:10022/superc/my-skills.git`)
- `docs/` 等非 skill 目录需在列表后说明用途