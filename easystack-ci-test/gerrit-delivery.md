# Gerrit Delivery

Use this file only after the requested CI checks pass and the user explicitly asks to upload the
current fix to Gerrit. Uploading is a remote write operation and is never implied by running tests.

## Preconditions 前置条件

1. `tox -e cover` 和 `tox -e pep8` 已通过。
2. 当前 `HEAD` 就是需要更新的 Gerrit change, commit message 中存在原 `Change-Id`。
3. 用户已确认本次需要 amend 并执行 `git review`。
4. 用户已提供 `git review -r <remote>` 的 remote, 或仓库配置可以无歧义确定 remote。
5. 工作区不存在与本次任务无关且会被误提交的修改。

任一条件不满足时停止, 不创建新 commit, 不猜测 remote。

## Amend Current Change 更新当前 change

先记录原 Gerrit `Change-Id`, 只暂存本次任务文件:

```bash
change_id_before=$(git show -s --format=%B HEAD | sed -n 's/^Change-Id: //p')
test -n "$change_id_before"
git status --short
git add -- <task-files>
git diff --cached --check
git commit --amend --no-edit
change_id_after=$(git show -s --format=%B HEAD | sed -n 's/^Change-Id: //p')
test "$change_id_after" = "$change_id_before"
```

`git commit --amend` 会生成新的 Git commit SHA, 这是 Git 的正常行为。必须保留原
`Change-Id`, Gerrit 才会把上传内容作为同一个 change 的新 patch set。禁止使用普通
`git commit` 创建新的 Gerrit change。

如果 amend 后 `Change-Id` 丢失或变化, 不要上传; 先恢复正确提交信息并重新验证。

## Upload 上传

使用用户确认的 Gerrit remote:

```bash
git review -r <remote>
```

`-r` 参数表示 remote 名称, 不是 Gerrit review ID。上传完成后报告 Gerrit 返回的
change URL 或错误信息; 不把新的 Git SHA 误称为新的 Gerrit Change-Id。
