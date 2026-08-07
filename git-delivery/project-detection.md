# Project Type Detection

必须先判断当前仓库属于 `company-gerrit` 还是 `personal-git`, 再决定交付模式。

## 识别优先级

1. 用户当前会话中的明确说明
2. 项目级规则、贡献文档和仓库开发文档
3. 近期 commit message 中的 `EAS-<number>` (大小写不敏感)
4. Git remote 地址和历史交付方式
5. 当前及历史提交中的 Gerrit `Change-Id`
6. 当前项目路径及其上级目录中的公司 `ES` 标识

用户明确说明优先于所有自动推断。仓库自身明确规则优先于路径和提交历史推断。

## EAS 任务编号 - 最强自动信号

用 grep 过滤近期 commit message 即可, 不需要读取完整提交:

```bash
git log -n 20 --format='%s %b' | grep -iE 'EAS-[0-9]+'
```

命中即为公司项目。不得把源代码变量、文件正文、普通英文单词、不包含任务编号的
`eas`、测试数据中的随机字符串作为依据。生成公司提交信息时, 遵循仓库现有格式,
通常使用大写 `EAS`。

## ES 路径标识 - 辅助信号

路径中的 `ES` 只能作为辅助信号, 不能机械搜索任意目录名中的连续字母。以下普通
英文目录不得仅因含有 `es` 就判断为公司项目:

```text
tests  services  resources  examples  styles  pages
```

应优先识别明显独立的目录标识、目录前缀或工作区分类名称, 并结合 `EAS-<number>`
提交信息、公司 remote、Gerrit `Change-Id` 等信号综合判断。即使仓库存在
`.gitreview`, 也不能仅凭该文件判断项目类型。

## 公司项目辅助信号

- 当前或近期提交包含 Gerrit `Change-Id`
- 历史提交使用 OpenStack / Gerrit 格式
- remote 指向公司内部 Gerrit 或代码托管服务
- 仓库文档要求使用 Gerrit 或 `git review`
- 历史提交常使用 Bug、Task、Depends-On 等 footer

## 个人项目识别信号

- 用户明确说明是个人项目
- 仓库规则要求普通 Git、Pull Request 或 Merge Request 工作流
- commit message 中没有 `EAS-<number>`
- 提交历史不使用 Gerrit `Change-Id`
- remote 指向个人 GitHub、GitLab、Gitea 或类似仓库

## 冲突处理

信号冲突时按以下顺序处理:

1. 用户明确说明
2. 仓库自身规则
3. commit message 中的 `EAS-<number>`
4. 公司 remote 和历史 Gerrit 工作流
5. Gerrit `Change-Id`
6. 路径中的独立 `ES` 标识

近期 commit 包含 `EAS` 但仓库规则明确要求普通 Git 工作流时, 简短报告冲突并
请求用户确认。路径中出现 `ES` 但没有 EAS、Gerrit、公司 remote 或仓库规则等
其他信号时, 不得仅凭路径执行 `git review`。

无法可靠识别时: 可以检查工作区、分析 diff、生成候选提交信息, 但不得自行执行
commit、amend、`git review` 或 push。简短请求用户确认:

```text
当前仓库无法可靠判断提交模式, 请确认使用公司 Gerrit 模式还是个人 Git 模式。
```
