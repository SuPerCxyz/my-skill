# Git 精简规则

## 硬规则

1. **浅 log**
   - `git log` 必须加 `--oneline -20` 或 `-n 20`
   - 禁止 `git log` 不带数量限制
   - 需要详细 log 时用 `git log -1 --stat` 只查最近 1 条

2. **定向 diff**
   - `git diff` 必须指定文件路径或 `--stat` 先看摘要
   - 禁止 `git diff HEAD~10` 这种大范围 diff
   - 大 diff 先 `git diff --stat` 看文件列表，再逐个查

3. **禁止全量操作**
   - 禁止 `git fetch --all` — 只 fetch 需要的 remote/branch
   - 禁止 `git clone --depth=1` 以外的浅 clone 在 CI 中
   - 禁止 `git push --force` 除非用户明确要求

4. **状态检查精简**
   - `git status -s` 代替 `git status`（短格式）
   - `git branch -a | head -20` 限制分支列表
   - `git stash list | head -10` 限制 stash 列表

## 常用安全命令模板

```bash
# 查看最近提交
git log --oneline -10

# 查看当前状态（精简）
git status -s

# 查看 diff 摘要（先看哪些文件变了）
git diff --stat HEAD

# 查看指定文件的 diff
git diff HEAD -- path/to/file | head -100

# 查看某个文件的 blame（定向行范围）
git blame -L 10,30 path/to/file

# 查看最近的 tag
git tag --sort=-version:refname | head -10

# 查看远程（不 fetch）
git remote -v
```

## 禁止清单

| 禁止命令 | 替代方案 |
|----------|----------|
| `git log` (无限制) | `git log --oneline -20` |
| `git diff` (无范围) | `git diff --stat HEAD` 先，再指定文件 |
| `git fetch --all` | `git fetch origin <branch>` |
| `git branch -a` (无截断) | `git branch -a \| head -20` |
| `git log -p` (全量 patch) | `git log -1 -p -- <file>` 指定文件 |
| `git push --force` | 需用户明确确认 |
