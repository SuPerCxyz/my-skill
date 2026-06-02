# EasyStack OSINOS 环境调试

在 EasyStack OSINOS 环境中排查和修复 OpenStack 服务问题。

## 功能

通过 SSH 跳板机访问 K8s 环境，对运行在 Kubernetes 上的 OpenStack 服务进行调试，包括：

- SSH 访问链建立与本地 OpenStack 客户端配置
- 服务状态检查、Pod 诊断、日志分析
- ConfigMap 编辑与 Pod 重启
- `sleep 10d` 模式手动调试代码
- Nova 维护操作（cell、evacuation）
- fluentd 历史日志搜索
- 常见故障场景排查

## 固定访问路径

```bash
# 跳板机 → K8s 控制节点 10.20.0.3
sshpass -p "easystack" ssh -F /dev/null -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=8 root@<JUMP_IP> 'ssh -F /dev/null -i /root/.ssh/id_rsa.roller -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@10.20.0.3' "<kubectl-command>"
```

## 文件说明

| 文件 | 内容 |
|------|------|
| [SKILL.md](SKILL.md) | Skill 主入口，快速参考 |
| [access.md](access.md) | SSH 访问链、本地 OpenStack 客户端配置 |
| [auth.md](auth.md) | 认证与鉴权排查 |
| [code-debug.md](code-debug.md) | 代码级调试指南（/opt mount） |
| [logs.md](logs.md) | kubectl 日志查看、fluentd 历史搜索 |
| [nova-maintenance.md](nova-maintenance.md) | Nova 维护操作（cell、evacuation） |
| [pods.md](pods.md) | K8s Pod 诊断技巧 |
| [reference.md](reference.md) | 常用命令、环境常量速查 |
| [scenarios.md](scenarios.md) | 常见故障场景排查 |
| [scripts.md](scripts.md) | ConfigMap 结构、sleep 10d 调试模式、脚本编辑 |
