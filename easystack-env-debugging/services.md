# Services Discovery

将服务名映射到 pod 前缀、端口、namespace 或仓库位置时阅读本文件。具体日志命令参考
[logs.md](logs.md); 认证方式参考 [auth.md](auth.md)。

## Component Catalog 组件目录

更完整的组件部署详情按项目拆分到以下目录。新增组件时优先在对应目录添加
`<component>.md`, 本文件只保留跨项目路由和必须注意的 namespace/Helm 安全边界。

| 项目 | 组件详情 |
|------|----------|
| OpenStack | [openstack/index.md](openstack/index.md) |
| Ceph | [ceph/index.md](ceph/index.md) |
| Kubernetes | [k8s/index.md](k8s/index.md) |

## OpenStack Service Map 服务映射

OpenStack 服务、Pod 前缀、端口、OVN 组件、扩展服务和基础组件速查统一维护在
[openstack/service-map.md](openstack/service-map.md)。

OpenStack 组件仓库布局统一维护在
[openstack/project-code-layout.md](openstack/project-code-layout.md)。

## Ironic Namespace 命名空间

Ironic services run in the independent `ironic` namespace. Do not assume they are
in `openstack`. The exception is `nova-compute-ironic`, which belongs to the
Nova side and may appear under the OpenStack deployment layout.

```bash
kubectl get pods -n ironic
kubectl get pods -n ironic --show-labels
kubectl get pods -n openstack -l service=nova-compute-ironic
```

## Helm Releases 发布记录

大多数 OpenStack control-plane release 通过 Helm 部署在 `openstack` namespace。
像 `ironic` 这类服务专用 namespace 需要单独检查:

```bash
helm list -n openstack
helm history -n openstack <release-name>
```

`helm get values -n openstack <release-name>` is read-only, but some environments
return `Unauthorized operation`. Treat it as optional and do not block the
inspection flow if it fails.

`helm rollback` changes the environment. Do not run it unless the user explicitly
authorizes that exact rollback.
