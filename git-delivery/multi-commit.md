# Multi-Commit Stack 多提交处理

当前分支存在多个本地提交时, 先分析提交栈:

```bash
git log --oneline --decorate --graph -n 30
git log -n 30 --format=fuller
```

识别每个提交对应的 `Change-Id`、EAS 任务、提交之间的依赖关系, 以及当前修改应
属于哪个 Change。

不得把某个 Change 的文件 amend 到另一个 Change、在多个提交中错误复用同一个
`Change-Id`、把无关修改加入当前 `HEAD`、未经授权擅自 squash、重排提交或执行
interactive rebase。

如果应更新的 Change 不是当前 `HEAD`: 停止直接 amend, 说明当前提交栈关系,
指出目标 Change 所在提交, 给出安全处理方案, 获得明确授权后才能执行 rebase、
重排或其他历史改写。
