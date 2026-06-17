# easystack-ui-test 基础层与路径口径收敛设计

## 背景

上一轮已经完成 `patterns/login.md`、`patterns/instance-ops.md`、
`patterns/quick-reference.md` 的核心收敛，但基础约定层与全目录路径
口径仍存在上游冲突，继续影响后续文档的可信度与可执行性。

当前主要问题包括：

- `connection.md`、`navigation.md` 仍保留 Python Playwright 模板，与
  当前 MCP Playwright / `browser_run_code_unsafe` 语义冲突
- `connection.md`、`SKILL.md`、`patterns/login.md` 对环境配置来源和
  登录契约存在重复与不一致
- 全目录同时出现 `/ens/*`、`/neutron/*`、`/glance/*`、
  `/container-registry/*` 等路径体系，但多数文档没有解释其关系
- 部分基础层文档仍包含真实 URL、用户名、密码示例
- 资源页文档中存在与基础层直接冲突的路径表述，容易误导执行入口

这些问题的共同特征是：它们位于“规则层”或“入口层”，属于上游约定
冲突。如果不先收敛，会持续污染后续操作库迁移和知识文档治理。

## 本轮目标

本轮做“基础层 + 全目录路径同步”的分层收敛。

核心目标：

- 建立基础权威层的统一规则
- 用双轨模型统一页面路径表述
- 对会直接误导执行的全目录冲突片段做同步修正
- 同步完成基础层去敏感化

## 范围

### 权威层文件

以下文件属于本轮权威层，要求完成系统性收敛：

- `easystack-ui-test/connection.md`
- `easystack-ui-test/navigation.md`
- `easystack-ui-test/SKILL.md`

### 直接冲突同步层

以下文件不做整篇重构，但会修正会直接误导执行的冲突片段：

- `easystack-ui-test/patterns/platform-info.md`
- `easystack-ui-test/relationships.md`
- `easystack-ui-test/network/network.md`
- `easystack-ui-test/network/router.md`
- `easystack-ui-test/network/vnic.md`
- `easystack-ui-test/image/image.md`

### 本轮不做

- 不迁移 `patterns/volume-ops.md`、`patterns/network-ops.md`
- 不治理 `instance/*.md`、`volume/*.md`、`network/*.md`、
  `image/image.md` 的大文件拆分问题
- 不做全目录彻底去敏感化，只处理本轮涉及文件
- 不做真实 UI 回放验证

## 设计原则

### 1. 权威层优先

所有下游路径和登录口径以基础权威层为准。若下游文档与权威层冲突，
本轮优先修正下游表述，而不是放任多套结论并存。

### 2. 双轨路径模型

路径统一采用以下结构：

- 当前主路径
- 历史/别名路径
- 必要时的差异说明

这意味着本轮不强行删除历史路径信息，但必须明确其地位：

- 当前主路径：默认执行入口
- 历史/别名路径：对照信息，不作为默认执行入口

### 3. 去敏感化与结构收敛同时进行

基础层文档不能一边统一契约，一边继续保留真实环境样例。
因此去敏感化不是额外优化，而是本轮验收条件的一部分。

### 4. 只修直接冲突

对同步层文件，本轮只修正会误导执行的冲突内容，不顺手扩展为大规模
知识库整理。

## 路径模型

### 统一表达格式

本轮路径说明统一采用以下格式：

```text
页面：网络管理
当前主路径：/ens/networks
历史/别名路径：/neutron/networks
说明：执行示例默认使用当前主路径；历史路径只作为旧文档对照信息
```

若某路径当前无法确认唯一主路径，则允许使用：

- 当前主路径：待确认
- 历史/别名路径：列出已发现路径
- 说明：需运行时验证或版本对照后确认

但在本轮目标文件里，应尽量减少“待确认”状态，仅在确无证据时使用。

### 当前主路径判定策略

本轮优先依据以下证据判定主路径：

1. 已完成收敛的 `patterns` 核心文档中实际使用的路径
2. `patterns/platform-info.md`、`network/*.md`、
   `image/image.md` 中相互一致的路径
3. 更贴近当前产品结构的路径分组，例如：
   - 网络类优先考虑 `/ens/*`
   - 镜像类优先考虑 `/container-registry/image`

当 `navigation.md` 的旧路径表与当前资源文档冲突时，不再默认保留
`navigation.md` 为真，而是将其改为双轨说明。

## 文件设计

## `connection.md`

### 目标职责

仅负责以下内容：

- 环境配置来源
- 登录契约
- 会话复用
- 等待与页面验证原则

### 本轮改动

- 全部改为 MCP Playwright / JavaScript 语义
- 去掉 Python Playwright 模板
- 去掉真实 URL、用户名、密码
- 统一引用 `/tmp/easystack-env.json` 的：
  - `platform.url`
  - `platform.username`
  - `platform.password`
- 登录契约与 `patterns/login.md` 保持一致，但不重复堆叠执行细节

### 结果定位

`connection.md` 应成为“基础层登录与连接规则说明”，而不是“旧版脚本片段
仓库”。

## `navigation.md`

### 目标职责

仅负责以下内容：

- 导航入口
- 菜单结构
- 页面路径映射
- 导航验证方式

### 本轮改动

- 全部改为 MCP Playwright / JavaScript 语义
- 建立“当前主路径 + 历史/别名路径”表
- 不再把 `/neutron/*`、`/glance/*` 直接写成未解释的唯一事实
- 为默认执行入口给出明确路径

### 结果定位

`navigation.md` 应成为“权威导航基线”，供 `SKILL.md` 和下游文档引用。

## `SKILL.md`

### 目标职责

顶层索引、执行规则、文件分流入口。

### 本轮改动

- 去掉与 `connection.md` / `navigation.md` 冲突的重复约定
- 将环境配置、登录、路径口径统一引用到基础权威层
- 同步去敏感化
- 对顶层路径表述采用统一双轨模型

### 结果定位

`SKILL.md` 只保留必要的顶层执行信息，避免再成为第二套基础规则来源。

## 直接冲突同步层设计

### `patterns/platform-info.md`

- 对基础页面路径做主路径 / 别名路径收敛
- 作为基础层与下游资源页之间的桥接说明

### `relationships.md`

- 修正资源页入口路径的直接冲突
- 不扩展为资源关系大重写

### `network/network.md`
### `network/router.md`
### `network/vnic.md`

- 若这些文档已采用 `/ens/*` 为主，则保留为当前主路径
- 如出现与基础层冲突的旧路径，补成别名说明

### `image/image.md`

- 以当前路径口径为主，明确 `container-registry` 与历史镜像路径的关系

## 去敏感化策略

本轮涉及文件中的真实环境样例统一替换为：

- 占位域名，如 `https://<IP>` 或 `https://example.local`
- 占位账号，如 `<USERNAME>`
- 占位密码，如 `<PASSWORD>`

若某处示例更适合直接引用环境文件，则优先写成：

```text
从 /tmp/easystack-env.json 读取 platform.url / platform.username / platform.password
```

本轮不承诺清理整个 `easystack-ui-test` 目录，但凡本轮触碰到的目标文件，
不应继续保留真实凭证。

## 验证标准

完成后必须满足：

1. `connection.md`、`navigation.md`、`SKILL.md` 在以下方面一致：
   - env 契约
   - 登录语义
   - 导航语义
   - 页面路径主口径
2. 这三个权威层文件不再包含真实 URL、用户名、密码
3. 权威层主路径说明已统一采用双轨模型
4. 同步层文件中会误导执行的路径冲突片段已与权威层对齐
5. 最终说明中显式列出本轮仍未处理的问题

## 风险与控制

### 风险 1：路径强收敛过度

不同路径可能确实对应历史版本或不同产品线，若强行删掉一侧，会损失
有价值的信息。

控制方式：

- 采用双轨模型
- 优先补充“当前主路径 / 历史别名路径 / 差异说明”
- 仅在证据明确时才做单一路径归一

### 风险 2：范围膨胀为全目录重写

路径冲突分布很广，若每看到一个冲突就整篇重写，很快会演变成大规模
知识库整理。

控制方式：

- 只修同步层中的直接冲突片段
- 不对非关键大文件做结构重组

### 风险 3：基础层与下游再次失配

若只改权威层，不同步直接冲突片段，会出现“规则层是新的，资源页还是
旧的”的短期失配。

控制方式：

- 本轮必须包含同步层修正
- 但同步层仅限直接冲突，不扩散

## 后续演进

如果本轮完成，下一轮建议继续处理：

- `patterns/volume-ops.md`、`patterns/network-ops.md` 模板迁移
- 大文件知识文档治理
- 全目录彻底去敏感化
- 真实 UI 回放验证

## 预期产出

本轮产出应是一个稳定的基础规则层：

- 基础权威层不再自相矛盾
- 路径说明改为双轨模型
- 直接冲突的下游片段不再误导执行
- 本轮涉及文件完成去敏感化
