## Why

固定 hub/agent 和 Rocky/Fedora 模板会把一个项目的偶然架构误当成所有测试项目的默认配置, 造成不必要的 VM 创建和错误的 guest 选择. 同时, 仅描述流程而缺少可复制命令会让执行模型自行猜测 libvirt 和 guest 操作, 增加失败、重试和 token 消耗.

## What Changes

- 移除环境示例中的固定 hub/agent 模板映射.
- 先读取项目架构、部署配置和测试依赖, 生成项目专属 VM plan, 只创建架构实际需要的 VM.
- 将 hub、agent 视为可选项目角色, 不再作为默认角色或默认操作系统.
- 在现有 discovery、clone/resize、verification reference 中补充带占位符、前置检查和失败处理的具体命令.
- 明确只读命令、变更命令、关机要求、运行态磁盘查询和 guest 内扩容命令的使用边界.
- 保持现有 skill 文件集合, 不新增或删除 skill 文件.

## Capabilities

### New Capabilities

无.

### Modified Capabilities

- `kvm-test-vm-operations`: 从固定 hub/agent 流程改为项目架构驱动的 VM 规划和命令模板驱动的执行流程.

## Impact

- 修改现有 `kvm-test-vm-ops/SKILL.md`、README、environment example 和 references.
- 更新现有 OpenSpec capability requirement.
- 不新增运行时依赖, 不修改当前 KVM VM、模板、网络或节点.
- 现有项目根目录的本地环境和 VM inventory 格式继续使用, 但角色字段改为项目自定义值.
