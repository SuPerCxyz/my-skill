# 常用操作索引

本文件只索引 `patterns/` 当前能力。
`ready-validated` 表示已通过真实 EasyStack Web UI 用例验证；
`ready-template` 表示已按 `patterns/operation-template.md` 补齐统一模板但尚未
完成真实用例闭环验证；
`planned` 仅保留待迁移名称清单，不作为当前可执行入口。

## 使用流程

1. 先读 `patterns/login.md`
2. 再读对应资源域文档
3. 优先使用 `ready-validated`；`ready-template` 可作为模板执行但必须现场确认；
   `planned` 只代表后续迁移目标

## 能力索引

| 操作名 | 资源域 | 文档位置 | 必填参数 | 默认参数来源 | 返回结果 | 当前状态 |
|---|---|---|---|---|---|---|
| `create_instance` | `instance` | `patterns/instance-ops/create-instance.md` | `name` | `resources.image_name`、`resources.flavor`、`resources.network_name`、`resources.subnet_name`、`ssh.key_name`、`vm_defaults.password` | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-validated` |
| `delete_instance` | `instance` | `patterns/instance-ops/delete-instance.md` | `name` | 无 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `attach_volume` | `instance` | `patterns/instance-ops/attach-volume.md` | `instance`、`volume` | 无 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-validated` |
| `rename_instance` | `instance` | `patterns/instance-ops/rename-instance.md` | `instance`、`new_name` | 无 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `start_stop_reboot_instance` | `instance` | `patterns/instance-ops/start-stop-reboot.md` | `name`、`action` | `target_status` 可由动作推导 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `create_instance_snapshot` | `instance` | `patterns/instance-ops/create-snapshot.md` | `instance`、`snapshot_name` | 无 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `create_volume` | `volume` | `patterns/volume-ops.md` | `name`、`size` | `resources.volume_type`、`screenshot_dir` | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-validated` |
| `detach_volume` | `volume` | `patterns/volume-ops.md` | `volume` | `instance`、`device` 可选 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-validated` |
| `delete_volume` | `volume` | `patterns/volume-ops.md` | `name` | 无 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-validated` |
| `upload_image` | `volume` | `patterns/volume-ops.md` | `name`、`source_url` | `resources.image_os_category` | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `create_volume_snapshot` | `volume` | `patterns/volume-ops.md` | `volume`、`snapshot_name` | `forced=false` | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `rollback_volume_snapshot` | `volume` | `patterns/volume-ops.md` | `snapshot_name` | `volume` 可选 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-validated` |
| `delete_volume_snapshot` | `volume` | `patterns/volume-ops.md` | `snapshot_name` | 无 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-validated` |
| `create_volume_from_snapshot` | `volume` | `patterns/volume-ops.md` | `snapshot_name`、`volume_name` | `copy_full_data=false`、快照继承 `size/type` | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `allocate_floating_ip` | `network` | `patterns/network-ops.md` | 无 | `resources.project_name`、`resources.external_network` | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-validated` |
| `associate_floating_ip` | `network` | `patterns/network-ops.md` | `instance`、`private_ip` | `floating_ip` 可选 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-validated` |
| `disassociate_floating_ip` | `network` | `patterns/network-ops.md` | `floating_ip` | `instance` 可选 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `release_floating_ip` | `network` | `patterns/network-ops.md` | `floating_ip` | 无 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `create_network` | `network` | `patterns/network-ops.md` | `name` | 显式可选参数 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `create_router` | `network` | `patterns/network-ops.md` | `name` | 显式可选参数 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `probe_resource_list_pages` | `page` | `patterns/page-probes.md` | 无 | `platform.url` | 结构化对象 `{ok,resource,action,pages}` | `ready-template` |
| `probe_create_instance_page` | `page` | `patterns/page-probes.md` | 无 | `platform.url` | 结构化对象 `{ok,resource,action,fields}` | `ready-template` |
| `probe_create_volume_modal` | `page` | `patterns/page-probes.md` | 无 | `platform.url` | 结构化对象 `{ok,resource,action,labels,defaults}` | `ready-template` |
| `cleanup_resources_plan` | `cleanup` | `patterns/cleanup-resources.md` | `resources[]` | 报告中的 `cleanup: recommended` | 结构化对象 `{ok,action,status,resources,message}` | `ready-template` |
| `resize_instance` | `instance` | `patterns/instance-ops.md（待迁移操作）` | `instance`、`flavor` | `resources.flavor` | 待迁移 | `planned` |
| `reset_instance_password` | `instance` | `patterns/instance-ops.md（待迁移操作）` | `instance`、`password` | `vm_defaults.password` | 待迁移 | `planned` |
| `clone_instance` | `instance` | `patterns/instance-ops.md（待迁移操作）` | `instance`、`new_name` | 调用方入参 | 待迁移 | `planned` |
| `lock_instance` | `instance` | `patterns/instance-ops.md（待迁移操作）` | `instance` | 无 | 待迁移 | `planned` |
| `unlock_instance` | `instance` | `patterns/instance-ops.md（待迁移操作）` | `instance` | 无 | 待迁移 | `planned` |
| `rollback_instance_snapshot` | `instance` | `patterns/instance-ops.md（待迁移操作）` | `instance`、`snapshot_name` | 无 | 待迁移 | `planned` |
| `delete_instance_snapshot` | `instance` | `patterns/instance-ops.md（待迁移操作）` | `snapshot_name` | 无 | 待迁移 | `planned` |
| `delete_image` | `volume` | `patterns/volume-ops.md（待迁移操作）` | `image_name` | 无 | 待迁移 | `planned` |
