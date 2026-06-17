# 页面导航

## 适用范围

本文件定义 EasyStack Cloud Web E2E中的导航入口、菜单结构、页面路径基线
和导航验证方式。

所有示例统一面向 `agent-browser` CLI；不使用其他浏览器自动化模板。

## 导航语义

- 已知目标路径时，优先直接用标准启动参数打开目标 URL：
  `agent-browser --args '--no-sandbox' --ignore-https-errors open <url>`
- 不确定目标入口时，先通过“产品与服务”菜单定位
- 页面路径默认以“当前主路径”为执行入口
- 历史/别名路径只作为旧文档和历史实现的对照信息

## 顶部导航元素

| 元素 | 定位方式 | 说明 |
|------|--------|------|
| 概览 | `a.action-overview` | 跳转到 `/overview` |
| 产品与服务 | `a.action-products-menu` | 打开服务目录 |
| 语言切换 | `a.action-language` | 切换中英文 |
| 用户菜单 | `a.action-user` | 用户会话操作 |

## 服务目录导航

当前文档只保留与默认执行入口相关的菜单信息：

- Computing
  - Instance -> `/eec/instances`
  - Instance Snapshot -> `/eec/instance-snapshots`
  - SSH Key Pair -> `/eec/keypairs`
- Block Storage
  - Volume -> `/ebs/volumes`
  - Volume Snapshot -> `/ebs/volume-snapshots`
  - Volume Type -> `/ebs/volume-types`
- Network
  - Network -> 当前主路径 `/ens/networks`
  - Router -> 当前主路径 `/ens/routers`
  - vNIC -> 当前主路径 `/ens/nics`
  - Floating IP -> 见路径基线表
- Image Repository
  - Image -> 当前主路径 `/container-registry/image`

## 当前主路径与历史/别名路径

| 页面 | 当前主路径 | 历史/别名路径 | 说明 |
|------|------------|---------------|------|
| 概览 | `/overview` | 无 | 当前资料一致 |
| 云主机 | `/eec/instances` | 无 | 当前资料一致 |
| 云主机创建 | `/eec/instances/create-instance` | 无 | 当前资料一致 |
| 云硬盘 | `/ebs/volumes` | 无 | 当前资料一致 |
| 云硬盘快照 | `/ebs/volume-snapshots` | 无 | 当前资料一致 |
| 云硬盘类型 | `/ebs/volume-types` | 无 | 当前资料一致 |
| 镜像管理 | `/container-registry/image` | `/glance/images` | 默认执行入口使用当前主路径 |
| 网络管理 | `/ens/networks` | `/neutron/networks` | 默认执行入口使用当前主路径 |
| 路由器 | `/ens/routers` | `/neutron/routers` | 默认执行入口使用当前主路径 |
| 虚拟网卡 | `/ens/nics` | 无 | 当前资料一致 |
| 浮动 IP | `/ens/floatingIPs` | `/eec/floating-ips`、`/neutron/floatingips` | 当前 UI 从 Service Catalog -> Network -> Floating IP 进入该路径 |

## 导航验证

- 到达目标页后优先检查 URL 是否命中目标路径
- 再检查主区域是否可见，如 `main`、`.ant-table`
- 固定等待只作兜底，不作主成功信号

## 标准示例

```bash
agent-browser --args '--no-sandbox' --ignore-https-errors open "$TARGET_URL"
agent-browser wait 'main, .ant-table'
agent-browser get url
```

## 菜单入口示例

```bash
agent-browser click 'a.action-products-menu'
agent-browser find text "$ITEM_TEXT" click
agent-browser wait 'main, .ant-table'
agent-browser get url
```
