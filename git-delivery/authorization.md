# Authorization Boundary 用户授权边界

必须区分不同请求所代表的授权范围, 不得越权执行。

## 仅生成提交信息

用户要求"生成提交信息"、"整理 commit message"时, 只允许检查 diff、分析逻辑范围、
生成提交信息。不代表授权 `git add`、`git commit`、`git commit --amend`、
`git review` 或 `git push`。

## 提交当前修改

用户明确要求"提交代码"、"帮我 commit"、"提交当前修改"时, 可以视为授权检查并
暂存本次任务文件、执行普通 `git commit`, 以及在明确属于当前未合并 Gerrit
Change 时执行必要的 `git commit --amend`。但不自动授权 `git review`、
`git push`、rebase、merge、cherry-pick 或 force push。

## 提交到 Gerrit

用户明确要求"提交到 Gerrit"、"执行 git review"、"更新原评审"、"上传新的
Patch Set"时, 可以视为授权检查并暂存相关文件、执行必要的 commit 或 amend、
执行 `git review -r origin <branch>`。不自动授权 interactive rebase、squash、
重排提交、merge、cherry-pick、force push、abandon 或删除远程 Change。

## Push

只有用户明确要求 push 时, 才能执行普通 push。不得把"commit"或"提交代码"自动
解释为 push。

## 历史改写

以下操作必须获得用户明确授权: `git rebase`、interactive rebase、squash、重排
提交、cherry-pick、force push、修改非 HEAD 提交、合并多个 Gerrit Change、拆分
已有 Gerrit Change。
