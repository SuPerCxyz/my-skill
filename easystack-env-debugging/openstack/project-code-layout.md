# OpenStack Project Code Layout

本文件从 `services.md` 迁出组件和代码仓库的对应关系。它描述仓库布局, 不表示节点上存在源码。

每个组件通常有 3 到 4 个仓库:

| Repository | 用途 | Pod 名称模式 |
|------------|---------|-----------------|
| `<service>` (如 `nova`) | 核心服务代码 | `<service>-*` |
| `ark-<service>` (如 `ark-nova`) | 管理配置和启动脚本 | 同一批 pod, 脚本位于 `/tmp/` |
| `<service>-dashboard` | 前端 UI | `<service>-dashboard-*` |
| `<service>-dashboard-api` | 前端后端 API | `<service>-dashboard-api-*` |

**Cinder 例外:** dashboard API 是 `golem`, pod 是 `cinder-golem-*`:

| Component | Backend | 配置/脚本 | 前端 UI | 前端 API |
|-----------|---------|---------------|-------------|-------------|
| Nova | `nova` | `ark-nova` | `nova-dashboard` | `nova-dashboard-api` |
| Cinder | `cinder` | `ark-cinder` | `cinder-dashboard` | `golem` |
| Glance | `glance` | `ark-glance` | `glance-dashboard` | `glance-dashboard-api` |

这些是仓库名。默认情况下节点上**没有**源码, pod 中运行的是已打包服务代码。
