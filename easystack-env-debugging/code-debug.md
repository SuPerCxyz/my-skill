# Code Debugging via /opt Mount

This is an authorization-required workflow. Copying files to `/opt`, overlaying
runtime code, or changing startup scripts affects the environment and must not be
used during default read-only inspection.

Use this file when the user explicitly asks to modify live environment code,
debug a new feature, validate a code change in the environment, or temporarily
overlay runtime code for diagnosis.

代码调试可以是调用本 skill 的主要目标, 不需要先证明环境存在故障, 也不需要先执行
完整根因调查。只做足以确认目标服务、当前版本、运行位置和回滚基线的最小只读检查。

使用此工作流前, 必须获得用户对目标服务、目标节点、待修改文件、回滚方式和验证命令的明确授权。
进入环境仍必须先使用 [access.md](access.md) 中的统一访问脚本; `scp` 只是在用户
授权后传递文件的动作, 不能作为默认环境登录方式。

许多服务 pod 会把宿主机节点的 `/opt` 目录挂载到 pod 内的 `/opt`, 这提供了代码调试路径。

## How It Works 工作原理

宿主机 `/opt` 目录在 pod 内同样显示为 `/opt`。
宿主机 `/opt` 中包含各服务对应的子目录, 例如 `/opt/cinder/`、`/opt/nova-compute/`、
`/opt/nova-api-os-compute/`。

## Debugging Workflow 调试流程

```bash
# Step 1: Copy your debug code to the host node's /opt directory
# e.g., after entering the environment through env-access, paste it in the shell
# or use scp only when the user explicitly authorizes that transfer path
scp <your-code.py> root@<TARGET_NODE_IP>:/opt/<service>/

# Step 2: Edit the startup script so it copies code from /opt into the runtime package path first
# Example:
cp -rf /opt/<service>/* /path/to/site-packages/<service>/

# Step 3: Let the pod continue normal startup
# Keep the original launch path so logs stay visible through kubectl logs
exec /usr/bin/python3 -m <service>.main
```

## Common /opt Locations 常见 /opt 位置

| Service | 宿主机 /opt 路径 | Pod 挂载点 |
|---------|---------------|-----------|
| cinder-volume | `/opt/cinder/` | `/opt/cinder/` |
| nova-compute | `/opt/nova-compute/` | `/opt/nova-compute/` |
| nova-api-os-compute | `/opt/nova-api-os-compute/` | `/opt/nova-api-os-compute/` |

## Result Report 调试结果

纯代码调试完成后报告以下内容, 不套用问题调查报告的第 1 至第 6 节模板:

1. 授权范围: 环境、服务、节点、文件和允许的变更动作。
2. 调试基线: 修改前版本、pod、文件状态和关键行为。
3. 实际改动: 传入文件、overlay 路径、启动脚本或重启范围。
4. 验证结果: 已执行命令、预期结果、实际结果和未执行项。
5. 回滚状态: 回滚命令或备份位置, 以及当前是否已回滚。
6. 剩余风险: 临时改动、跨节点差异、pod 重建影响和后续动作。

任务同时包含故障根因判断时, 另按 [report-format.md](report-format.md) 输出问题调查
报告, 再附上述代码调试记录。
